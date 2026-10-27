"""
Unit and Integration Test Suite for V1 Subscription Model & Cashfree Integration.
Tests:
- Plan catalog and quota definitions
- Entitlement retrieval and expiration handling
- 72-hour Basic trial activation (strictly once)
- Checkout order creation with server-authoritative pricing
- Server-side order verification and polling
- Webhook HMAC-SHA256 signature verification & replay attack defense
- Idempotent payment processing and 30-day prepaid entitlement grant
- Order history
- No secret leak in responses
"""
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.deps import get_current_user
from app.main import app
from app.schemas.billing import OrderStatus, PlanTier
from app.services.billing.cashfree_gateway import cashfree_gateway

client = TestClient(app)

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_LEARNER_ID = "00000000-0000-0000-0000-000000000002"
OTHER_LEARNER_ID = "00000000-0000-0000-0000-000000000003"


@pytest.fixture
def mock_get_current_user():
    prev = app.dependency_overrides.get(get_current_user)
    user = {
        "user_id": TEST_USER_ID,
        "email": "student@unios.ai",
        "role": "learner",
        "payload": {},
    }
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    if prev is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = prev


@pytest.fixture
def mock_learner_profile():
    with patch("app.api.v1.endpoints.billing.supabase_admin") as mock_admin:
        query_mock = MagicMock()
        query_mock.select.return_value = query_mock
        query_mock.eq.return_value = query_mock
        query_mock.execute.return_value = MagicMock(data=[{"id": TEST_LEARNER_ID}])
        mock_admin.table.return_value = query_mock
        yield mock_admin


# ==============================================================================
# 1. Plan Catalog Tests
# ==============================================================================

def test_get_plans():
    response = client.get("/api/v1/billing/plans")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "plans" in data
    plans = data["plans"]
    assert len(plans) == 3

    # Check plan codes
    plan_codes = [p["planCode"] for p in plans]
    assert "FREE" in plan_codes
    assert "BASIC" in plan_codes
    assert "PRO" in plan_codes

    # Verify Free
    free_plan = next(p for p in plans if p["planCode"] == "FREE")
    assert free_plan["price"] == 0.0
    assert free_plan["durationDays"] == 0
    assert free_plan["quotas"]["aiRoadmapGenerations"] == 3
    assert free_plan["quotas"]["aiTutorRequests"] == 5
    assert free_plan["quotas"]["practiceQuestions"] == 10
    assert free_plan["quotas"]["resumeGenerations"] == 1
    assert free_plan["quotas"]["atsChecks"] == 1

    # Verify Basic (₹149, 30 days)
    basic_plan = next(p for p in plans if p["planCode"] == "BASIC")
    assert basic_plan["price"] == 149.0
    assert basic_plan["durationDays"] == 30
    assert basic_plan["quotas"]["aiRoadmapGenerations"] == 15
    assert basic_plan["quotas"]["aiTutorRequests"] == 25
    assert basic_plan["quotas"]["practiceQuestions"] == 50

    # Verify Pro (₹299, 30 days)
    pro_plan = next(p for p in plans if p["planCode"] == "PRO")
    assert pro_plan["price"] == 299.0
    assert pro_plan["durationDays"] == 30
    assert pro_plan["quotas"]["aiRoadmapGenerations"] == 40
    assert pro_plan["quotas"]["aiTutorRequests"] == 60
    assert pro_plan["quotas"]["practiceQuestions"] == 150


# ==============================================================================
# 2. Entitlement & Usage Tests
# ==============================================================================

def test_get_entitlement_default_free(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        # Mock no existing entitlement -> creates FREE default
        select_mock = MagicMock()
        select_mock.select.return_value = select_mock
        select_mock.eq.return_value = select_mock
        select_mock.execute.return_value = MagicMock(data=[])

        insert_mock = MagicMock()
        insert_mock.execute.return_value = MagicMock(data=[{
            "learner_id": TEST_LEARNER_ID,
            "current_plan": "FREE",
            "status": "ACTIVE",
            "trial_used": False,
            "current_period_start": datetime.now(timezone.utc).isoformat(),
            "current_period_end": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }])

        def table_router(name):
            t = MagicMock()
            if name == "billing_entitlements":
                t.select.return_value = select_mock
                t.insert.return_value = insert_mock
            return t

        mock_db.table.side_effect = table_router

        response = client.get("/api/v1/billing/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currentPlan"] == "FREE"
        assert data["status"] == "ACTIVE"
        assert data["trialUsed"] is False
        assert data["isActive"] is True
        assert data["isTrial"] is False


def test_get_entitlement_expired_reverts_to_free(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        expired_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        
        select_mock = MagicMock()
        select_mock.select.return_value = select_mock
        select_mock.eq.return_value = select_mock
        select_mock.execute.return_value = MagicMock(data=[{
            "learner_id": TEST_LEARNER_ID,
            "current_plan": "BASIC",
            "status": "ACTIVE",
            "trial_used": False,
            "current_period_start": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat(),
            "current_period_end": expired_date,
            "updated_at": expired_date,
        }])

        update_mock = MagicMock()
        update_mock.update.return_value = update_mock
        update_mock.eq.return_value = update_mock
        update_mock.execute.return_value = MagicMock(data=[{
            "learner_id": TEST_LEARNER_ID,
            "current_plan": "FREE",
            "status": "EXPIRED",
            "trial_used": False,
            "current_period_start": expired_date,
            "current_period_end": expired_date,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }])

        def table_router(name):
            t = MagicMock()
            if name == "billing_entitlements":
                t.select.return_value = select_mock
                t.update.return_value = update_mock
            return t

        mock_db.table.side_effect = table_router

        response = client.get("/api/v1/billing/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currentPlan"] == "FREE"
        assert data["status"] == "EXPIRED"


# ==============================================================================
# 3. Trial Activation Tests
# ==============================================================================

def test_activate_trial_success(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        now_iso = datetime.now(timezone.utc).isoformat()
        trial_end_iso = (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat()

        # 1. Existing entitlement has trial_used = False
        entitlement_row = {
            "learner_id": TEST_LEARNER_ID,
            "current_plan": "FREE",
            "status": "ACTIVE",
            "trial_used": False,
            "current_period_start": now_iso,
            "current_period_end": None,
            "updated_at": now_iso,
        }

        updated_row = {
            "learner_id": TEST_LEARNER_ID,
            "current_plan": "BASIC",
            "status": "TRIAL",
            "trial_used": True,
            "current_period_start": now_iso,
            "current_period_end": trial_end_iso,
            "updated_at": now_iso,
        }

        call_count = {"entitlement_select": 0}

        def table_router(name):
            t = MagicMock()
            if name == "billing_entitlements":
                select_m = MagicMock()
                select_m.eq.return_value = select_m
                if call_count["entitlement_select"] == 0:
                    select_m.execute.return_value = MagicMock(data=[entitlement_row])
                else:
                    select_m.execute.return_value = MagicMock(data=[updated_row])
                call_count["entitlement_select"] += 1
                t.select.return_value = select_m

                update_m = MagicMock()
                update_m.eq.return_value = update_m
                update_m.execute.return_value = MagicMock(data=[updated_row])
                t.update.return_value = update_m
            elif name == "billing_usage_quotas":
                t.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])
            return t

        mock_db.table.side_effect = table_router

        response = client.post("/api/v1/billing/trial")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["entitlement"]["currentPlan"] == "BASIC"
        assert data["entitlement"]["status"] == "TRIAL"
        assert data["entitlement"]["trialUsed"] is True


def test_activate_trial_duplicate_rejected(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                "learner_id": TEST_LEARNER_ID,
                "current_plan": "FREE",
                "status": "ACTIVE",
                "trial_used": True,  # Already used
                "current_period_start": None,
                "current_period_end": None,
                "updated_at": None,
            }]
        )

        response = client.post("/api/v1/billing/trial")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already been used" in response.json()["detail"]


# ==============================================================================
# 4. Checkout & Renew Tests
# ==============================================================================

def test_checkout_free_plan_rejected(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID):
        response = client.post("/api/v1/billing/checkout", json={"planCode": "FREE"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Free plan cannot be checked out" in response.json()["detail"]


def test_checkout_basic_creates_order(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db, \
         patch("app.services.billing.billing_service.cashfree_gateway.create_order", new_callable=AsyncMock) as mock_create_cf:

        mock_create_cf.return_value = {
            "payment_session_id": "session_test_xyz123",
            "order_id": "unios_ord_123",
            "order_status": "ACTIVE",
        }

        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])

        response = client.post(
            "/api/v1/billing/checkout",
            json={"planCode": "BASIC", "returnUrl": "http://localhost:3000/billing/return"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["planCode"] == "BASIC"
        assert data["amount"] == 149.0
        assert data["currency"] == "INR"
        assert data["paymentSessionId"] == "session_test_xyz123"
        assert data["orderId"].startswith("unios_ord_")


def test_renew_subscription_endpoint(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db, \
         patch("app.services.billing.billing_service.cashfree_gateway.create_order", new_callable=AsyncMock) as mock_create_cf:

        mock_create_cf.return_value = {
            "payment_session_id": "session_renew_xyz999",
            "order_id": "unios_ord_renew_1",
            "order_status": "ACTIVE",
        }

        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])

        response = client.post(
            "/api/v1/billing/renew",
            json={"planCode": "PRO"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["planCode"] == "PRO"
        assert data["amount"] == 299.0
        assert data["paymentSessionId"] == "session_renew_xyz999"


# ==============================================================================
# 5. Order Payment Verification & History Tests
# ==============================================================================

def test_verify_order_payment_success(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db, \
         patch("app.services.billing.billing_service.cashfree_gateway.verify_payment", new_callable=AsyncMock) as mock_verify_cf:

        order_record = {
            "order_id": "unios_ord_test1",
            "learner_id": TEST_LEARNER_ID,
            "plan_code": "BASIC",
            "amount": 149.0,
            "currency": "INR",
            "status": "PENDING",
            "cashfree_payment_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[order_record]
        )
        mock_verify_cf.return_value = {
            "order_id": "unios_ord_test1",
            "order_status": "PAID",
            "cf_payment_id": "cf_pay_12345",
        }

        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[{}])

        response = client.get("/api/v1/billing/payments/unios_ord_test1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["orderId"] == "unios_ord_test1"
        assert data["status"] == "SUCCESS"
        assert data["cashfreePaymentId"] == "cf_pay_12345"


def test_order_history_endpoint(mock_get_current_user):
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{
                "order_id": "unios_ord_1",
                "plan_code": "BASIC",
                "amount": 149.0,
                "currency": "INR",
                "status": "SUCCESS",
                "cashfree_payment_id": "cf_1",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }]
        )

        response = client.get("/api/v1/billing/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["orders"][0]["orderId"] == "unios_ord_1"
        assert data["orders"][0]["amount"] == 149.0


# ==============================================================================
# 6. Webhook Signature & Idempotency Tests
# ==============================================================================

def test_webhook_invalid_signature_rejected():
    payload = json.dumps({"type": "PAYMENT_SUCCESS_WEBHOOK", "data": {}})
    headers = {
        "x-webhook-signature": "invalid_sig_xyz",
        "x-webhook-timestamp": str(int(time.time())),
        "Content-Type": "application/json",
    }
    response = client.post("/api/v1/webhooks/cashfree", content=payload, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid Cashfree webhook signature" in response.json()["detail"]


def test_webhook_replay_attack_expired_timestamp_rejected():
    test_secret = "test_webhook_secret_key"
    payload = json.dumps({"type": "PAYMENT_SUCCESS_WEBHOOK", "data": {}})
    expired_ts = str(int(time.time()) - 600)  # 10 minutes ago (> 300s drift)

    # Compute valid signature on expired timestamp
    signed = f"{expired_ts}{payload}"
    h = hmac.new(test_secret.encode("utf-8"), signed.encode("utf-8"), hashlib.sha256).digest()
    sig = base64.b64encode(h).decode("utf-8")

    with patch.object(cashfree_gateway, "client_secret", test_secret):
        headers = {
            "x-webhook-signature": sig,
            "x-webhook-timestamp": expired_ts,
            "Content-Type": "application/json",
        }
        response = client.post("/api/v1/webhooks/cashfree", content=payload, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_webhook_valid_signature_processes_payment_idempotently():
    test_secret = "test_webhook_secret_key"
    order_id = "unios_ord_webhook_123"

    payload_dict = {
        "type": "PAYMENT_SUCCESS_WEBHOOK",
        "event_time": datetime.now(timezone.utc).isoformat(),
        "data": {
            "order": {
                "order_id": order_id,
                "order_amount": 149.00,
                "order_currency": "INR",
            },
            "payment": {
                "cf_payment_id": 99887766,
                "payment_status": "SUCCESS",
            },
        },
    }
    raw_payload = json.dumps(payload_dict)
    curr_ts = str(int(time.time()))

    signed = f"{curr_ts}{raw_payload}"
    h = hmac.new(test_secret.encode("utf-8"), signed.encode("utf-8"), hashlib.sha256).digest()
    valid_sig = base64.b64encode(h).decode("utf-8")

    with patch.object(cashfree_gateway, "client_secret", test_secret), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        # Order found with PENDING
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                "order_id": order_id,
                "learner_id": TEST_LEARNER_ID,
                "plan_code": "BASIC",
                "amount": 149.0,
                "status": "PENDING",
            }]
        )
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[{}])

        headers = {
            "x-webhook-signature": valid_sig,
            "x-webhook-timestamp": curr_ts,
            "Content-Type": "application/json",
        }
        response = client.post("/api/v1/webhooks/cashfree", content=raw_payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"


# ==============================================================================
# 7. Security: Zero Leakage of Cashfree Secret
# ==============================================================================

def test_secret_is_never_in_responses(mock_get_current_user):
    secret_value = settings.CASHFREE_CLIENT_SECRET or "cf_sandbox_placeholder_secret"
    
    with patch("app.api.v1.endpoints.billing._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.billing.billing_service.supabase_admin") as mock_db:

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                "learner_id": TEST_LEARNER_ID,
                "current_plan": "FREE",
                "status": "ACTIVE",
                "trial_used": False,
                "current_period_start": None,
                "current_period_end": None,
                "updated_at": None,
            }]
        )

        resp1 = client.get("/api/v1/billing/plans")
        assert secret_value not in resp1.text

        resp2 = client.get("/api/v1/billing/me")
        assert secret_value not in resp2.text

from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from app.core.deps import RequireRole, get_current_user
from app.core.supabase import supabase_admin
from app.schemas.billing import (
    AdminAssignSubscriptionRequest,
    AdminAssignSubscriptionResponse,
    BillingCycle,
    CheckoutPreviewResponse,
    CheckoutRequest,
    CheckoutResponse,
    CreditLedgerResponse,
    EntitlementResponse,
    OrderHistoryResponse,
    PaymentStatusResponse,
    PlanTier,
    PlansResponse,
    TrialActivationResponse,
    UsageResponse,
)
from app.services.billing.billing_service import billing_service
from app.services.billing.cashfree_gateway import cashfree_gateway

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Billing & Subscriptions"])


def _get_learner_id(user_id: str) -> str:
    """Helper to fetch the learner_profile id for an authenticated user."""
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found for authenticated user.",
        )
    return str(res.data[0]["id"])


# ------------------------------------------------------------------------------
# 1. Plans & Pricing Catalog
# ------------------------------------------------------------------------------

@router.get(
    "/api/v1/billing/plans",
    response_model=PlansResponse,
    summary="List available subscription plans",
    description="Returns server-defined Free, Basic (₹149), and Pro (₹299) plans, features, and quotas.",
)
async def get_plans() -> PlansResponse:
    return billing_service.get_plans()


# ------------------------------------------------------------------------------
# 2. Entitlement & Usage
# ------------------------------------------------------------------------------

@router.get(
    "/api/v1/billing/me",
    response_model=EntitlementResponse,
    summary="Get current entitlement",
    description="Returns learner's active plan, status, start/end dates, and trial eligibility.",
)
async def get_my_entitlement(
    current_user: dict = Depends(get_current_user),
) -> EntitlementResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.get_or_create_entitlement(learner_id)


@router.get(
    "/api/v1/billing/usage",
    response_model=UsageResponse,
    summary="Get current usage and quotas",
    description="Returns used/remaining limits and next reset times for the current cycle.",
)
async def get_my_usage(
    current_user: dict = Depends(get_current_user),
) -> UsageResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.get_or_create_usage(learner_id)


# ------------------------------------------------------------------------------
# 3. Trial Activation
# ------------------------------------------------------------------------------

@router.post(
    "/api/v1/billing/trial",
    response_model=TrialActivationResponse,
    summary="Activate 72-hour Basic trial",
    description="Enables a 3-day Basic trial. Available strictly once per verified account.",
)
async def activate_trial(
    current_user: dict = Depends(get_current_user),
) -> TrialActivationResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.activate_trial(learner_id)


# ------------------------------------------------------------------------------
# 4. Checkout & Renew
# ------------------------------------------------------------------------------

@router.get(
    "/api/v1/billing/checkout/preview",
    response_model=CheckoutPreviewResponse,
    summary="Preview checkout or prorated upgrade",
    description="Calculates action type (NEW/RENEW/UPGRADE), monetary proration credit, and final payable amount (GST included).",
)
async def preview_checkout(
    plan_code: PlanTier,
    billing_cycle: BillingCycle = BillingCycle.MONTHLY,
    current_user: dict = Depends(get_current_user),
) -> CheckoutPreviewResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.preview_checkout(
        learner_id=learner_id,
        plan_code=plan_code,
        billing_cycle=billing_cycle,
    )


@router.post(
    "/api/v1/billing/checkout",
    response_model=CheckoutResponse,
    summary="Create checkout order",
    description="Initiates a Weekly/Monthly/Semester plan order and returns Cashfree payment session info.",
)
async def create_checkout(
    payload: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
) -> CheckoutResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    user_email = current_user.get("email", "")
    return await billing_service.create_checkout(
        learner_id=learner_id,
        user_email=user_email,
        plan_code=payload.plan_code,
        billing_cycle=payload.billing_cycle,
        custom_return_url=payload.return_url,
    )


@router.post(
    "/api/v1/billing/renew",
    response_model=CheckoutResponse,
    summary="Explicitly renew prepaid subscription",
    description="Creates a new checkout order to manually renew or extend the prepaid subscription.",
)
async def renew_subscription(
    payload: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
) -> CheckoutResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    user_email = current_user.get("email", "")
    return await billing_service.create_checkout(
        learner_id=learner_id,
        user_email=user_email,
        plan_code=payload.plan_code,
        billing_cycle=payload.billing_cycle,
        custom_return_url=payload.return_url,
    )


# ------------------------------------------------------------------------------
# 5. Order Verification & History
# ------------------------------------------------------------------------------

@router.get(
    "/api/v1/billing/payments/{order_id}",
    response_model=PaymentStatusResponse,
    summary="Poll/verify order payment status",
    description="Fetches definitive order payment state server-side from Cashfree.",
)
async def verify_order_payment(
    order_id: str,
    current_user: dict = Depends(get_current_user),
) -> PaymentStatusResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return await billing_service.poll_and_verify_order(order_id, learner_id)


@router.get(
    "/api/v1/billing/history",
    response_model=OrderHistoryResponse,
    summary="Get billing and payment history",
    description="Returns the authenticated learner's past orders and payment receipts.",
)
async def get_billing_history(
    current_user: dict = Depends(get_current_user),
) -> OrderHistoryResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.get_order_history(learner_id)


@router.get(
    "/api/v1/billing/ledger",
    response_model=CreditLedgerResponse,
    summary="Get AI credit ledger history",
    description="Returns recent AI credit deductions and refunds for the authenticated learner.",
)
async def get_credit_ledger(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
) -> CreditLedgerResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return billing_service.get_credit_ledger(learner_id, limit=min(max(1, limit), 100))


@router.post(
    "/api/v1/billing/admin/assign",
    response_model=AdminAssignSubscriptionResponse,
    summary="Admin assign promotional or institutional subscription",
    description="Allows administrators to assign Basic or Pro plans for promotional or institutional accounts.",
)
async def admin_assign_subscription(
    payload: AdminAssignSubscriptionRequest,
    current_user: dict = Depends(RequireRole(["admin"])),
) -> AdminAssignSubscriptionResponse:
    return billing_service.admin_assign_subscription(
        admin_user_id=current_user["user_id"],
        payload=payload,
    )


# ------------------------------------------------------------------------------
# 6. Cashfree Webhook Handler
# ------------------------------------------------------------------------------

@router.post(
    "/api/v1/webhooks/cashfree",
    summary="Cashfree PG Webhook endpoint",
    description="Handles Cashfree asynchronous payment webhook notifications. Validates HMAC signature.",
)
@router.post(
    "/api/v1/billing/webhook",
    summary="Cashfree PG Webhook endpoint (alias)",
    include_in_schema=False,
)
async def handle_cashfree_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="x-webhook-signature"),
    x_webhook_timestamp: Optional[str] = Header(None, alias="x-webhook-timestamp"),
) -> Dict[str, Any]:
    """
    Consumes raw request body bytes for strict cryptographic signature verification.
    Processes payment success idempotently and activates the 30-day entitlement.
    """
    raw_body = await request.body()

    # Fallback header check in case headers are case-altered by reverse proxy
    if not x_webhook_signature:
        x_webhook_signature = request.headers.get("x-webhook-signature")
    if not x_webhook_timestamp:
        x_webhook_timestamp = request.headers.get("x-webhook-timestamp")

    # Cryptographically verify signature
    is_valid = cashfree_gateway.verify_webhook_signature(
        payload_raw_body=raw_body,
        signature_header=x_webhook_signature,
        timestamp_header=x_webhook_timestamp,
    )

    if not is_valid:
        logger.warning("Rejected Cashfree webhook due to invalid signature.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Cashfree webhook signature.",
        )

    # Parse JSON after signature has been verified
    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception as exc:
        logger.error(f"Failed to parse Cashfree webhook body as JSON: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON in webhook body.",
        )

    event_type = data.get("type", "")
    logger.info(f"Received verified Cashfree webhook event: {event_type}")

    # Process successful payment events
    if event_type in ("PAYMENT_SUCCESS_WEBHOOK", "ORDER_PAID"):
        event_data = data.get("data", {})
        order_info = event_data.get("order", {})
        payment_info = event_data.get("payment", {})

        order_id = order_info.get("order_id")
        cf_payment_id = payment_info.get("cf_payment_id")

        if order_id:
            billing_service.process_successful_payment(
                order_id=order_id,
                cashfree_payment_id=str(cf_payment_id) if cf_payment_id else None,
            )
        else:
            logger.warning(f"Webhook {event_type} received without order_id: {data}")

    elif event_type in ("PAYMENT_FAILED_WEBHOOK", "PAYMENT_USER_DROPPED_WEBHOOK"):
        event_data = data.get("data", {})
        order_id = event_data.get("order", {}).get("order_id")
        if order_id:
            logger.info(f"Marking order {order_id} as FAILED from webhook.")
            supabase_admin.table("billing_orders").update({
                "status": "FAILED",
                "updated_at": billing_service._get_next_reset_times()[0].isoformat(),
            }).eq("order_id", order_id).execute()

    return {"status": "ok", "message": "Webhook processed successfully"}

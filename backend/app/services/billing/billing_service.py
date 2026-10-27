from __future__ import annotations
from datetime import datetime, timedelta, timezone
import logging
import uuid
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.supabase import supabase_admin
from app.schemas.billing import (
    CheckoutResponse,
    EntitlementResponse,
    EntitlementStatus,
    OrderHistoryItem,
    OrderHistoryResponse,
    OrderStatus,
    PaymentStatusResponse,
    PlanConfiguration,
    PlanQuotaMatrix,
    PlanTier,
    PlansResponse,
    QuotaUsageDetail,
    TrialActivationResponse,
    UsageResponse,
)
from app.services.billing.cashfree_gateway import cashfree_gateway

logger = logging.getLogger(__name__)

# Asia/Kolkata timezone offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Server-authoritative plan catalog
PLAN_CATALOG: Dict[PlanTier, PlanConfiguration] = {
    PlanTier.FREE: PlanConfiguration(
        plan_code=PlanTier.FREE,
        name="Free Plan",
        price=0.0,
        currency="INR",
        duration_days=0,
        description="Acquisition plan with ongoing core learning and controlled AI usage.",
        features=[
            "Multiple subjects supported (no subject cap)",
            "3 successful AI roadmap generations / month",
            "5 successful AI tutor doubt requests / day",
            "10 practice questions / day",
            "1 Resume generation / month",
            "1 ATS Resume check / month",
            "BUILD idea discovery preview",
            "COMPETE opportunities preview",
        ],
        quotas=PlanQuotaMatrix(
            ai_roadmap_generations=3,
            ai_roadmap_period="monthly",
            ai_tutor_requests=5,
            ai_tutor_period="daily",
            practice_questions=10,
            practice_questions_period="daily",
            resume_generations=1,
            resume_generations_period="monthly",
            ats_checks=1,
            ats_checks_period="monthly",
            project_tracking_included=False,
            ai_project_guidance=3,
            compete_access="preview",
        ),
    ),
    PlanTier.BASIC: PlanConfiguration(
        plan_code=PlanTier.BASIC,
        name="Basic Plan",
        price=149.0,
        currency="INR",
        duration_days=30,
        description="Everyday student plan with enhanced AI limits and paid feature access.",
        features=[
            "Multiple subjects supported (no subject cap)",
            "15 successful AI roadmap generations / month",
            "25 successful AI tutor doubt requests / day",
            "50 practice questions / day",
            "5 Resume generations / month",
            "3 ATS Resume checks / month",
            "Full project creation & tracking",
            "10 AI project guidance requests / month",
            "Full COMPETE opportunity feed",
        ],
        quotas=PlanQuotaMatrix(
            ai_roadmap_generations=15,
            ai_roadmap_period="monthly",
            ai_tutor_requests=25,
            ai_tutor_period="daily",
            practice_questions=50,
            practice_questions_period="daily",
            resume_generations=5,
            resume_generations_period="monthly",
            ats_checks=3,
            ats_checks_period="monthly",
            project_tracking_included=True,
            ai_project_guidance=10,
            compete_access="full",
        ),
    ),
    PlanTier.PRO: PlanConfiguration(
        plan_code=PlanTier.PRO,
        name="Pro Plan",
        price=299.0,
        currency="INR",
        duration_days=30,
        description="Higher usage allowances for students who use UniOS.ai frequently.",
        features=[
            "Multiple subjects supported (no subject cap)",
            "40 successful AI roadmap generations / month",
            "60 successful AI tutor doubt requests / day",
            "150 practice questions / day",
            "15 Resume generations / month",
            "10 ATS Resume checks / month",
            "Advanced project creation & tracking",
            "50 AI project guidance requests / month",
            "Full COMPETE opportunity feed & priority filters",
        ],
        quotas=PlanQuotaMatrix(
            ai_roadmap_generations=40,
            ai_roadmap_period="monthly",
            ai_tutor_requests=60,
            ai_tutor_period="daily",
            practice_questions=150,
            practice_questions_period="daily",
            resume_generations=15,
            resume_generations_period="monthly",
            ats_checks=10,
            ats_checks_period="monthly",
            project_tracking_included=True,
            ai_project_guidance=50,
            compete_access="full",
        ),
    ),
}


class BillingService:
    """
    Core business logic service for subscriptions, entitlements, quotas,
    checkout session management, and order lifecycle.
    """

    @staticmethod
    def get_plans() -> PlansResponse:
        """Returns the server-defined pricing and quota configurations."""
        return PlansResponse(plans=list(PLAN_CATALOG.values()))

    @staticmethod
    def _get_next_reset_times() -> tuple[datetime, datetime]:
        """Calculates next daily (00:00 IST) and monthly (1st of month 00:00 IST) reset times."""
        now_ist = datetime.now(IST)
        
        # Next daily reset: tomorrow at 00:00:00 IST
        tomorrow_ist = (now_ist + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        next_daily = tomorrow_ist.astimezone(timezone.utc)

        # Next monthly reset: first day of next month at 00:00:00 IST
        if now_ist.month == 12:
            next_month = now_ist.replace(year=now_ist.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now_ist.replace(month=now_ist.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        next_monthly = next_month.astimezone(timezone.utc)

        return next_daily, next_monthly

    def get_or_create_entitlement(self, learner_id: str) -> EntitlementResponse:
        """
        Retrieves the learner's current entitlement. If none exists, creates a FREE tier record.
        Automatically verifies whether an active paid plan or trial has expired.
        """
        res = (
            supabase_admin.table("billing_entitlements")
            .select("*")
            .eq("learner_id", learner_id)
            .execute()
        )

        now_utc = datetime.now(timezone.utc)

        if not res.data:
            # Create default FREE entitlement
            new_entitlement = {
                "learner_id": learner_id,
                "current_plan": PlanTier.FREE.value,
                "status": EntitlementStatus.ACTIVE.value,
                "trial_used": False,
                "current_period_start": now_utc.isoformat(),
                "current_period_end": None,
                "updated_at": now_utc.isoformat(),
            }
            insert_res = (
                supabase_admin.table("billing_entitlements")
                .insert(new_entitlement)
                .execute()
            )
            row = insert_res.data[0]
        else:
            row = res.data[0]

        # Check for expiration
        current_plan = PlanTier(row["current_plan"])
        status = EntitlementStatus(row["status"])
        trial_used = bool(row["trial_used"])
        period_end = None

        if row.get("current_period_end"):
            period_end = datetime.fromisoformat(row["current_period_end"])
            if period_end.tzinfo is None:
                period_end = period_end.replace(tzinfo=timezone.utc)

            # If end date is in the past and plan was paid/trial, expire and revert to FREE
            if period_end < now_utc and status in (EntitlementStatus.ACTIVE, EntitlementStatus.TRIAL) and current_plan != PlanTier.FREE:
                logger.info(f"Entitlement expired for learner {learner_id}. Reverting to FREE tier.")
                update_res = (
                    supabase_admin.table("billing_entitlements")
                    .update({
                        "current_plan": PlanTier.FREE.value,
                        "status": EntitlementStatus.EXPIRED.value,
                        "updated_at": now_utc.isoformat(),
                    })
                    .eq("learner_id", learner_id)
                    .execute()
                )
                row = update_res.data[0]
                current_plan = PlanTier.FREE
                status = EntitlementStatus.EXPIRED

        is_active = status == EntitlementStatus.ACTIVE
        is_trial = status == EntitlementStatus.TRIAL

        days_remaining = None
        if period_end and period_end > now_utc:
            delta = period_end - now_utc
            days_remaining = max(0, delta.days)

        start_dt = None
        if row.get("current_period_start"):
            start_dt = datetime.fromisoformat(row["current_period_start"])

        return EntitlementResponse(
            learner_id=learner_id,
            current_plan=current_plan,
            status=status,
            trial_used=trial_used,
            current_period_start=start_dt,
            current_period_end=period_end,
            is_active=is_active or is_trial,
            is_trial=is_trial,
            days_remaining=days_remaining,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
        )

    def get_or_create_usage(self, learner_id: str) -> UsageResponse:
        """
        Fetches the current usage cycle limits and consumed quantities for the learner.
        Initializes the quota tracker row if not present.
        """
        entitlement = self.get_or_create_entitlement(learner_id)
        plan_config = PLAN_CATALOG.get(entitlement.current_plan, PLAN_CATALOG[PlanTier.FREE])
        quotas_def = plan_config.quotas

        res = (
            supabase_admin.table("billing_usage_quotas")
            .select("*")
            .eq("learner_id", learner_id)
            .execute()
        )

        now_utc = datetime.now(timezone.utc)

        if not res.data:
            new_usage = {
                "learner_id": learner_id,
                "period_start": now_utc.isoformat(),
                "ai_roadmap_generations": 0,
                "ai_tutor_requests": 0,
                "practice_questions": 0,
                "resume_generations": 0,
                "ats_checks": 0,
                "updated_at": now_utc.isoformat(),
            }
            insert_res = (
                supabase_admin.table("billing_usage_quotas")
                .insert(new_usage)
                .execute()
            )
            row = insert_res.data[0]
        else:
            row = res.data[0]

        # Calculate remaining values
        used_roadmaps = int(row.get("ai_roadmap_generations") or 0)
        used_tutor = int(row.get("ai_tutor_requests") or 0)
        used_questions = int(row.get("practice_questions") or 0)
        used_resumes = int(row.get("resume_generations") or 0)
        used_ats = int(row.get("ats_checks") or 0)

        next_daily, next_monthly = self._get_next_reset_times()

        period_start = None
        if row.get("period_start"):
            period_start = datetime.fromisoformat(row["period_start"])

        return UsageResponse(
            learner_id=learner_id,
            period_start=period_start,
            quotas={
                "aiRoadmapGenerations": QuotaUsageDetail(
                    used=used_roadmaps,
                    limit=quotas_def.ai_roadmap_generations,
                    remaining=max(0, quotas_def.ai_roadmap_generations - used_roadmaps),
                    period=quotas_def.ai_roadmap_period,
                ),
                "aiTutorRequests": QuotaUsageDetail(
                    used=used_tutor,
                    limit=quotas_def.ai_tutor_requests,
                    remaining=max(0, quotas_def.ai_tutor_requests - used_tutor),
                    period=quotas_def.ai_tutor_period,
                ),
                "practiceQuestions": QuotaUsageDetail(
                    used=used_questions,
                    limit=quotas_def.practice_questions,
                    remaining=max(0, quotas_def.practice_questions - used_questions),
                    period=quotas_def.practice_questions_period,
                ),
                "resumeGenerations": QuotaUsageDetail(
                    used=used_resumes,
                    limit=quotas_def.resume_generations,
                    remaining=max(0, quotas_def.resume_generations - used_resumes),
                    period=quotas_def.resume_generations_period,
                ),
                "atsChecks": QuotaUsageDetail(
                    used=used_ats,
                    limit=quotas_def.ats_checks,
                    remaining=max(0, quotas_def.ats_checks - used_ats),
                    period=quotas_def.ats_checks_period,
                ),
            },
            next_reset_daily=next_daily,
            next_reset_monthly=next_monthly,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
        )

    def activate_trial(self, learner_id: str) -> TrialActivationResponse:
        """
        Activates a 72-hour Basic plan trial. Allowed strictly once per verified account.
        """
        entitlement = self.get_or_create_entitlement(learner_id)

        if entitlement.trial_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 72-hour Basic trial has already been used on this account.",
            )

        if entitlement.is_active and entitlement.current_plan in (PlanTier.BASIC, PlanTier.PRO):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already has an active paid subscription.",
            )

        now_utc = datetime.now(timezone.utc)
        trial_end_utc = now_utc + timedelta(hours=72)

        update_res = (
            supabase_admin.table("billing_entitlements")
            .update({
                "current_plan": PlanTier.BASIC.value,
                "status": EntitlementStatus.TRIAL.value,
                "trial_used": True,
                "current_period_start": now_utc.isoformat(),
                "current_period_end": trial_end_utc.isoformat(),
                "updated_at": now_utc.isoformat(),
            })
            .eq("learner_id", learner_id)
            .execute()
        )

        # Reset quotas for fresh trial
        supabase_admin.table("billing_usage_quotas").update({
            "period_start": now_utc.isoformat(),
            "ai_roadmap_generations": 0,
            "ai_tutor_requests": 0,
            "practice_questions": 0,
            "resume_generations": 0,
            "ats_checks": 0,
            "updated_at": now_utc.isoformat(),
        }).eq("learner_id", learner_id).execute()

        refreshed_entitlement = self.get_or_create_entitlement(learner_id)

        return TrialActivationResponse(
            success=True,
            message="72-hour Basic trial activated successfully.",
            entitlement=refreshed_entitlement,
        )

    async def create_checkout(
        self,
        learner_id: str,
        user_email: str,
        plan_code: PlanTier,
        custom_return_url: Optional[str] = None,
        user_phone: Optional[str] = None,
    ) -> CheckoutResponse:
        """
        Initiates order checkout. Price is determined strictly server-side.
        Creates pending billing order in DB and requests Cashfree session ID.
        """
        if plan_code == PlanTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free plan cannot be checked out via payment gateway.",
            )

        plan = PLAN_CATALOG.get(plan_code)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan code '{plan_code}'.",
            )

        order_id = f"unios_ord_{uuid.uuid4().hex[:16]}"
        now_utc = datetime.now(timezone.utc)

        # 1. Create order record with PENDING status
        order_record = {
            "order_id": order_id,
            "learner_id": learner_id,
            "plan_code": plan_code.value,
            "amount": plan.price,
            "currency": "INR",
            "status": OrderStatus.PENDING.value,
            "created_at": now_utc.isoformat(),
            "updated_at": now_utc.isoformat(),
        }

        supabase_admin.table("billing_orders").insert(order_record).execute()

        # 2. Prepare return URL
        base_return = custom_return_url or settings.CASHFREE_RETURN_URL
        separator = "&" if "?" in base_return else "?"
        return_url = f"{base_return}{separator}order_id={order_id}"

        # 3. Call Cashfree PG to create order
        customer_details = {
            "customer_id": learner_id,
            "customer_email": user_email,
            "customer_phone": user_phone or "9999999999",
        }

        cf_response = await cashfree_gateway.create_order(
            order_id=order_id,
            amount=plan.price,
            customer_details=customer_details,
            return_url=return_url,
            order_note=f"UniOS {plan.name} (30-day access)",
        )

        payment_session_id = cf_response.get("payment_session_id", "")

        # 4. Save session ID to order record
        supabase_admin.table("billing_orders").update({
            "payment_session_id": payment_session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("order_id", order_id).execute()

        return CheckoutResponse(
            order_id=order_id,
            payment_session_id=payment_session_id,
            environment=cashfree_gateway.env,
            amount=plan.price,
            currency="INR",
            plan_code=plan_code,
        )

    def process_successful_payment(
        self,
        order_id: str,
        cashfree_payment_id: Optional[str] = None,
    ) -> None:
        """
        Idempotent payment confirmation.
        Marks billing_order as SUCCESS, extends entitlement by 30 days, and resets usage quotas.
        """
        res = (
            supabase_admin.table("billing_orders")
            .select("*")
            .eq("order_id", order_id)
            .execute()
        )

        if not res.data:
            logger.warning(f"Payment process skipped: order '{order_id}' not found.")
            return

        order = res.data[0]

        # Idempotency check: if order is already SUCCESS, skip
        if order.get("status") == OrderStatus.SUCCESS.value:
            logger.info(f"Order '{order_id}' is already SUCCESS. Skipping re-grant.")
            return

        now_utc = datetime.now(timezone.utc)
        learner_id = order["learner_id"]
        plan_code = PlanTier(order["plan_code"])

        # 1. Update order status to SUCCESS
        supabase_admin.table("billing_orders").update({
            "status": OrderStatus.SUCCESS.value,
            "cashfree_payment_id": cashfree_payment_id,
            "updated_at": now_utc.isoformat(),
        }).eq("order_id", order_id).execute()

        # 2. Calculate new period start & end (30-day prepaid)
        entitlement_res = (
            supabase_admin.table("billing_entitlements")
            .select("*")
            .eq("learner_id", learner_id)
            .execute()
        )

        existing_end = None
        if entitlement_res.data and entitlement_res.data[0].get("current_period_end"):
            parsed_end = datetime.fromisoformat(entitlement_res.data[0]["current_period_end"])
            if parsed_end.tzinfo is None:
                parsed_end = parsed_end.replace(tzinfo=timezone.utc)
            # If current plan is active and same or higher tier, extend from end date
            if parsed_end > now_utc:
                existing_end = parsed_end

        period_start = now_utc
        period_end = (existing_end or now_utc) + timedelta(days=30)

        # 3. Update entitlement table
        supabase_admin.table("billing_entitlements").upsert({
            "learner_id": learner_id,
            "current_plan": plan_code.value,
            "status": EntitlementStatus.ACTIVE.value,
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        # 4. Reset quotas for new billing cycle
        supabase_admin.table("billing_usage_quotas").upsert({
            "learner_id": learner_id,
            "period_start": now_utc.isoformat(),
            "ai_roadmap_generations": 0,
            "ai_tutor_requests": 0,
            "practice_questions": 0,
            "resume_generations": 0,
            "ats_checks": 0,
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        logger.info(
            f"Successfully processed payment for order {order_id}. Plan {plan_code.value} granted to learner {learner_id} until {period_end.isoformat()}."
        )

    async def poll_and_verify_order(
        self,
        order_id: str,
        learner_id: str,
    ) -> PaymentStatusResponse:
        """
        Polls payment status server-side from Cashfree and applies entitlement if confirmed PAID.
        """
        res = (
            supabase_admin.table("billing_orders")
            .select("*")
            .eq("order_id", order_id)
            .execute()
        )

        if not res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order '{order_id}' not found.",
            )

        order = res.data[0]
        if str(order["learner_id"]) != str(learner_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this order.",
            )

        # If already SUCCESS, return status directly
        if order.get("status") == OrderStatus.SUCCESS.value:
            return PaymentStatusResponse(
                order_id=order_id,
                status=OrderStatus.SUCCESS,
                plan_code=PlanTier(order["plan_code"]),
                amount=float(order["amount"]),
                currency=order.get("currency", "INR"),
                cashfree_payment_id=order.get("cashfree_payment_id"),
                created_at=datetime.fromisoformat(order["created_at"]) if order.get("created_at") else None,
                updated_at=datetime.fromisoformat(order["updated_at"]) if order.get("updated_at") else None,
            )

        # Verify status directly with Cashfree
        cf_status_data = await cashfree_gateway.verify_payment(order_id)
        cf_order_status = cf_status_data.get("order_status")

        if cf_order_status == "PAID":
            cf_payment_id = cf_status_data.get("cf_payment_id")
            self.process_successful_payment(order_id, cashfree_payment_id=cf_payment_id)
            return PaymentStatusResponse(
                order_id=order_id,
                status=OrderStatus.SUCCESS,
                plan_code=PlanTier(order["plan_code"]),
                amount=float(order["amount"]),
                currency=order.get("currency", "INR"),
                cashfree_payment_id=cf_payment_id,
                created_at=datetime.fromisoformat(order["created_at"]) if order.get("created_at") else None,
                updated_at=datetime.now(timezone.utc),
            )
        elif cf_order_status == "EXPIRED":
            supabase_admin.table("billing_orders").update({
                "status": OrderStatus.FAILED.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("order_id", order_id).execute()
            status_val = OrderStatus.FAILED
        else:
            status_val = OrderStatus(order["status"])

        return PaymentStatusResponse(
            order_id=order_id,
            status=status_val,
            plan_code=PlanTier(order["plan_code"]),
            amount=float(order["amount"]),
            currency=order.get("currency", "INR"),
            cashfree_payment_id=order.get("cashfree_payment_id"),
            created_at=datetime.fromisoformat(order["created_at"]) if order.get("created_at") else None,
            updated_at=datetime.fromisoformat(order["updated_at"]) if order.get("updated_at") else None,
        )

    def get_order_history(self, learner_id: str) -> OrderHistoryResponse:
        """Retrieves past payment orders for the learner."""
        res = (
            supabase_admin.table("billing_orders")
            .select("*")
            .eq("learner_id", learner_id)
            .order("created_at", desc=True)
            .execute()
        )

        items: List[OrderHistoryItem] = []
        for row in res.data or []:
            items.append(
                OrderHistoryItem(
                    order_id=row["order_id"],
                    plan_code=PlanTier(row["plan_code"]),
                    amount=float(row["amount"]),
                    currency=row.get("currency", "INR"),
                    status=OrderStatus(row["status"]),
                    cashfree_payment_id=row.get("cashfree_payment_id"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None,
                )
            )

        return OrderHistoryResponse(orders=items, total=len(items))


billing_service = BillingService()

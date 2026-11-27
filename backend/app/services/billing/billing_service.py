from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.deps import validate_redirect_url
from app.core.supabase import supabase_admin
from app.schemas.billing import (
    AdminAssignSubscriptionRequest,
    AdminAssignSubscriptionResponse,
    BillingCycle,
    CheckoutPreviewResponse,
    CheckoutResponse,
    CreditLedgerItem,
    CreditLedgerResponse,
    CreditSummary,
    EntitlementResponse,
    EntitlementStatus,
    ModuleCreditDetail,
    OrderHistoryItem,
    OrderHistoryResponse,
    OrderStatus,
    PaymentStatusResponse,
    PlanConfiguration,
    PlanCycleOption,
    PlanQuotaMatrix,
    PlanTier,
    PlansResponse,
    QuotaUsageDetail,
    RenewalPolicy,
    SubscriptionSource,
    TrialActivationResponse,
    UsageResponse,
)
from app.services.billing.cashfree_gateway import cashfree_gateway

logger = logging.getLogger(__name__)

# Asia/Kolkata timezone offset (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

COMING_SOON_FEATURES = ["AI Mock Interviews", "GitHub Integration", "COMPETE"]


@dataclass(frozen=True)
class SKUConfig:
    plan_code: PlanTier
    billing_cycle: BillingCycle
    duration_days: int
    price: float  # GST included (INR)
    total_credits: int
    module_credits: Dict[str, int]
    mock_tests: int
    ats_checks: int
    mock_interviews: int
    renewal_policy: RenewalPolicy


# Authoritative server-side SKU matrix (all prices GST included)
SKU_CATALOG: Dict[Tuple[PlanTier, BillingCycle], SKUConfig] = {
    (PlanTier.FREE, BillingCycle.MONTHLY): SKUConfig(
        plan_code=PlanTier.FREE,
        billing_cycle=BillingCycle.MONTHLY,
        duration_days=0,
        price=0.0,
        total_credits=30,
        module_credits={"LEARN": 20, "BUILD": 5, "LAUNCH": 5},
        mock_tests=1,
        ats_checks=1,
        mock_interviews=0,
        renewal_policy=RenewalPolicy.NONE,
    ),
    (PlanTier.BASIC, BillingCycle.WEEKLY): SKUConfig(
        plan_code=PlanTier.BASIC,
        billing_cycle=BillingCycle.WEEKLY,
        duration_days=7,
        price=49.0,
        total_credits=117,
        module_credits={"LEARN": 70, "BUILD": 29, "LAUNCH": 18},
        mock_tests=2,
        ats_checks=2,
        mock_interviews=1,
        renewal_policy=RenewalPolicy.ONE_TIME,
    ),
    (PlanTier.BASIC, BillingCycle.MONTHLY): SKUConfig(
        plan_code=PlanTier.BASIC,
        billing_cycle=BillingCycle.MONTHLY,
        duration_days=30,
        price=149.0,
        total_credits=500,
        module_credits={"LEARN": 300, "BUILD": 125, "LAUNCH": 75},
        mock_tests=5,
        ats_checks=5,
        mock_interviews=2,
        renewal_policy=RenewalPolicy.MANUAL,
    ),
    (PlanTier.BASIC, BillingCycle.SEMESTER): SKUConfig(
        plan_code=PlanTier.BASIC,
        billing_cycle=BillingCycle.SEMESTER,
        duration_days=150,
        price=599.0,
        total_credits=500,  # Refreshes every 30 days (5 cycles)
        module_credits={"LEARN": 300, "BUILD": 125, "LAUNCH": 75},
        mock_tests=5,
        ats_checks=5,
        mock_interviews=2,
        renewal_policy=RenewalPolicy.ONE_TIME,
    ),
    (PlanTier.PRO, BillingCycle.WEEKLY): SKUConfig(
        plan_code=PlanTier.PRO,
        billing_cycle=BillingCycle.WEEKLY,
        duration_days=7,
        price=99.0,
        total_credits=350,
        module_credits={"LEARN": 210, "BUILD": 88, "LAUNCH": 52},
        mock_tests=5,
        ats_checks=5,
        mock_interviews=3,
        renewal_policy=RenewalPolicy.ONE_TIME,
    ),
    (PlanTier.PRO, BillingCycle.MONTHLY): SKUConfig(
        plan_code=PlanTier.PRO,
        billing_cycle=BillingCycle.MONTHLY,
        duration_days=30,
        price=299.0,
        total_credits=1500,
        module_credits={"LEARN": 900, "BUILD": 375, "LAUNCH": 225},
        mock_tests=20,
        ats_checks=20,
        mock_interviews=10,
        renewal_policy=RenewalPolicy.MANUAL,
    ),
    (PlanTier.PRO, BillingCycle.SEMESTER): SKUConfig(
        plan_code=PlanTier.PRO,
        billing_cycle=BillingCycle.SEMESTER,
        duration_days=150,
        price=1199.0,
        total_credits=1500,  # Refreshes every 30 days (5 cycles)
        module_credits={"LEARN": 900, "BUILD": 375, "LAUNCH": 225},
        mock_tests=20,
        ats_checks=20,
        mock_interviews=10,
        renewal_policy=RenewalPolicy.ONE_TIME,
    ),
}

_TIER_RANK = {PlanTier.FREE: 0, PlanTier.BASIC: 1, PlanTier.PRO: 2}
_CYCLE_RANK = {BillingCycle.WEEKLY: 1, BillingCycle.MONTHLY: 2, BillingCycle.SEMESTER: 3}


def _to_cycle_option(sku: SKUConfig) -> PlanCycleOption:
    return PlanCycleOption(
        billing_cycle=sku.billing_cycle,
        duration_days=sku.duration_days,
        price=sku.price,
        currency="INR",
        gst_included=True,
        total_credits=sku.total_credits,
        module_credits=dict(sku.module_credits),
        mock_tests=sku.mock_tests,
        ats_checks=sku.ats_checks,
        mock_interviews=sku.mock_interviews,
        renewal_policy=sku.renewal_policy,
    )


# Server-authoritative plan catalog (top-level price/duration reflect Monthly defaults)
PLAN_CATALOG: Dict[PlanTier, PlanConfiguration] = {
    PlanTier.FREE: PlanConfiguration(
        plan_code=PlanTier.FREE,
        name="Free Plan",
        price=0.0,
        currency="INR",
        gst_included=True,
        duration_days=0,
        description="Explore and experience UniOS.ai with essential learning, build, and launch access.",
        features=[
            "30 AI Credits / 30 days (20 Learn · 5 Build · 5 Launch)",
            "Basic AI Subject Tutor & limited syllabus PDF analysis",
            "Sample personalized learning roadmap & basic progress tracking",
            "1 Mock Test / month & 10 practice questions / day",
            "Basic project library browsing & project tracking",
            "Basic resume builder (2 starter templates) & 1 ATS scan / month",
            "COMPETE opportunities preview (Coming Soon)",
        ],
        coming_soon_features=list(COMING_SOON_FEATURES),
        cycles=[_to_cycle_option(SKU_CATALOG[(PlanTier.FREE, BillingCycle.MONTHLY)])],
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
            mock_tests=1,
            mock_tests_period="monthly",
            mock_interviews=0,
            mock_interviews_period="monthly",
            monthly_credits=30,
            module_credits={"LEARN": 20, "BUILD": 5, "LAUNCH": 5},
            project_tracking_included=True,
            ai_project_guidance=3,
            debugging_access="NONE",
            project_evaluation_access="NONE",
            resume_template_tier="starter",
            github_integration="NONE",
            compete_access="preview",
            coming_soon_features=list(COMING_SOON_FEATURES),
        ),
    ),
    PlanTier.BASIC: PlanConfiguration(
        plan_code=PlanTier.BASIC,
        name="Basic Plan",
        price=149.0,
        currency="INR",
        gst_included=True,
        duration_days=30,
        description="Complete academic learning, project building, and career preparation.",
        features=[
            "500 AI Credits / 30 days (300 Learn · 125 Build · 75 Launch)",
            "Weekly (₹49), Monthly (₹149), & Semester (₹599) passes · GST included",
            "Advanced AI Subject Tutor & full syllabus PDF analysis",
            "Complete personalized roadmaps & Exam Preparation Mode",
            "5 Mock Tests / month & 50 practice questions / day",
            "Full project roadmaps, Code Assistant & limited debugging",
            "Complete resume builder (standard templates) & 5 ATS scans / month",
            "2 AI Mock Interviews / month (Coming Soon) · Basic GitHub Integration (Coming Soon)",
        ],
        coming_soon_features=list(COMING_SOON_FEATURES),
        cycles=[
            _to_cycle_option(SKU_CATALOG[(PlanTier.BASIC, BillingCycle.WEEKLY)]),
            _to_cycle_option(SKU_CATALOG[(PlanTier.BASIC, BillingCycle.MONTHLY)]),
            _to_cycle_option(SKU_CATALOG[(PlanTier.BASIC, BillingCycle.SEMESTER)]),
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
            ats_checks=5,
            ats_checks_period="monthly",
            mock_tests=5,
            mock_tests_period="monthly",
            mock_interviews=2,
            mock_interviews_period="monthly",
            monthly_credits=500,
            module_credits={"LEARN": 300, "BUILD": 125, "LAUNCH": 75},
            project_tracking_included=True,
            ai_project_guidance=10,
            debugging_access="LIMITED",
            project_evaluation_access="STANDARD",
            resume_template_tier="standard",
            github_integration="BASIC",
            compete_access="full",
            coming_soon_features=list(COMING_SOON_FEATURES),
        ),
    ),
    PlanTier.PRO: PlanConfiguration(
        plan_code=PlanTier.PRO,
        name="Pro Plan",
        price=299.0,
        currency="INR",
        gst_included=True,
        duration_days=30,
        description="Advanced AI intelligence (LIE & PDE), deeper personalization, and maximum allowances.",
        features=[
            "1,500 AI Credits / 30 days (900 Learn · 375 Build · 225 Launch)",
            "Weekly (₹99), Monthly (₹299), & Semester (₹1,199) passes · GST included",
            "Pro-Exclusive LIE & PDE adaptive depth + Unified Student Intelligence Profile",
            "20 Mock Tests / month & predictive weakness identification",
            "Advanced AI Project Mentor, debugging & project milestone evaluation",
            "Advanced resume optimization (premium templates) & 20 ATS scans / month",
            "10 AI Mock Interviews / month (Coming Soon) · Extended GitHub Integration (Coming Soon)",
        ],
        coming_soon_features=list(COMING_SOON_FEATURES),
        cycles=[
            _to_cycle_option(SKU_CATALOG[(PlanTier.PRO, BillingCycle.WEEKLY)]),
            _to_cycle_option(SKU_CATALOG[(PlanTier.PRO, BillingCycle.MONTHLY)]),
            _to_cycle_option(SKU_CATALOG[(PlanTier.PRO, BillingCycle.SEMESTER)]),
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
            ats_checks=20,
            ats_checks_period="monthly",
            mock_tests=20,
            mock_tests_period="monthly",
            mock_interviews=10,
            mock_interviews_period="monthly",
            monthly_credits=1500,
            module_credits={"LEARN": 900, "BUILD": 375, "LAUNCH": 225},
            project_tracking_included=True,
            ai_project_guidance=50,
            debugging_access="ADVANCED",
            project_evaluation_access="ADVANCED",
            resume_template_tier="premium",
            github_integration="EXTENDED",
            compete_access="full",
            coming_soon_features=list(COMING_SOON_FEATURES),
        ),
    ),
}


def get_sku(plan_code: PlanTier, billing_cycle: BillingCycle = BillingCycle.MONTHLY) -> SKUConfig:
    sku = SKU_CATALOG.get((plan_code, billing_cycle))
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported plan/cycle combination: {plan_code.value}/{billing_cycle.value}",
        )
    return sku


def _parse_dt(val: Any) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, datetime):
        dt = val
    else:
        dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class BillingService:
    """
    Core business logic service for subscriptions, hybrid credit pools,
    prorated upgrades, manual renewals, checkout session management, and order lifecycle.
    """

    @staticmethod
    def get_plans() -> PlansResponse:
        """Returns the server-defined pricing, cycles (GST included), and quota configurations."""
        return PlansResponse(plans=list(PLAN_CATALOG.values()))

    @staticmethod
    def _get_next_reset_times() -> tuple[datetime, datetime]:
        """Calculates next daily (00:00 IST) and monthly (1st of month 00:00 IST) reset times."""
        now_ist = datetime.now(IST)
        tomorrow_ist = (now_ist + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        next_daily = tomorrow_ist.astimezone(timezone.utc)

        if now_ist.month == 12:
            next_month = now_ist.replace(year=now_ist.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now_ist.replace(month=now_ist.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        next_monthly = next_month.astimezone(timezone.utc)
        return next_daily, next_monthly

    @staticmethod
    def compute_proration_credit(
        paid_amount: float,
        paid_duration_days: int,
        period_end: Optional[datetime],
        now_utc: Optional[datetime] = None,
    ) -> tuple[float, int]:
        """
        Simple monetary proration:
        credit = round((paid_amount / paid_duration_days) * remaining_days, 2)
        """
        now = now_utc or datetime.now(timezone.utc)
        if not period_end or period_end <= now or paid_amount <= 0 or paid_duration_days <= 0:
            return 0.0, 0
        remaining_days = max(0, (period_end - now).days)
        if remaining_days <= 0:
            return 0.0, 0
        credit = round((float(paid_amount) / float(paid_duration_days)) * remaining_days, 2)
        return credit, remaining_days

    def _safe_fetch_entitlement_row(self, learner_id: str) -> Optional[Dict[str, Any]]:
        try:
            res = (
                supabase_admin.table("billing_entitlements")
                .select("*")
                .eq("learner_id", learner_id)
                .execute()
            )
            if isinstance(getattr(res, "data", None), list) and res.data:
                row = res.data[0]
                if isinstance(row, dict) and row.get("current_plan"):
                    return row
        except Exception:
            pass
        return None

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
            new_entitlement = {
                "learner_id": learner_id,
                "current_plan": PlanTier.FREE.value,
                "billing_cycle": BillingCycle.MONTHLY.value,
                "status": EntitlementStatus.ACTIVE.value,
                "source": SubscriptionSource.FREE_DEFAULT.value,
                "trial_used": False,
                "paid_amount": 0.0,
                "paid_duration_days": 0,
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

        current_plan = PlanTier(row["current_plan"])
        billing_cycle = BillingCycle(row.get("billing_cycle") or BillingCycle.MONTHLY.value)
        ent_status = EntitlementStatus(row["status"])
        source = SubscriptionSource(
            row.get("source")
            or (SubscriptionSource.TRIAL.value if ent_status == EntitlementStatus.TRIAL else (
                SubscriptionSource.PAYMENT.value if current_plan != PlanTier.FREE else SubscriptionSource.FREE_DEFAULT.value
            ))
        )
        trial_used = bool(row["trial_used"])
        last_expired_plan = PlanTier(row["last_expired_plan"]) if row.get("last_expired_plan") else None
        period_end = _parse_dt(row.get("current_period_end"))

        if period_end and period_end < now_utc and ent_status in (EntitlementStatus.ACTIVE, EntitlementStatus.TRIAL) and current_plan != PlanTier.FREE:
            logger.info(f"Entitlement expired for learner {learner_id}. Reverting to FREE tier.")
            last_expired_plan = current_plan
            update_res = (
                supabase_admin.table("billing_entitlements")
                .update({
                    "current_plan": PlanTier.FREE.value,
                    "billing_cycle": BillingCycle.MONTHLY.value,
                    "status": EntitlementStatus.EXPIRED.value,
                    "source": SubscriptionSource.FREE_DEFAULT.value,
                    "paid_amount": 0.0,
                    "paid_duration_days": 0,
                    "last_expired_plan": current_plan.value,
                    "updated_at": now_utc.isoformat(),
                })
                .eq("learner_id", learner_id)
                .execute()
            )
            row = update_res.data[0]
            current_plan = PlanTier.FREE
            billing_cycle = BillingCycle.MONTHLY
            ent_status = EntitlementStatus.EXPIRED
            source = SubscriptionSource.FREE_DEFAULT

        sku = get_sku(current_plan, billing_cycle)
        paid_amount = float(row.get("paid_amount") or 0.0)
        if paid_amount == 0.0 and source == SubscriptionSource.PAYMENT and current_plan != PlanTier.FREE:
            paid_amount = sku.price

        is_active = ent_status == EntitlementStatus.ACTIVE
        is_trial = ent_status == EntitlementStatus.TRIAL

        days_remaining = None
        if period_end and period_end > now_utc:
            days_remaining = max(0, (period_end - now_utc).days)

        start_dt = _parse_dt(row.get("current_period_start"))
        updated_dt = _parse_dt(row.get("updated_at"))

        # Check usage cycle info if available (best-effort)
        credit_cycle_index = 1
        credit_cycle_end = None
        try:
            u_res = supabase_admin.table("billing_usage_quotas").select("credit_cycle_index, cycle_end").eq("learner_id", learner_id).execute()
            if isinstance(getattr(u_res, "data", None), list) and u_res.data and isinstance(u_res.data[0], dict):
                credit_cycle_index = int(u_res.data[0].get("credit_cycle_index") or 1)
                credit_cycle_end = _parse_dt(u_res.data[0].get("cycle_end"))
        except Exception:
            pass

        return EntitlementResponse(
            learner_id=learner_id,
            current_plan=current_plan,
            billing_cycle=billing_cycle,
            status=ent_status,
            source=source,
            trial_used=trial_used,
            current_period_start=start_dt,
            current_period_end=period_end,
            is_active=is_active or is_trial,
            is_trial=is_trial,
            days_remaining=days_remaining,
            paid_amount=paid_amount,
            renewal_policy=sku.renewal_policy,
            last_expired_plan=last_expired_plan,
            credit_cycle_index=credit_cycle_index,
            credit_cycle_end=credit_cycle_end,
            updated_at=updated_dt,
        )

    def _apply_lazy_resets(
        self,
        learner_id: str,
        row: Dict[str, Any],
        entitlement: EntitlementResponse,
        now_utc: datetime,
    ) -> Dict[str, Any]:
        """Applies daily (00:00 IST) and 30-day rolling / Semester credit resets if due."""
        next_daily, _ = self._get_next_reset_times()
        updates: Dict[str, Any] = {}

        daily_reset_at = _parse_dt(row.get("daily_reset_at"))
        if daily_reset_at and now_utc >= daily_reset_at:
            updates["ai_tutor_requests"] = 0
            updates["practice_questions"] = 0
            updates["daily_reset_at"] = next_daily.isoformat()

        cycle_end = _parse_dt(row.get("cycle_end"))
        if cycle_end and now_utc >= cycle_end:
            # Semester 30-day refresh or Free/Monthly 30-day rolling refresh
            if entitlement.current_period_end and entitlement.current_period_end > now_utc:
                new_cycle_end = min(now_utc + timedelta(days=30), entitlement.current_period_end)
            else:
                new_cycle_end = now_utc + timedelta(days=30)

            updates.update({
                "period_start": now_utc.isoformat(),
                "cycle_start": now_utc.isoformat(),
                "cycle_end": new_cycle_end.isoformat(),
                "credit_cycle_index": int(row.get("credit_cycle_index") or 1) + 1 if entitlement.billing_cycle == BillingCycle.SEMESTER else 1,
                "learn_credits_used": 0,
                "build_credits_used": 0,
                "launch_credits_used": 0,
                "mock_tests_used": 0,
                "mock_interviews_used": 0,
                "ai_roadmap_generations": 0,
                "resume_generations": 0,
                "ats_checks": 0,
                "ai_project_guidance": 0,
            })

        if updates:
            updates["updated_at"] = now_utc.isoformat()
            try:
                upd_res = (
                    supabase_admin.table("billing_usage_quotas")
                    .update(updates)
                    .eq("learner_id", learner_id)
                    .execute()
                )
                if isinstance(getattr(upd_res, "data", None), list) and upd_res.data:
                    return upd_res.data[0]
            except Exception as exc:
                logger.warning(f"Failed lazy quota reset for {learner_id}: {exc}")
            merged = dict(row)
            merged.update(updates)
            return merged
        return row

    def get_or_create_usage(self, learner_id: str) -> UsageResponse:
        """
        Fetches current usage cycle limits, hybrid module credit balances, and consumed quantities.
        Applies due daily (00:00 IST) and 30-day / Semester cycle resets.
        """
        entitlement = self.get_or_create_entitlement(learner_id)
        plan_config = PLAN_CATALOG.get(entitlement.current_plan, PLAN_CATALOG[PlanTier.FREE])
        quotas_def = plan_config.quotas
        sku = get_sku(entitlement.current_plan, entitlement.billing_cycle)

        res = (
            supabase_admin.table("billing_usage_quotas")
            .select("*")
            .eq("learner_id", learner_id)
            .execute()
        )
        now_utc = datetime.now(timezone.utc)
        next_daily, next_monthly = self._get_next_reset_times()

        if not res.data:
            cycle_days = 7 if entitlement.billing_cycle == BillingCycle.WEEKLY else 30
            new_usage = {
                "learner_id": learner_id,
                "period_start": now_utc.isoformat(),
                "cycle_start": now_utc.isoformat(),
                "cycle_end": (now_utc + timedelta(days=cycle_days)).isoformat(),
                "daily_reset_at": next_daily.isoformat(),
                "credit_cycle_index": 1,
                "learn_credits_used": 0,
                "build_credits_used": 0,
                "launch_credits_used": 0,
                "mock_tests_used": 0,
                "mock_interviews_used": 0,
                "ai_roadmap_generations": 0,
                "ai_tutor_requests": 0,
                "practice_questions": 0,
                "resume_generations": 0,
                "ats_checks": 0,
                "ai_project_guidance": 0,
                "updated_at": now_utc.isoformat(),
            }
            insert_res = (
                supabase_admin.table("billing_usage_quotas")
                .insert(new_usage)
                .execute()
            )
            row = insert_res.data[0]
        else:
            row = self._apply_lazy_resets(learner_id, res.data[0], entitlement, now_utc)

        used_roadmaps = int(row.get("ai_roadmap_generations") or 0)
        used_tutor = int(row.get("ai_tutor_requests") or 0)
        used_questions = int(row.get("practice_questions") or 0)
        used_resumes = int(row.get("resume_generations") or 0)
        used_ats = int(row.get("ats_checks") or 0)
        used_mock_tests = int(row.get("mock_tests_used") or 0)
        used_mock_interviews = int(row.get("mock_interviews_used") or 0)
        used_guidance = int(row.get("ai_project_guidance") or 0)

        learn_used = int(row.get("learn_credits_used") or 0)
        build_used = int(row.get("build_credits_used") or 0)
        launch_used = int(row.get("launch_credits_used") or 0)
        total_used = learn_used + build_used + launch_used

        learn_limit = sku.module_credits["LEARN"]
        build_limit = sku.module_credits["BUILD"]
        launch_limit = sku.module_credits["LAUNCH"]

        period_start = _parse_dt(row.get("period_start"))
        cycle_start = _parse_dt(row.get("cycle_start")) or period_start
        cycle_end = _parse_dt(row.get("cycle_end")) or next_monthly
        updated_dt = _parse_dt(row.get("updated_at"))

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
                    limit=sku.ats_checks,
                    remaining=max(0, sku.ats_checks - used_ats),
                    period=quotas_def.ats_checks_period,
                ),
                "mockTests": QuotaUsageDetail(
                    used=used_mock_tests,
                    limit=sku.mock_tests,
                    remaining=max(0, sku.mock_tests - used_mock_tests),
                    period="monthly",
                ),
                "mockInterviews": QuotaUsageDetail(
                    used=used_mock_interviews,
                    limit=sku.mock_interviews,
                    remaining=max(0, sku.mock_interviews - used_mock_interviews),
                    period="monthly",
                ),
                "aiProjectGuidance": QuotaUsageDetail(
                    used=used_guidance,
                    limit=quotas_def.ai_project_guidance,
                    remaining=max(0, quotas_def.ai_project_guidance - used_guidance),
                    period="monthly",
                ),
            },
            credits=CreditSummary(
                total_used=total_used,
                total_limit=sku.total_credits,
                total_remaining=max(0, sku.total_credits - total_used),
                cycle_start=cycle_start,
                cycle_end=cycle_end,
                modules={
                    "LEARN": ModuleCreditDetail(
                        used=learn_used,
                        limit=learn_limit,
                        remaining=max(0, learn_limit - learn_used),
                    ),
                    "BUILD": ModuleCreditDetail(
                        used=build_used,
                        limit=build_limit,
                        remaining=max(0, build_limit - build_used),
                    ),
                    "LAUNCH": ModuleCreditDetail(
                        used=launch_used,
                        limit=launch_limit,
                        remaining=max(0, launch_limit - launch_used),
                    ),
                },
            ),
            next_reset_daily=next_daily,
            next_reset_monthly=next_monthly,
            updated_at=updated_dt,
        )

    def activate_trial(self, learner_id: str) -> TrialActivationResponse:
        """Activates a 72-hour Basic plan trial. Allowed strictly once per verified account."""
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
        next_daily, _ = self._get_next_reset_times()

        supabase_admin.table("billing_entitlements").update({
            "current_plan": PlanTier.BASIC.value,
            "billing_cycle": BillingCycle.WEEKLY.value,
            "status": EntitlementStatus.TRIAL.value,
            "source": SubscriptionSource.TRIAL.value,
            "trial_used": True,
            "paid_amount": 0.0,
            "paid_duration_days": 0,
            "current_period_start": now_utc.isoformat(),
            "current_period_end": trial_end_utc.isoformat(),
            "updated_at": now_utc.isoformat(),
        }).eq("learner_id", learner_id).execute()

        supabase_admin.table("billing_usage_quotas").update({
            "period_start": now_utc.isoformat(),
            "cycle_start": now_utc.isoformat(),
            "cycle_end": trial_end_utc.isoformat(),
            "daily_reset_at": next_daily.isoformat(),
            "credit_cycle_index": 1,
            "learn_credits_used": 0,
            "build_credits_used": 0,
            "launch_credits_used": 0,
            "mock_tests_used": 0,
            "mock_interviews_used": 0,
            "ai_roadmap_generations": 0,
            "ai_tutor_requests": 0,
            "practice_questions": 0,
            "resume_generations": 0,
            "ats_checks": 0,
            "ai_project_guidance": 0,
            "updated_at": now_utc.isoformat(),
        }).eq("learner_id", learner_id).execute()

        refreshed_entitlement = self.get_or_create_entitlement(learner_id)

        return TrialActivationResponse(
            success=True,
            message="72-hour Basic trial activated successfully.",
            entitlement=refreshed_entitlement,
        )

    def _evaluate_checkout_plan(
        self,
        learner_id: str,
        target_plan: PlanTier,
        target_cycle: BillingCycle,
    ) -> CheckoutPreviewResponse:
        """Computes action type (NEW/RENEW/UPGRADE), monetary proration credit, and payable amount."""
        if target_plan == PlanTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free plan cannot be checked out via payment gateway.",
            )

        target_sku = get_sku(target_plan, target_cycle)
        now_utc = datetime.now(timezone.utc)
        ent_row = self._safe_fetch_entitlement_row(learner_id)

        action_type = "NEW"
        prorated_credit = 0.0
        remaining_days_credited = 0
        allowed = True
        block_reason: Optional[str] = None
        new_period_start = now_utc
        new_period_end = now_utc + timedelta(days=target_sku.duration_days)

        if ent_row:
            curr_plan = PlanTier(ent_row["current_plan"])
            curr_cycle = BillingCycle(ent_row.get("billing_cycle") or BillingCycle.MONTHLY.value)
            curr_status = EntitlementStatus(ent_row["status"])
            curr_source = SubscriptionSource(
                ent_row.get("source")
                or (SubscriptionSource.TRIAL.value if curr_status == EntitlementStatus.TRIAL else (
                    SubscriptionSource.PAYMENT.value if curr_plan != PlanTier.FREE else SubscriptionSource.FREE_DEFAULT.value
                ))
            )
            curr_end = _parse_dt(ent_row.get("current_period_end"))

            if curr_plan != PlanTier.FREE and curr_status == EntitlementStatus.ACTIVE and curr_end and curr_end > now_utc:
                if _TIER_RANK[target_plan] < _TIER_RANK[curr_plan]:
                    allowed = False
                    block_reason = (
                        f"You already have an active {curr_plan.value} subscription until "
                        f"{curr_end.date().isoformat()}. Downgrade is not allowed while active."
                    )
                elif target_plan == curr_plan and target_cycle == curr_cycle:
                    action_type = "RENEW"
                    new_period_start = _parse_dt(ent_row.get("current_period_start")) or now_utc
                    new_period_end = curr_end + timedelta(days=target_sku.duration_days)
                elif target_plan == curr_plan and _CYCLE_RANK[target_cycle] < _CYCLE_RANK[curr_cycle]:
                    allowed = False
                    block_reason = (
                        f"You already have a longer {curr_cycle.value} {curr_plan.value} pass active until "
                        f"{curr_end.date().isoformat()}."
                    )
                else:
                    # Tier upgrade (BASIC -> PRO) or cycle upgrade (WEEKLY -> MONTHLY/SEMESTER)
                    action_type = "UPGRADE"
                    if curr_source == SubscriptionSource.PAYMENT:
                        curr_paid_amount = float(ent_row.get("paid_amount") or 0.0)
                        curr_paid_days = int(ent_row.get("paid_duration_days") or 0)
                        if curr_paid_amount <= 0.0 or curr_paid_days <= 0:
                            curr_sku = get_sku(curr_plan, curr_cycle)
                            curr_paid_amount = curr_sku.price
                            curr_paid_days = curr_sku.duration_days
                        prorated_credit, remaining_days_credited = self.compute_proration_credit(
                            curr_paid_amount, curr_paid_days, curr_end, now_utc
                        )
                    new_period_start = now_utc
                    new_period_end = now_utc + timedelta(days=target_sku.duration_days)

        capped_credit = min(prorated_credit, max(0.0, target_sku.price - 1.0))
        payable_amount = max(1.0, round(target_sku.price - capped_credit, 2))

        return CheckoutPreviewResponse(
            plan_code=target_plan,
            billing_cycle=target_cycle,
            action_type=action_type,
            sku_price=target_sku.price,
            prorated_credit=round(capped_credit, 2),
            remaining_days_credited=remaining_days_credited,
            payable_amount=payable_amount,
            currency="INR",
            gst_included=True,
            new_period_start=new_period_start,
            new_period_end=new_period_end,
            allowed=allowed,
            block_reason=block_reason,
        )

    def preview_checkout(
        self,
        learner_id: str,
        plan_code: PlanTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
    ) -> CheckoutPreviewResponse:
        return self._evaluate_checkout_plan(learner_id, plan_code, billing_cycle)

    async def create_checkout(
        self,
        learner_id: str,
        user_email: str,
        plan_code: PlanTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        custom_return_url: Optional[str] = None,
        user_phone: Optional[str] = None,
    ) -> CheckoutResponse:
        """
        Initiates order checkout. Price & proration are determined strictly server-side.
        Creates pending billing order in DB and requests Cashfree session ID.
        """
        preview = self._evaluate_checkout_plan(learner_id, plan_code, billing_cycle)
        if not preview.allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=preview.block_reason or "Selected plan change is not allowed while current plan is active.",
            )

        if custom_return_url:
            validated_base_return = validate_redirect_url(custom_return_url, default_path="/billing/return")
        else:
            validated_base_return = settings.CASHFREE_RETURN_URL

        sku = get_sku(plan_code, billing_cycle)
        order_id = f"unios_ord_{uuid.uuid4().hex[:16]}"
        now_utc = datetime.now(timezone.utc)

        order_record = {
            "order_id": order_id,
            "learner_id": learner_id,
            "plan_code": plan_code.value,
            "billing_cycle": billing_cycle.value,
            "order_type": preview.action_type,
            "sku_price": preview.sku_price,
            "proration_credit": preview.prorated_credit,
            "amount": preview.payable_amount,
            "currency": "INR",
            "status": OrderStatus.PENDING.value,
            "created_at": now_utc.isoformat(),
            "updated_at": now_utc.isoformat(),
        }

        supabase_admin.table("billing_orders").insert(order_record).execute()

        if "{order_id}" in validated_base_return:
            return_url = validated_base_return.replace("{order_id}", order_id)
        elif "order_id=" in validated_base_return:
            return_url = validated_base_return
        else:
            separator = "&" if "?" in validated_base_return else "?"
            return_url = f"{validated_base_return}{separator}order_id={order_id}"

        customer_details = {
            "customer_id": learner_id,
            "customer_email": user_email,
            "customer_phone": user_phone or "9999999999",
        }

        cf_response = await cashfree_gateway.create_order(
            order_id=order_id,
            amount=preview.payable_amount,
            customer_details=customer_details,
            return_url=return_url,
            order_note=f"UniOS {plan_code.value} {billing_cycle.value} ({sku.duration_days}-day access, GST included)",
        )

        payment_session_id = cf_response.get("payment_session_id", "")

        supabase_admin.table("billing_orders").update({
            "payment_session_id": payment_session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("order_id", order_id).execute()

        return CheckoutResponse(
            order_id=order_id,
            payment_session_id=payment_session_id,
            environment=cashfree_gateway.env,
            amount=preview.payable_amount,
            currency="INR",
            plan_code=plan_code,
            billing_cycle=billing_cycle,
            sku_price=preview.sku_price,
            prorated_credit=preview.prorated_credit,
            gst_included=True,
            action_type=preview.action_type,
        )

    def _claim_order(self, order_id: str, cashfree_payment_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Attempts atomic RPC order claim first; falls back gracefully for legacy/mocked DB."""
        try:
            rpc_res = supabase_admin.rpc(
                "claim_billing_order_for_fulfillment",
                {"p_order_id": order_id, "p_payment_id": cashfree_payment_id},
            ).execute()
            if isinstance(getattr(rpc_res, "data", None), list):
                if not rpc_res.data:
                    return None
                return rpc_res.data[0]
        except Exception:
            pass

        res = (
            supabase_admin.table("billing_orders")
            .select("*")
            .eq("order_id", order_id)
            .execute()
        )
        if not res.data:
            return None
        order = res.data[0]
        if order.get("status") == OrderStatus.SUCCESS.value:
            return None

        supabase_admin.table("billing_orders").update({
            "status": OrderStatus.SUCCESS.value,
            "cashfree_payment_id": cashfree_payment_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("order_id", order_id).execute()
        return order

    def process_successful_payment(
        self,
        order_id: str,
        cashfree_payment_id: Optional[str] = None,
    ) -> None:
        """
        Idempotent payment confirmation.
        Claims order atomically, grants Weekly/Monthly/Semester validity, and resets usage quotas.
        """
        order = self._claim_order(order_id, cashfree_payment_id)
        if not order:
            logger.info(f"Payment process skipped for order '{order_id}' (missing or already SUCCESS).")
            return

        now_utc = datetime.now(timezone.utc)
        learner_id = order["learner_id"]
        plan_code = PlanTier(order["plan_code"])
        billing_cycle = BillingCycle(order.get("billing_cycle") or BillingCycle.MONTHLY.value)
        order_type = str(order.get("order_type") or "NEW").upper()
        sku = get_sku(plan_code, billing_cycle)
        next_daily, _ = self._get_next_reset_times()

        ent_row = self._safe_fetch_entitlement_row(learner_id)
        existing_end = None
        if ent_row and ent_row.get("current_period_end"):
            parsed_end = _parse_dt(ent_row["current_period_end"])
            if parsed_end and parsed_end > now_utc:
                existing_end = parsed_end

        if order_type == "UPGRADE":
            period_start = now_utc
            period_end = now_utc + timedelta(days=sku.duration_days)
        elif ent_row and ent_row.get("current_plan") == plan_code.value and (
            ent_row.get("billing_cycle") in (None, billing_cycle.value)
        ) and existing_end:
            period_start = _parse_dt(ent_row.get("current_period_start")) or now_utc
            period_end = existing_end + timedelta(days=sku.duration_days)
        else:
            period_start = now_utc
            period_end = now_utc + timedelta(days=sku.duration_days)

        # Preserve full SKU value for downstream proration if user upgrades again
        paid_value = float(order.get("sku_price") or order.get("amount") or sku.price)

        supabase_admin.table("billing_entitlements").upsert({
            "learner_id": learner_id,
            "current_plan": plan_code.value,
            "billing_cycle": billing_cycle.value,
            "status": EntitlementStatus.ACTIVE.value,
            "source": SubscriptionSource.PAYMENT.value,
            "paid_amount": paid_value,
            "paid_duration_days": sku.duration_days,
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        # Reset quotas cleanly for new cycle (or start 30-day cycle for Semester/Monthly, 7d for Weekly)
        cycle_window_days = 7 if billing_cycle == BillingCycle.WEEKLY else 30
        cycle_end = min(now_utc + timedelta(days=cycle_window_days), period_end)

        supabase_admin.table("billing_usage_quotas").upsert({
            "learner_id": learner_id,
            "period_start": now_utc.isoformat(),
            "cycle_start": now_utc.isoformat(),
            "cycle_end": cycle_end.isoformat(),
            "daily_reset_at": next_daily.isoformat(),
            "credit_cycle_index": 1,
            "learn_credits_used": 0,
            "build_credits_used": 0,
            "launch_credits_used": 0,
            "mock_tests_used": 0,
            "mock_interviews_used": 0,
            "ai_roadmap_generations": 0,
            "ai_tutor_requests": 0,
            "practice_questions": 0,
            "resume_generations": 0,
            "ats_checks": 0,
            "ai_project_guidance": 0,
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        logger.info(
            f"Successfully processed payment for order {order_id}. "
            f"Plan {plan_code.value}/{billing_cycle.value} granted to learner {learner_id} until {period_end.isoformat()}."
        )

    async def poll_and_verify_order(
        self,
        order_id: str,
        learner_id: str,
    ) -> PaymentStatusResponse:
        """
        Polls payment status server-side from Cashfree, validates amount/currency,
        and applies entitlement if confirmed PAID.
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

        order_cycle = BillingCycle(order.get("billing_cycle") or BillingCycle.MONTHLY.value)

        if order.get("status") == OrderStatus.SUCCESS.value:
            return PaymentStatusResponse(
                order_id=order_id,
                status=OrderStatus.SUCCESS,
                plan_code=PlanTier(order["plan_code"]),
                billing_cycle=order_cycle,
                amount=float(order["amount"]),
                currency=order.get("currency", "INR"),
                gst_included=True,
                cashfree_payment_id=order.get("cashfree_payment_id"),
                created_at=_parse_dt(order.get("created_at")),
                updated_at=_parse_dt(order.get("updated_at")),
            )

        cf_status_data = await cashfree_gateway.verify_payment(order_id)
        cf_order_status = cf_status_data.get("order_status")
        cf_amount = cf_status_data.get("order_amount")
        cf_currency = cf_status_data.get("order_currency", "INR")

        if cf_order_status == "PAID":
            if cf_amount is not None and abs(float(cf_amount) - float(order["amount"])) > 0.01:
                logger.error(
                    f"Order amount mismatch for {order_id}: expected {order['amount']}, got {cf_amount}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment amount mismatch detected during verification.",
                )
            if cf_currency and cf_currency.upper() != str(order.get("currency", "INR")).upper():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment currency mismatch detected during verification.",
                )
            cf_payment_id = cf_status_data.get("cf_payment_id")
            self.process_successful_payment(order_id, cashfree_payment_id=cf_payment_id)
            return PaymentStatusResponse(
                order_id=order_id,
                status=OrderStatus.SUCCESS,
                plan_code=PlanTier(order["plan_code"]),
                billing_cycle=order_cycle,
                amount=float(order["amount"]),
                currency=order.get("currency", "INR"),
                gst_included=True,
                cashfree_payment_id=cf_payment_id,
                created_at=_parse_dt(order.get("created_at")),
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
            billing_cycle=order_cycle,
            amount=float(order["amount"]),
            currency=order.get("currency", "INR"),
            gst_included=True,
            cashfree_payment_id=order.get("cashfree_payment_id"),
            created_at=_parse_dt(order.get("created_at")),
            updated_at=_parse_dt(order.get("updated_at")),
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
                    billing_cycle=BillingCycle(row.get("billing_cycle") or BillingCycle.MONTHLY.value),
                    order_type=row.get("order_type") or "NEW",
                    sku_price=float(row["sku_price"]) if row.get("sku_price") is not None else None,
                    proration_credit=float(row.get("proration_credit") or 0.0),
                    amount=float(row["amount"]),
                    currency=row.get("currency", "INR"),
                    gst_included=True,
                    status=OrderStatus(row["status"]),
                    cashfree_payment_id=row.get("cashfree_payment_id"),
                    created_at=_parse_dt(row.get("created_at")),
                    updated_at=_parse_dt(row.get("updated_at")),
                )
            )

        return OrderHistoryResponse(orders=items, total=len(items))

    def get_credit_ledger(self, learner_id: str, limit: int = 50) -> CreditLedgerResponse:
        """Retrieves recent credit ledger transactions for the learner."""
        res = (
            supabase_admin.table("billing_credit_ledger")
            .select("*")
            .eq("learner_id", learner_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        entries: List[CreditLedgerItem] = []
        for row in res.data or []:
            entries.append(
                CreditLedgerItem(
                    id=str(row["id"]),
                    module=row["module"],
                    operation=row["operation"],
                    credits_delta=int(row["credits_delta"]),
                    status=row.get("status", "COMMITTED"),
                    reference_id=row.get("reference_id"),
                    created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
                )
            )
        return CreditLedgerResponse(entries=entries, total=len(entries))

    def admin_assign_subscription(
        self,
        admin_user_id: str,
        payload: AdminAssignSubscriptionRequest,
    ) -> AdminAssignSubscriptionResponse:
        """Allows administrators to assign promotional or institutional subscriptions."""
        sku = get_sku(payload.plan_code, payload.billing_cycle)
        duration_days = payload.duration_days or (sku.duration_days if sku.duration_days > 0 else 30)
        now_utc = datetime.now(timezone.utc)
        period_end = None if payload.plan_code == PlanTier.FREE else (now_utc + timedelta(days=duration_days))
        source = (
            SubscriptionSource.INSTITUTIONAL
            if payload.grant_type.upper() == "INSTITUTIONAL"
            else SubscriptionSource.ADMIN_PROMO
        )
        next_daily, _ = self._get_next_reset_times()

        supabase_admin.table("billing_entitlements").upsert({
            "learner_id": payload.learner_id,
            "current_plan": payload.plan_code.value,
            "billing_cycle": payload.billing_cycle.value,
            "status": EntitlementStatus.ACTIVE.value,
            "source": source.value,
            "paid_amount": 0.0,
            "paid_duration_days": 0,
            "assigned_by_admin_id": admin_user_id,
            "admin_note": payload.note,
            "current_period_start": now_utc.isoformat(),
            "current_period_end": period_end.isoformat() if period_end else None,
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        cycle_window_days = 7 if payload.billing_cycle == BillingCycle.WEEKLY else 30
        cycle_end = min(now_utc + timedelta(days=cycle_window_days), period_end) if period_end else (now_utc + timedelta(days=30))

        supabase_admin.table("billing_usage_quotas").upsert({
            "learner_id": payload.learner_id,
            "period_start": now_utc.isoformat(),
            "cycle_start": now_utc.isoformat(),
            "cycle_end": cycle_end.isoformat(),
            "daily_reset_at": next_daily.isoformat(),
            "credit_cycle_index": 1,
            "learn_credits_used": 0,
            "build_credits_used": 0,
            "launch_credits_used": 0,
            "mock_tests_used": 0,
            "mock_interviews_used": 0,
            "ai_roadmap_generations": 0,
            "ai_tutor_requests": 0,
            "practice_questions": 0,
            "resume_generations": 0,
            "ats_checks": 0,
            "ai_project_guidance": 0,
            "updated_at": now_utc.isoformat(),
        }, on_conflict="learner_id").execute()

        supabase_admin.table("billing_admin_grants").insert({
            "learner_id": payload.learner_id,
            "admin_user_id": admin_user_id,
            "plan_code": payload.plan_code.value,
            "billing_cycle": payload.billing_cycle.value,
            "duration_days": duration_days,
            "grant_type": source.value,
            "note": payload.note,
        }).execute()

        entitlement = self.get_or_create_entitlement(payload.learner_id)
        return AdminAssignSubscriptionResponse(
            success=True,
            message=f"Assigned {payload.plan_code.value} ({payload.billing_cycle.value}) for {duration_days} days.",
            entitlement=entitlement,
        )


billing_service = BillingService()

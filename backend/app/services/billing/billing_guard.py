from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Optional
from fastapi import HTTPException, status

from app.core.supabase import supabase_admin
from app.schemas.billing import CreditOperation, ModuleType, PlanTier
from app.services.billing.billing_service import billing_service, get_sku

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OperationSpec:
    module: ModuleType
    credits: int
    feature_col: Optional[str] = None
    legacy_col: Optional[str] = None


OPERATION_SPECS: dict[CreditOperation, OperationSpec] = {
    CreditOperation.SIMPLE_AI_QUESTION: OperationSpec(ModuleType.LEARN, 1, "ai_tutor_requests", "ai_tutor_requests"),
    CreditOperation.DETAILED_EXPLANATION: OperationSpec(ModuleType.LEARN, 2, "ai_tutor_requests", "ai_tutor_requests"),
    CreditOperation.AI_NOTES_GENERATION: OperationSpec(ModuleType.LEARN, 3),
    CreditOperation.ASSESSMENT_GENERATION: OperationSpec(ModuleType.LEARN, 3, "mock_tests_used"),
    CreditOperation.SYLLABUS_ANALYSIS: OperationSpec(ModuleType.LEARN, 5),
    CreditOperation.COMPLETE_ROADMAP_GENERATION: OperationSpec(ModuleType.LEARN, 5, legacy_col="ai_roadmap_generations"),
    CreditOperation.ADVANCED_PROJECT_GUIDANCE: OperationSpec(ModuleType.BUILD, 5, legacy_col="ai_project_guidance"),
    CreditOperation.ADVANCED_DEBUGGING: OperationSpec(ModuleType.BUILD, 5, legacy_col="ai_project_guidance"),
    CreditOperation.CAREER_ANALYSIS: OperationSpec(ModuleType.LAUNCH, 4),
    CreditOperation.RESUME_OPTIMIZATION: OperationSpec(ModuleType.LAUNCH, 3, legacy_col="resume_generations"),
    CreditOperation.ATS_SCAN: OperationSpec(ModuleType.LAUNCH, 0, "ats_checks", "ats_checks"),
    CreditOperation.INTERVIEW_SIMULATION: OperationSpec(ModuleType.LAUNCH, 5, "mock_interviews_used"),
}


class BillingGuardService:
    """Centralized credit, monthly cap, capability gating, and error-refund service."""

    @staticmethod
    def _raise_quota_exceeded(message: str, module: str, required_plan: str = "BASIC") -> None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": message,
                "module": module,
                "requiredPlan": required_plan,
                "upgradeUrl": "/billing",
            },
        )

    @staticmethod
    def _raise_feature_locked(message: str, module: str, required_plan: str = "BASIC") -> None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_LOCKED",
                "message": message,
                "module": module,
                "requiredPlan": required_plan,
                "upgradeUrl": "/billing",
            },
        )

    def get_plan_tier(self, learner_id: str) -> str:
        """Best-effort resolution of learner's active PlanTier value for KIE context."""
        try:
            ent = billing_service.get_or_create_entitlement(learner_id)
            return ent.current_plan.value
        except Exception:
            return PlanTier.FREE.value

    def require_capability(self, learner_id: str, capability: str, requested_tier: Optional[str] = None) -> None:
        """Validates feature access based on current subscription tier."""
        try:
            ent = billing_service.get_or_create_entitlement(learner_id)
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning(f"Capability check skipped ({capability}): {exc}")
            return

        plan = ent.current_plan
        if capability == "debugging" and plan == PlanTier.FREE:
            self._raise_feature_locked(
                "Debugging assistance requires a Basic or Pro plan.",
                module="BUILD",
                required_plan="BASIC",
            )
        elif capability == "project_evaluation" and plan == PlanTier.FREE:
            self._raise_feature_locked(
                "Project evaluation requires a Basic or Pro plan.",
                module="BUILD",
                required_plan="BASIC",
            )
        elif capability == "resume_template":
            req = (requested_tier or "starter").strip().lower()
            if req == "standard" and plan == PlanTier.FREE:
                self._raise_feature_locked(
                    "Standard resume templates require a Basic or Pro plan.",
                    module="LAUNCH",
                    required_plan="BASIC",
                )
            if req == "premium" and plan != PlanTier.PRO:
                self._raise_feature_locked(
                    "Premium resume templates require a Pro plan.",
                    module="LAUNCH",
                    required_plan="PRO",
                )

    def authorize_and_consume(
        self,
        learner_id: str,
        operation: CreditOperation,
        reference_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Validates module + total AI credits and optional monthly/daily feature caps,
        deducts atomically, and returns a ledger_id for refunding if downstream AI fails.
        """
        spec = OPERATION_SPECS[operation]
        try:
            ent = billing_service.get_or_create_entitlement(learner_id)
            usage = billing_service.get_or_create_usage(learner_id)
            sku = get_sku(ent.current_plan, ent.billing_cycle)

            feature_limit: Optional[int] = None
            feature_key_map = {
                "mock_tests_used": ("mockTests", sku.mock_tests),
                "ats_checks": ("atsChecks", sku.ats_checks),
                "mock_interviews_used": ("mockInterviews", sku.mock_interviews),
                "ai_tutor_requests": ("aiTutorRequests", usage.quotas["aiTutorRequests"].limit),
            }
            if spec.feature_col and spec.feature_col in feature_key_map:
                quota_key, feature_limit = feature_key_map[spec.feature_col]
                q_detail = usage.quotas.get(quota_key)
                if q_detail and q_detail.remaining <= 0:
                    next_plan = "PRO" if ent.current_plan == PlanTier.BASIC else "BASIC"
                    self._raise_quota_exceeded(
                        f"Your {quota_key} limit for this cycle has been reached. Upgrade to continue.",
                        module=spec.module.value,
                        required_plan=next_plan,
                    )

            module_limit = sku.module_credits[spec.module.value]
            if usage.credits and spec.credits > 0:
                mod_detail = usage.credits.modules.get(spec.module.value)
                if mod_detail and mod_detail.remaining < spec.credits:
                    next_plan = "PRO" if ent.current_plan == PlanTier.BASIC else "BASIC"
                    self._raise_quota_exceeded(
                        f"Insufficient {spec.module.value} AI credits ({mod_detail.remaining} left, {spec.credits} needed).",
                        module=spec.module.value,
                        required_plan=next_plan,
                    )
                if usage.credits.total_remaining < spec.credits:
                    next_plan = "PRO" if ent.current_plan == PlanTier.BASIC else "BASIC"
                    self._raise_quota_exceeded(
                        f"Insufficient AI credits ({usage.credits.total_remaining} left, {spec.credits} needed).",
                        module=spec.module.value,
                        required_plan=next_plan,
                    )

            # Attempt atomic Postgres RPC first
            try:
                rpc_res = supabase_admin.rpc(
                    "consume_billing_quota",
                    {
                        "p_learner_id": learner_id,
                        "p_module": spec.module.value,
                        "p_operation": operation.value,
                        "p_credit_cost": spec.credits,
                        "p_total_limit": sku.total_credits,
                        "p_module_limit": module_limit,
                        "p_feature_col": spec.feature_col,
                        "p_feature_limit": feature_limit,
                        "p_legacy_col": spec.legacy_col,
                        "p_reference_id": reference_id,
                    },
                ).execute()
                rpc_data = getattr(rpc_res, "data", None)
                if isinstance(rpc_data, dict):
                    if not rpc_data.get("allowed", False):
                        next_plan = "PRO" if ent.current_plan == PlanTier.BASIC else "BASIC"
                        self._raise_quota_exceeded(
                            f"Quota limit reached ({rpc_data.get('reason', 'QUOTA_EXCEEDED')}).",
                            module=spec.module.value,
                            required_plan=next_plan,
                        )
                    return str(rpc_data["ledger_id"]) if rpc_data.get("ledger_id") else None
            except HTTPException:
                raise
            except Exception:
                pass

            # Fallback table update when RPC is not deployed/mocked
            col_map = {
                ModuleType.LEARN: "learn_credits_used",
                ModuleType.BUILD: "build_credits_used",
                ModuleType.LAUNCH: "launch_credits_used",
            }
            mod_col = col_map[spec.module]
            current_mod_used = (
                usage.credits.modules[spec.module.value].used
                if usage.credits and spec.module.value in usage.credits.modules
                else 0
            )
            update_payload = {
                mod_col: current_mod_used + spec.credits,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if spec.feature_col:
                q_key = next((k for k, (qk, _) in [(spec.feature_col, feature_key_map[spec.feature_col])] if spec.feature_col in feature_key_map), None)
                if q_key:
                    qk_name = feature_key_map[spec.feature_col][0]
                    update_payload[spec.feature_col] = usage.quotas[qk_name].used + 1
            if spec.legacy_col and spec.legacy_col != spec.feature_col:
                legacy_key_map = {
                    "ai_roadmap_generations": "aiRoadmapGenerations",
                    "resume_generations": "resumeGenerations",
                    "ai_project_guidance": "aiProjectGuidance",
                    "ats_checks": "atsChecks",
                    "ai_tutor_requests": "aiTutorRequests",
                }
                lk = legacy_key_map.get(spec.legacy_col)
                if lk and lk in usage.quotas:
                    update_payload[spec.legacy_col] = usage.quotas[lk].used + 1

            supabase_admin.table("billing_usage_quotas").update(update_payload).eq("learner_id", learner_id).execute()
            return None
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning(f"Quota check skipped or unconfigured for {operation.value}: {exc}")
            return None

    def refund(self, ledger_id: Optional[str]) -> None:
        """Refunds consumed credits if a downstream AI call fails."""
        if not ledger_id:
            return
        try:
            supabase_admin.rpc("refund_billing_quota", {"p_ledger_id": ledger_id}).execute()
        except Exception as exc:
            logger.warning(f"Failed to refund ledger entry {ledger_id}: {exc}")


billing_guard = BillingGuardService()


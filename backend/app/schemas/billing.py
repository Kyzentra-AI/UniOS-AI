from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with camelCase serialization and loose parsing."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class PlanTier(str, Enum):
    FREE = "FREE"
    BASIC = "BASIC"
    PRO = "PRO"


class BillingCycle(str, Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    SEMESTER = "SEMESTER"


class RenewalPolicy(str, Enum):
    NONE = "NONE"
    ONE_TIME = "ONE_TIME"
    MANUAL = "MANUAL"


class SubscriptionSource(str, Enum):
    FREE_DEFAULT = "FREE_DEFAULT"
    PAYMENT = "PAYMENT"
    TRIAL = "TRIAL"
    ADMIN_PROMO = "ADMIN_PROMO"
    INSTITUTIONAL = "INSTITUTIONAL"


class ModuleType(str, Enum):
    LEARN = "LEARN"
    BUILD = "BUILD"
    LAUNCH = "LAUNCH"


class CreditOperation(str, Enum):
    SIMPLE_AI_QUESTION = "SIMPLE_AI_QUESTION"
    DETAILED_EXPLANATION = "DETAILED_EXPLANATION"
    AI_NOTES_GENERATION = "AI_NOTES_GENERATION"
    ASSESSMENT_GENERATION = "ASSESSMENT_GENERATION"
    SYLLABUS_ANALYSIS = "SYLLABUS_ANALYSIS"
    COMPLETE_ROADMAP_GENERATION = "COMPLETE_ROADMAP_GENERATION"
    ADVANCED_PROJECT_GUIDANCE = "ADVANCED_PROJECT_GUIDANCE"
    ADVANCED_DEBUGGING = "ADVANCED_DEBUGGING"
    CAREER_ANALYSIS = "CAREER_ANALYSIS"
    RESUME_OPTIMIZATION = "RESUME_OPTIMIZATION"
    ATS_SCAN = "ATS_SCAN"
    INTERVIEW_SIMULATION = "INTERVIEW_SIMULATION"


class EntitlementStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TRIAL = "TRIAL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


# ------------------------------------------------------------------------------
# Plan & Quota Schemas
# ------------------------------------------------------------------------------

class PlanQuotaMatrix(CamelModel):
    ai_roadmap_generations: int
    ai_roadmap_period: str = "monthly"
    ai_tutor_requests: int
    ai_tutor_period: str = "daily"
    practice_questions: int
    practice_questions_period: str = "daily"
    resume_generations: int
    resume_generations_period: str = "monthly"
    ats_checks: int
    ats_checks_period: str = "monthly"
    mock_tests: int = 1
    mock_tests_period: str = "monthly"
    mock_interviews: int = 0
    mock_interviews_period: str = "monthly"
    monthly_credits: int = 30
    module_credits: Dict[str, int] = Field(default_factory=dict)
    project_tracking_included: bool = True
    ai_project_guidance: int = 3
    debugging_access: str = "NONE"
    project_evaluation_access: str = "NONE"
    resume_template_tier: str = "starter"
    github_integration: str = "NONE"
    compete_access: str = "preview"
    coming_soon_features: List[str] = Field(
        default_factory=lambda: ["AI Mock Interviews", "GitHub Integration", "COMPETE"]
    )


class PlanCycleOption(CamelModel):
    billing_cycle: BillingCycle
    duration_days: int
    price: float
    currency: str = "INR"
    gst_included: bool = True
    total_credits: int
    module_credits: Dict[str, int]
    mock_tests: int
    ats_checks: int
    mock_interviews: int
    renewal_policy: RenewalPolicy


class PlanConfiguration(CamelModel):
    plan_code: PlanTier
    name: str
    price: float
    currency: str = "INR"
    gst_included: bool = True
    duration_days: int
    description: str
    features: List[str]
    coming_soon_features: List[str] = Field(
        default_factory=lambda: ["AI Mock Interviews", "GitHub Integration", "COMPETE"]
    )
    cycles: List[PlanCycleOption] = Field(default_factory=list)
    quotas: PlanQuotaMatrix


class PlansResponse(CamelModel):
    plans: List[PlanConfiguration]


# ------------------------------------------------------------------------------
# Entitlement & Usage Schemas
# ------------------------------------------------------------------------------

class EntitlementResponse(CamelModel):
    learner_id: str
    current_plan: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    status: EntitlementStatus
    source: SubscriptionSource = SubscriptionSource.FREE_DEFAULT
    trial_used: bool
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    is_active: bool
    is_trial: bool
    days_remaining: Optional[int] = None
    paid_amount: float = 0.0
    renewal_policy: RenewalPolicy = RenewalPolicy.NONE
    last_expired_plan: Optional[PlanTier] = None
    credit_cycle_index: int = 1
    credit_cycle_end: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QuotaUsageDetail(CamelModel):
    used: int
    limit: int
    remaining: int
    period: str


class ModuleCreditDetail(CamelModel):
    used: int
    limit: int
    remaining: int


class CreditSummary(CamelModel):
    total_used: int
    total_limit: int
    total_remaining: int
    cycle_start: Optional[datetime] = None
    cycle_end: Optional[datetime] = None
    modules: Dict[str, ModuleCreditDetail] = Field(default_factory=dict)


class UsageResponse(CamelModel):
    learner_id: str
    period_start: Optional[datetime] = None
    quotas: Dict[str, QuotaUsageDetail]
    credits: Optional[CreditSummary] = None
    next_reset_daily: datetime
    next_reset_monthly: datetime
    updated_at: Optional[datetime] = None


class TrialActivationResponse(CamelModel):
    success: bool
    message: str
    entitlement: EntitlementResponse


# ------------------------------------------------------------------------------
# Checkout, Preview & Order Schemas
# ------------------------------------------------------------------------------

class CheckoutPreviewResponse(CamelModel):
    plan_code: PlanTier
    billing_cycle: BillingCycle
    action_type: str  # NEW | RENEW | UPGRADE
    sku_price: float
    prorated_credit: float = 0.0
    remaining_days_credited: int = 0
    payable_amount: float
    currency: str = "INR"
    gst_included: bool = True
    new_period_start: datetime
    new_period_end: datetime
    allowed: bool = True
    block_reason: Optional[str] = None


class CheckoutRequest(CamelModel):
    plan_code: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    return_url: Optional[str] = None


class CheckoutResponse(CamelModel):
    order_id: str
    payment_session_id: str
    environment: str
    amount: float
    currency: str
    plan_code: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    sku_price: Optional[float] = None
    prorated_credit: float = 0.0
    gst_included: bool = True
    action_type: str = "NEW"


class PaymentStatusResponse(CamelModel):
    order_id: str
    status: OrderStatus
    plan_code: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    amount: float
    currency: str
    gst_included: bool = True
    cashfree_payment_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderHistoryItem(CamelModel):
    order_id: str
    plan_code: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    order_type: str = "NEW"
    sku_price: Optional[float] = None
    prorated_credit: float = 0.0
    amount: float
    currency: str
    gst_included: bool = True
    status: OrderStatus
    cashfree_payment_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderHistoryResponse(CamelModel):
    orders: List[OrderHistoryItem]
    total: int


class CreditLedgerItem(CamelModel):
    id: str
    module: str
    operation: str
    credits_delta: int
    status: str
    reference_id: Optional[str] = None
    created_at: datetime


class CreditLedgerResponse(CamelModel):
    entries: List[CreditLedgerItem]
    total: int


class AdminAssignSubscriptionRequest(CamelModel):
    learner_id: str
    plan_code: PlanTier
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    duration_days: Optional[int] = Field(default=None, ge=1, le=365)
    grant_type: str = Field(default="ADMIN_PROMO")  # ADMIN_PROMO | INSTITUTIONAL
    note: str = Field(..., min_length=3, max_length=500)


class AdminAssignSubscriptionResponse(CamelModel):
    success: bool
    message: str
    entitlement: EntitlementResponse


# ------------------------------------------------------------------------------
# Cashfree Webhook Schemas
# ------------------------------------------------------------------------------

class CashfreeOrderData(BaseModel):
    order_id: str
    order_amount: Optional[float] = None
    order_currency: Optional[str] = "INR"
    order_tags: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")


class CashfreePaymentData(BaseModel):
    cf_payment_id: Optional[Any] = None
    payment_status: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_currency: Optional[str] = "INR"
    payment_message: Optional[str] = None
    payment_time: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class CashfreeWebhookData(BaseModel):
    order: CashfreeOrderData
    payment: Optional[CashfreePaymentData] = None

    model_config = ConfigDict(extra="allow")


class CashfreeWebhookPayload(BaseModel):
    type: str
    event_time: Optional[str] = None
    data: CashfreeWebhookData

    model_config = ConfigDict(extra="allow")

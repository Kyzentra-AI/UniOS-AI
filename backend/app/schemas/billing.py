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
    project_tracking_included: bool
    ai_project_guidance: int
    compete_access: str


class PlanConfiguration(CamelModel):
    plan_code: PlanTier
    name: str
    price: float
    currency: str = "INR"
    duration_days: int
    description: str
    features: List[str]
    quotas: PlanQuotaMatrix


class PlansResponse(CamelModel):
    plans: List[PlanConfiguration]


# ------------------------------------------------------------------------------
# Entitlement & Usage Schemas
# ------------------------------------------------------------------------------

class EntitlementResponse(CamelModel):
    learner_id: str
    current_plan: PlanTier
    status: EntitlementStatus
    trial_used: bool
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    is_active: bool
    is_trial: bool
    days_remaining: Optional[int] = None
    updated_at: Optional[datetime] = None


class QuotaUsageDetail(CamelModel):
    used: int
    limit: int
    remaining: int
    period: str


class UsageResponse(CamelModel):
    learner_id: str
    period_start: Optional[datetime] = None
    quotas: Dict[str, QuotaUsageDetail]
    next_reset_daily: datetime
    next_reset_monthly: datetime
    updated_at: Optional[datetime] = None


class TrialActivationResponse(CamelModel):
    success: bool
    message: str
    entitlement: EntitlementResponse


# ------------------------------------------------------------------------------
# Checkout & Order Schemas
# ------------------------------------------------------------------------------

class CheckoutRequest(CamelModel):
    plan_code: PlanTier
    return_url: Optional[str] = None


class CheckoutResponse(CamelModel):
    order_id: str
    payment_session_id: str
    environment: str
    amount: float
    currency: str
    plan_code: PlanTier


class PaymentStatusResponse(CamelModel):
    order_id: str
    status: OrderStatus
    plan_code: PlanTier
    amount: float
    currency: str
    cashfree_payment_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderHistoryItem(CamelModel):
    order_id: str
    plan_code: PlanTier
    amount: float
    currency: str
    status: OrderStatus
    cashfree_payment_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderHistoryResponse(CamelModel):
    orders: List[OrderHistoryItem]
    total: int


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

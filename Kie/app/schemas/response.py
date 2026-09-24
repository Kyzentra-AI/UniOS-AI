from typing import Any

from pydantic import BaseModel, Field

from app.schemas.roadmap import RoadmapContract


class IdentityResult(BaseModel):
    user_id: str
    session_id: str
    role: str


class ContextResult(BaseModel):
    current_context: dict[str, Any] = Field(default_factory=dict)
    learner_stage: str | None = None
    learner_profile: dict[str, Any] = Field(default_factory=dict)
    learner_context: dict[str, Any] = Field(default_factory=dict)
    task: str
    memory: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    memory_categories: list[str] = Field(default_factory=list)
    sources: dict[str, str] = Field(default_factory=dict)


class IntentResult(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class PlanStep(BaseModel):
    step_id: str
    description: str
    agent: str | None = None


class RoadmapMetadata(BaseModel):
    planning_horizon: str | None = None
    learner_stage: str | None = None
    career_goal: str | None = None
    milestone_count: int = Field(ge=0)
    planning_status: str


class KIEMetadata(BaseModel):
    trace: dict[str, Any] = Field(default_factory=dict)
    model_routing: dict[str, Any] = Field(default_factory=dict)
    planning: dict[str, Any] = Field(default_factory=dict)
    roadmap: RoadmapMetadata | None = None
    roadmap_contract: RoadmapContract | None = None
    memory: dict[str, Any] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class KIEResponse(BaseModel):
    request_id: str
    session_id: str
    status: str
    identity: IdentityResult
    context: ContextResult
    intent: IntentResult
    plan: list[PlanStep]
    result: dict[str, Any]
    error: dict[str, Any] | None = None
    metadata: KIEMetadata = Field(default_factory=KIEMetadata)


# ============================================================
# Sprint 2 Onboarding Context Contracts
# ============================================================


class ContextQuestion(BaseModel):
    """
    A question returned by KIE when additional
    learner context is required during onboarding.
    """

    question_id: str = Field(
        ...,
        min_length=1,
    )

    text: str = Field(
        ...,
        min_length=1,
    )

    type: str = Field(
        ...,
        min_length=1,
    )

    options: list[str] = Field(
        default_factory=list,
    )


class AnalyzeContextResponse(BaseModel):
    """
    Response returned by KIE for the onboarding
    context analysis endpoint.

    KIE identifies missing learner information
    and returns structured questions.
    """

    status: str = "success"

    requires_more_info: bool = False

    questions: list[ContextQuestion] = Field(
        default_factory=list,
    )


class ResolveContextResponse(BaseModel):
    """
    Response returned by KIE after processing
    onboarding answers.

    Backend remains responsible for persisting
    the returned context.
    """

    status: str = "success"

    new_context: dict[str, Any] = Field(
        default_factory=dict,
    )
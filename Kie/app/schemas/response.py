from typing import Any

from pydantic import BaseModel, Field


class IdentityResult(BaseModel):
    user_id: str
    session_id: str
    role: str


class ContextResult(BaseModel):
    current_context: dict[str, Any] = Field(default_factory=dict)
    learner_stage: str | None = None
    learner_profile: dict[str, Any] = Field(default_factory=dict)
    task: str
    sources: dict[str, str] = Field(default_factory=dict)


class IntentResult(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class PlanStep(BaseModel):
    step_id: str
    description: str
    agent: str | None = None


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
    metadata: dict[str, Any] = Field(default_factory=dict)
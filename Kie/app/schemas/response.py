from typing import Any

from pydantic import BaseModel, Field


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

    intent: IntentResult

    plan: list[PlanStep]

    result: dict[str, Any]

    error: dict[str, Any] | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)
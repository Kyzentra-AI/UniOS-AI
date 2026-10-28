
from typing import Any, Literal

from pydantic import BaseModel, Field


class LearningInterpretRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    learner_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    user_intent: str = Field(...)

    context: dict[str, Any] = Field(default_factory=dict)
    references: list[dict[str, Any]] = Field(default_factory=list)


class LearningInterpretResponse(BaseModel):
    request_id: str
    intent_category: Literal[
        "CLARIFICATION",
        "NEXT_TOPIC",
        "REMEDIATION",
    ]
    pedagogical_strategy: str
    knowledge_gaps_identified: list[str]
    recommended_difficulty: int = Field(ge=1, le=5)
    internal_notes: str

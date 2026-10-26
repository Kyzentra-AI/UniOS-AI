
from typing import Any

from pydantic import BaseModel, Field


class CompetitionRecommendationRequest(BaseModel):
    learner_id: str = Field(..., min_length=1)
    learner_context: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=3, ge=1, le=10)


class CompetitionRecommendation(BaseModel):
    title: str
    challenge_type: str
    description: str
    matched_skills: list[str] = Field(default_factory=list)
    reason: str
    relevance_score: int = Field(ge=0, le=100)


class CompetitionRecommendationResponse(BaseModel):
    recommendations: list[CompetitionRecommendation]

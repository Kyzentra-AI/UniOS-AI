
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BuildRecommendation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    recommendation_id: str
    title: str
    type: str
    difficulty: Literal[
        "foundational",
        "intermediate",
        "advanced",
    ] = "intermediate"
    academic_domain: str
    description: str
    rationale: str
    skills: list[str] = Field(default_factory=list)
    estimated_effort_hours: float | None = None
    prerequisite_topics: list[str] = Field(default_factory=list)


class BuildRecommendationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    learner_id: str
    recommendations: list[BuildRecommendation] = Field(
        min_length=1
    )
    recommendation_rationale: str
    generated_at: str | None = None

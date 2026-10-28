from pydantic import BaseModel, Field


class BuildRecommendation(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    skills: list[str] = Field(default_factory=list)


class BuildRecommendationResponse(BaseModel):
    recommendations: list[BuildRecommendation] = Field(
        default_factory=list
    )
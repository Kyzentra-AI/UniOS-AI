
from pydantic import BaseModel, Field


class ChallengeReasoningRequest(BaseModel):
    challenge_title: str = Field(..., min_length=1)
    challenge_statement: str = Field(..., min_length=1)
    challenge_type: str = Field(default="general", min_length=1)
    domain: str | None = None
    learner_context: dict = Field(default_factory=dict)


class ChallengeRequirement(BaseModel):
    requirement: str
    priority: str = "medium"


class ChallengeReasoningResponse(BaseModel):
    challenge_title: str
    challenge_type: str
    problem_summary: str
    requirements: list[ChallengeRequirement]
    suggested_deliverables: list[str]
    assumptions: list[str]
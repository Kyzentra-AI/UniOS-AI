
from typing import Any

from pydantic import BaseModel, Field


class CompetitionPlanningRequest(BaseModel):
    challenge_title: str = Field(..., min_length=1)
    challenge_statement: str = Field(..., min_length=1)
    challenge_type: str = Field(default="general", min_length=1)
    deadline_days: int | None = Field(default=None, ge=1)
    learner_context: dict[str, Any] = Field(default_factory=dict)
    team_members: list[str] = Field(default_factory=list)


class CompetitionPlanTask(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    day_range: str


class CompetitionPlanningResponse(BaseModel):
    challenge_title: str
    challenge_type: str
    objective: str
    preparation_plan: list[CompetitionPlanTask]
    success_checklist: list[str]
    collaboration_guidance: list[str]
    assumptions: list[str]

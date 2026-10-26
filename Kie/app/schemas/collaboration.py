
from typing import Any

from pydantic import BaseModel, Field


class CollaborationRequest(BaseModel):
    challenge_title: str = Field(..., min_length=1)
    challenge_statement: str = Field(..., min_length=1)
    challenge_type: str = Field(default="general", min_length=1)
    team_members: list[str] = Field(default_factory=list)
    learner_context: dict[str, Any] = Field(default_factory=dict)


class CollaborationTask(BaseModel):
    title: str
    description: str
    suggested_owner: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    priority: str = "medium"


class CollaborationResponse(BaseModel):
    challenge_title: str
    challenge_type: str
    tasks: list[CollaborationTask]
    coordination_checkpoints: list[str]
    suggested_tool_categories: list[str]
    assumptions: list[str]

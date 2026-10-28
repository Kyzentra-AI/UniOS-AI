from typing import Any

from pydantic import BaseModel, Field


class BuildCoachRequest(BaseModel):
    intent: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    project_context: dict[str, Any] = Field(default_factory=dict)


class BuildCoachActionItem(BaseModel):
    type: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    url: str | None = None


class BuildCoachResponse(BaseModel):
    reply: str
    suggestions: list[str] = Field(default_factory=list)
    action_items: list[BuildCoachActionItem] = Field(default_factory=list)
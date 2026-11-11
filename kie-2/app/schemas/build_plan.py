import uuid
from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator


class BuildPlanRequest(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default="Build Project")
    description: str = Field(default="Project workspace")
    type: str = Field(default="CODING")
    domain: str = Field(default="General")
    goal: str = Field(default="Complete project milestone")
    skills: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if not d.get("project_id"):
            d["project_id"] = str(uuid.uuid4())
        if not d.get("title"):
            d["title"] = "Build Project"
        if not d.get("description"):
            d["description"] = "Project workspace"
        if not d.get("type"):
            d["type"] = "CODING"
        if not d.get("domain"):
            d["domain"] = "General"
        if not d.get("goal"):
            d["goal"] = "Complete project milestone"
        if d.get("skills") is None:
            d["skills"] = []
        elif isinstance(d["skills"], list):
            d["skills"] = [str(s) for s in d["skills"] if s is not None]
        return d


class BuildPlanTask(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(default="")
    order_idx: int = Field(default=1, ge=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_task(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if not d.get("title"):
            d["title"] = "Task"
        if d.get("description") is None:
            d["description"] = ""
        if not d.get("order_idx"):
            d["order_idx"] = 1
        return d


class BuildPlanMilestone(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(default="")
    order_idx: int = Field(default=1, ge=1)
    tasks: List[BuildPlanTask] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_milestone(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        d = dict(data)
        if not d.get("title"):
            d["title"] = "Milestone"
        if d.get("description") is None:
            d["description"] = ""
        if not d.get("order_idx"):
            d["order_idx"] = 1
        if d.get("tasks") is None:
            d["tasks"] = []
        return d


class BuildPlanResponse(BaseModel):
    milestones: List[BuildPlanMilestone] = Field(default_factory=list)

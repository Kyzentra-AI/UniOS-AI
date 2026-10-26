from pydantic import BaseModel, Field


class BuildPlanRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    skills: list[str] = Field(default_factory=list)


class BuildPlanTask(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    order_idx: int = Field(..., ge=1)


class BuildPlanMilestone(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    order_idx: int = Field(..., ge=1)
    tasks: list[BuildPlanTask] = Field(default_factory=list)


class BuildPlanResponse(BaseModel):
    milestones: list[BuildPlanMilestone] = Field(default_factory=list)
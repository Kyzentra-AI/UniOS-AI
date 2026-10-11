from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from uuid import UUID

class ProjectType(str, Enum):
    CODING = "CODING"
    RESEARCH = "RESEARCH"
    BUSINESS = "BUSINESS"
    ANALYSIS = "ANALYSIS"
    DESIGN = "DESIGN"
    OTHER = "OTHER"

class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class MilestoneStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

class ArtifactType(str, Enum):
    DOCUMENT = "DOCUMENT"
    UPLOAD = "UPLOAD"
    DELIVERABLE = "DELIVERABLE"
    PRESENTATION = "PRESENTATION"
    EVIDENCE = "EVIDENCE"


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True
    )


# ==============================================================================
# PROJECT SCHEMAS
# ==============================================================================

class CreateProjectInput(CamelModel):
    title: str = Field(..., description="Title of the project")
    description: Optional[str] = None
    type: ProjectType = Field(..., description="Type of the project")
    domain: Optional[str] = None
    goal: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

class UpdateProjectInput(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ProjectType] = None
    domain: Optional[str] = None
    goal: Optional[str] = None
    skills: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None

class Project(CamelModel):
    id: UUID
    learner_id: UUID
    title: str
    description: Optional[str] = None
    type: ProjectType
    domain: Optional[str] = None
    goal: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# MILESTONE SCHEMAS
# ==============================================================================

class CreateMilestoneInput(CamelModel):
    title: str
    description: Optional[str] = None
    status: Optional[MilestoneStatus] = MilestoneStatus.PENDING
    order_idx: Optional[int] = 0

class UpdateMilestoneInput(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MilestoneStatus] = None
    order_idx: Optional[int] = None

class Milestone(CamelModel):
    id: UUID
    project_id: UUID
    title: str
    description: Optional[str] = None
    status: MilestoneStatus
    order_idx: int
    created_at: datetime


# ==============================================================================
# TASK SCHEMAS
# ==============================================================================

class CreateTaskInput(CamelModel):
    milestone_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING
    order_idx: Optional[int] = 0

class UpdateTaskInput(CamelModel):
    milestone_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    order_idx: Optional[int] = None

class Task(CamelModel):
    id: UUID
    project_id: UUID
    milestone_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus
    order_idx: int
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# ARTIFACT SCHEMAS
# ==============================================================================

class CreateArtifactInput(CamelModel):
    title: str
    description: Optional[str] = None
    type: ArtifactType
    # First version details
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    storage_key: Optional[str] = None

class ArtifactVersionResponse(CamelModel):
    id: UUID
    artifact_id: UUID
    version: int
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    storage_key: Optional[str] = None
    created_at: datetime

class Artifact(CamelModel):
    id: UUID
    project_id: UUID
    title: str
    description: Optional[str] = None
    type: ArtifactType
    created_at: datetime
    updated_at: datetime
    versions: Optional[List[ArtifactVersionResponse]] = None


# ==============================================================================
# EVIDENCE SCHEMAS
# ==============================================================================

class CreateEvidenceInput(CamelModel):
    artifact_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

class Evidence(CamelModel):
    id: UUID
    project_id: UUID
    artifact_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    created_at: datetime


# ==============================================================================
# AI / KIE SCHEMAS
# ==============================================================================

class BuildCoachRequest(CamelModel):
    intent: str
    message: str
    context: Optional[Dict[str, Any]] = None

class BuildCoachResponse(CamelModel):
    reply: str
    suggestions: Optional[List[str]] = None
    action_items: Optional[List[Dict[str, Any]]] = None

class RecommendedProject(CamelModel):
    title: str
    description: str
    type: ProjectType
    skills: List[str]

class ProjectRecommendationResponse(CamelModel):
    recommendations: List[RecommendedProject]

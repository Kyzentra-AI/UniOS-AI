from pydantic import BaseModel
from typing import Optional
from enum import Enum
from app.schemas.roadmap import MissionType

class MissionStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DEFERRED = "DEFERRED"
    SKIPPED = "SKIPPED"

class MissionResponse(BaseModel):
    id: str
    roadmap_id: str
    title: str
    description: Optional[str] = None
    mission_type: MissionType
    subject: Optional[str] = None
    chapter: Optional[str] = None
    topic: Optional[str] = None
    objectives: Optional[str] = None
    core_concepts: Optional[str] = None
    deliverables: Optional[str] = None
    mastery_criteria: Optional[str] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    week: Optional[int] = None
    sequence: Optional[int] = None
    status: MissionStatus

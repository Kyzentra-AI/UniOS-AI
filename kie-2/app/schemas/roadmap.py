from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class MissionType(str, Enum):
    LEARNING = "LEARNING"
    REVISION = "REVISION"
    ASSIGNMENT = "ASSIGNMENT"
    PRACTICAL = "PRACTICAL"
    ARTIFACT = "ARTIFACT"
    CAREER = "CAREER"


class RoadmapMission(BaseModel):
    """A structured learning or practical mission inserted into the missions table."""
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, description="Mission title")
    type: MissionType = Field(..., description="Mission pedagogical type")
    description: str = Field(..., min_length=1, description="Detailed actionable mission description")
    priority: str = Field(default="MEDIUM", description="Priority level: HIGH | MEDIUM | LOW")
    estimated_minutes: int = Field(default=90, ge=1, description="Estimated duration in minutes")
    subject: Optional[str] = Field(default=None, description="Curriculum subject name")
    week: int = Field(default=1, ge=1, description="Week number in the progression plan")
    sequence: int = Field(default=1, ge=1, description="Sequence order within the week")


class RoadmapSubject(BaseModel):
    """Subject within an academic semester."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1)
    topics: List[str] = Field(default_factory=list)


class RoadmapSemester(BaseModel):
    """Academic semester division."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1)
    subjects: List[RoadmapSubject] = Field(default_factory=list)


class RoadmapCareer(BaseModel):
    """Career dimension in the roadmap."""
    model_config = ConfigDict(extra="ignore")

    goals: List[str] = Field(default_factory=list)


class AIMLRoadmapResponse(BaseModel):
    """
    Response schema for POST /api/v1/kie/roadmap/generate.
    Strictly validated by Backend against AIMLRoadmapResponse.
    """
    model_config = ConfigDict(extra="ignore")

    scope: str = Field(default="ACADEMIC", description="Echoed scope: ACADEMIC | CAREER | BOTH")
    semesters: List[RoadmapSemester] = Field(default_factory=list)
    career: Optional[RoadmapCareer] = None
    goals: List[str] = Field(default_factory=list)
    milestones: List[str] = Field(default_factory=list)
    missions: List[RoadmapMission] = Field(default_factory=list)


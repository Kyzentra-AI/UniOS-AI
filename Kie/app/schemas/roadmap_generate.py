from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================
# Context V2 Request
# ============================================================


class RoadmapLearner(BaseModel):
    id: str = Field(..., min_length=1)
    primary_goal: str = Field(..., min_length=1)


class RoadmapCareerContext(BaseModel):
    target_skills: list[str] = Field(
        default_factory=list
    )


class RoadmapContextV2Request(BaseModel):
    """
    Context V2 request received from UniOS Backend.

    This endpoint is synchronous:
    Backend -> KIE -> generated roadmap -> Backend.
    """

    learner: RoadmapLearner

    education: dict[str, Any] = Field(
        default_factory=dict
    )

    career: RoadmapCareerContext = Field(
        default_factory=RoadmapCareerContext
    )

    skills: list[str] = Field(
        default_factory=list
    )

    preferences: dict[str, Any] = Field(
        default_factory=dict
    )

    syllabus: dict[str, Any] = Field(
        default_factory=dict
    )

    roadmap: dict[str, Any] = Field(
        default_factory=dict
    )

    recent_history: list[Any] = Field(
        default_factory=list
    )

    memory_summary: str = ""

    scope: Literal[
        "ACADEMIC",
        "CAREER",
        "BOTH",
    ]


# ============================================================
# Response Models
# ============================================================


class RoadmapSubject(BaseModel):
    name: str

    topics: list[str] = Field(
        default_factory=list
    )


class RoadmapSemester(BaseModel):
    name: str

    subjects: list[RoadmapSubject] = Field(
        default_factory=list
    )


class RoadmapCareer(BaseModel):
    goals: list[str] = Field(
        default_factory=list
    )


class MissionType(str, Enum):
    LEARNING = "LEARNING"
    REVISION = "REVISION"
    ASSIGNMENT = "ASSIGNMENT"
    PRACTICAL = "PRACTICAL"
    ARTIFACT = "ARTIFACT"
    CAREER = "CAREER"


class RoadmapMission(BaseModel):
    title: str
    type: MissionType
    description: str
    priority: str
    estimated_minutes: int = Field(
        ge=1
    )
    subject: str | None = None
    week: int = Field(
        ge=1
    )
    sequence: int = Field(
        ge=1
    )


class AIMLRoadmapResponse(BaseModel):
    """
    Exact response contract expected by Backend.
    """

    scope: str

    semesters: list[RoadmapSemester] = Field(
        default_factory=list
    )

    career: RoadmapCareer | None = None

    goals: list[str] = Field(
        default_factory=list
    )

    milestones: list[str] = Field(
        default_factory=list
    )

    missions: list[RoadmapMission] = Field(
        default_factory=list
    )
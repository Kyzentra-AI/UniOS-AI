from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class RoadmapLearner(BaseModel):
    primary_goal: str = Field(..., min_length=1)
    target_skills: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    research: str | None = None
    experience: str | None = None
    inferred_context: dict[str, Any] = Field(default_factory=dict)
    id: str | None = None


class RoadmapCareerContext(BaseModel):
    target_skills: list[str] = Field(default_factory=list)


class RoadmapContextV2Request(BaseModel):
    # Optional for backward compatibility with the older
    # Sprint 3 roadmap contract.
    learner_id: str | None = None

    learner: RoadmapLearner

    education: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    syllabus: dict[str, Any] = Field(default_factory=dict)
    roadmap: dict[str, Any] = Field(default_factory=dict)
    recent_history: list[Any] = Field(default_factory=list)

    memory_summary: dict[str, Any] | str = Field(default_factory=dict)

    scope: Literal["ACADEMIC", "CAREER", "BOTH"]

    # Backward-compatible top-level fields from the older Context V2 contract.
    skills: list[str] = Field(default_factory=list)
    career: RoadmapCareerContext = Field(
        default_factory=RoadmapCareerContext
    )

    @model_validator(mode="after")
    def normalize_context(self):
        # If the new top-level learner_id is not supplied,
        # use the older learner.id field when available.
        if not self.learner_id and self.learner.id:
            self.learner_id = self.learner.id

        # Combine skills from both old and new contract locations.
        combined_skills: list[str] = []

        combined_skills.extend(self.learner.skills)
        combined_skills.extend(self.learner.target_skills)
        combined_skills.extend(self.skills)
        combined_skills.extend(self.career.target_skills)

        normalized_skills: list[str] = []

        for skill in combined_skills:
            if skill is None:
                continue

            skill = str(skill).strip()

            if skill and skill not in normalized_skills:
                normalized_skills.append(skill)

        self.skills = normalized_skills

        # Keep career target skills synchronized with the
        # newer learner.target_skills field.
        if self.learner.target_skills:
            self.career.target_skills = list(
                self.learner.target_skills
            )

        return self


class RoadmapSubject(BaseModel):
    name: str
    topics: list[str] = Field(default_factory=list)


class RoadmapSemester(BaseModel):
    name: str
    subjects: list[RoadmapSubject] = Field(default_factory=list)


class RoadmapCareer(BaseModel):
    goals: list[str] = Field(default_factory=list)


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
    estimated_minutes: int = Field(ge=1)
    subject: str | None = None
    week: int = Field(ge=1)
    sequence: int = Field(ge=1)


class AIMLRoadmapResponse(BaseModel):
    scope: str
    semesters: list[RoadmapSemester] = Field(default_factory=list)
    career: RoadmapCareer | None = None
    goals: list[str] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    missions: list[RoadmapMission] = Field(default_factory=list)
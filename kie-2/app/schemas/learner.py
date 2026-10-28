import re
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LearnerStage(str, Enum):
    """Academic and professional development stages recognized by AI/ML-2."""
    BACHELOR = "bachelor"
    MASTER = "master"
    GRADUATE = "graduate"


class ConfidenceLevel(str, Enum):
    """Learner self-confidence tiers for pedagogical calibration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LearnerIdentity(BaseModel):
    """Identity contract consumed by AI/ML-2 for intelligence generation.
    
    CRITICAL ARCHITECTURAL BOUNDARY:
    Authentication, passwords, credentials, sessions, and core user lifecycle
    management are strictly owned by UniOS Backend / KIE.
    AI/ML-2 only consumes this identity contract to personalize learning intelligence.
    """

    learner_id: str = Field(
        ...,
        description="Unique learner identifier from UniOS Backend / KIE (alphanumeric, hyphens, underscores)",
    )
    stage: LearnerStage = Field(
        default=LearnerStage.BACHELOR,
        description="Academic career stage (bachelor, master, graduate)",
    )
    academic_program: Optional[str] = Field(
        default=None,
        description="Enrolled degree or program (e.g. B.Tech Computer Science)",
    )
    current_semester: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Current semester (1 to 20)",
    )
    institution: Optional[str] = Field(
        default=None,
        description="University, college, or organization name",
    )
    full_name: Optional[str] = Field(
        default=None,
        description="Optional display name for personalized intelligence summaries",
    )
    email: Optional[str] = Field(
        default=None,
        description="Optional contact reference metadata",
    )

    @field_validator("learner_id")
    @classmethod
    def validate_learner_id(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("learner_id must be a string.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("learner_id cannot be empty or whitespace.")
        if len(cleaned) > 128:
            raise ValueError("learner_id exceeds maximum length of 128 characters.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@]+$", cleaned):
            raise ValueError(
                "learner_id contains invalid characters. Must contain only alphanumeric, '-', '_', '.', ':', or '@'."
            )
        return cleaned

    @field_validator("academic_program", "institution", "full_name", mode="before")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            cleaned = v.strip()
            return cleaned if cleaned else None
        return str(v)


class LearnerState(BaseModel):
    """Represents the active knowledge, skill, and behavioral state of the learner."""

    learner_id: str = Field(
        default="learner_001",
        description="Learner identifier associated with this active learning state",
    )
    stage: LearnerStage = LearnerStage.BACHELOR
    academic_program: str = "Computer Science"
    current_semester: Optional[int] = Field(default=None, ge=1, le=20)
    concept_mastery: Dict[str, float] = Field(
        default_factory=dict,
        description="Concept name mapped to mastery score between 0.0 and 1.0",
    )
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    weak_topics: List[str] = Field(default_factory=list)
    strong_topics: List[str] = Field(default_factory=list)
    career_goal: Optional[str] = None
    learning_preference: Optional[str] = "visual"
    academic_domain: Optional[str] = Field(
        default=None,
        description="Canonical academic domain (e.g. engineering, commerce, humanities, science, management, law)",
    )
    degree: Optional[str] = Field(
        default=None,
        description="Formal degree title (e.g. B.Tech, B.Com, BA, MSc, MBA)",
    )
    specialization: Optional[str] = Field(
        default=None,
        description="Disciplinary specialization or major concentration",
    )

    @field_validator("learner_id")
    @classmethod
    def validate_state_learner_id(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("learner_id must be a string.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("learner_id cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@]+$", cleaned):
            raise ValueError("learner_id contains invalid characters.")
        return cleaned

    @field_validator("concept_mastery")
    @classmethod
    def validate_concept_mastery(cls, v: Dict[str, float]) -> Dict[str, float]:
        for concept, score in v.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Concept mastery score for '{concept}' must be numeric.")
            if not (0.0 <= float(score) <= 1.0):
                raise ValueError(
                    f"Concept mastery score for '{concept}' must be between 0.0 and 1.0, got {score}"
                )
        return v

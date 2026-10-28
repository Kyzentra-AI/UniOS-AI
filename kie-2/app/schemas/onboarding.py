import re
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.learner import LearnerStage, LearnerIdentity, LearnerState


class SkillCategory(str, Enum):
    """Categorization of technical and domain skills."""
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    THEORY = "theory"
    TOOLS = "tools"
    SOFT_SKILLS = "soft_skills"


class DeclaredSkill(BaseModel):
    """A skill self-declared by the learner during onboarding."""

    skill_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the skill, language, or concept (e.g. Python, Docker)",
    )
    self_rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Self-assessment score between 1 (novice) and 5 (expert)",
    )
    category: SkillCategory = Field(
        default=SkillCategory.PROGRAMMING,
        description="Functional skill taxonomy category",
    )

    @field_validator("skill_name")
    @classmethod
    def validate_skill_name(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("skill_name must be a string.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("skill_name cannot be empty or whitespace only.")
        if len(cleaned) < 2:
            raise ValueError("skill_name must have at least 2 characters.")
        if len(cleaned) > 100:
            raise ValueError("skill_name exceeds maximum length of 100 characters.")
        return cleaned


class LearningPreferencesInput(BaseModel):
    """Learner pedagogical and instructional preferences collected during onboarding."""

    preferred_medium: Optional[str] = Field(
        default=None,
        description="Preferred style: visual, hands-on, theoretical, interactive, conversational",
    )
    pace: Optional[str] = Field(
        default=None,
        description="Self-identified pace: fast-track, moderate, relaxed",
    )
    weekly_hours: Optional[int] = Field(
        default=None,
        ge=1,
        le=80,
        description="Available weekly hours dedicated to learning (1 to 80)",
    )
    practical_vs_theory_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Ratio of practical project work vs theoretical conceptual study (0.0 to 1.0)",
    )

    @field_validator("preferred_medium", "pace", mode="before")
    @classmethod
    def normalize_preference_strings(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Preference value must be a string.")
        cleaned = v.strip().lower()
        if not cleaned:
            return None
        return cleaned


class LearnerProfileCreate(BaseModel):
    """Contract for submitting a new onboarding profile from UniOS Backend / KIE."""

    learner_id: str = Field(
        ...,
        description="Unique identifier of the learner from Backend/KIE",
    )
    stage: Optional[LearnerStage] = Field(
        default=None,
        description="Current academic/career stage",
    )
    academic_program: Optional[str] = Field(
        default=None,
        description="Academic degree or department",
    )
    current_semester: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Current enrolled semester",
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Desired target career role (e.g. Fullstack Engineer, ML Architect)",
    )
    career_goal: Optional[str] = Field(
        default=None,
        description="Desired career goal or role if provided in place of target_role",
    )
    declared_skills: List[DeclaredSkill] = Field(
        default_factory=list,
        description="Self-declared technical baseline skills",
    )
    interests: List[str] = Field(
        default_factory=list,
        description="Key domain interests and learning curiosities",
    )
    preferences: Optional[LearningPreferencesInput] = Field(
        default=None,
        description="Cognitive and study preferences",
    )
    motivation_statement: Optional[str] = Field(
        default=None,
        description="Learner's primary stated motivation or career transition driver",
    )
    prior_projects_summary: Optional[str] = Field(
        default=None,
        description="Summary of past hands-on engineering or academic projects",
    )

    @field_validator("learner_id")
    @classmethod
    def validate_learner_id(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("learner_id must be a string.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("learner_id cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@]+$", cleaned):
            raise ValueError("learner_id contains invalid characters.")
        return cleaned

    @model_validator(mode="after")
    def validate_role(self) -> "LearnerProfileCreate":
        role = self.target_role or self.career_goal
        if not role or not str(role).strip():
            raise ValueError("Either target_role or career_goal must be provided.")
        cleaned = str(role).strip()
        if len(cleaned) < 2:
            raise ValueError("target_role must contain at least 2 characters.")
        self.target_role = cleaned
        return self


class LearnerProfileSummary(BaseModel):
    """Compact summary of a learner profile for overview, listings, and logging."""

    learner_id: str
    stage: Optional[LearnerStage] = None
    target_role: str
    declared_skills_count: int = 0
    top_skills: List[str] = Field(default_factory=list)
    weekly_hours: Optional[int] = None
    preferred_medium: Optional[str] = None


class LearnerProfileValidationResult(BaseModel):
    """Result returned by the lightweight /validate-profile preflight endpoint."""

    is_valid: bool = True
    learner_id: str
    stage: Optional[LearnerStage] = None
    target_role: str
    issues: List[str] = Field(
        default_factory=list,
        description="List of detected validation problems or profile gaps",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable suggestions to improve onboarding data quality",
    )
    declared_skills_count: int = 0
    estimated_readiness_indicator: str = Field(
        default="pending_ai_analysis",
        description="Heuristic readiness indicator prior to full LLM analysis",
    )


class OnboardingInputProfile(BaseModel):
    """Normalized onboarding profile ingested from UniOS Backend / KIE for AI/ML-2 intelligence analysis."""

    learner_id: str = Field(
        ...,
        description="Unique identifier of the learner (UUID or clean handle)",
    )
    identity: Optional[LearnerIdentity] = Field(
        default=None,
        description="Optional structured identity metadata consumed from Backend",
    )
    stage: Optional[LearnerStage] = Field(
        default=None,
        description="Academic development stage",
    )
    academic_program: Optional[str] = Field(
        default=None,
        description="Current enrolled degree or department",
    )
    current_semester: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Current enrolled semester",
    )
    target_role: Optional[str] = Field(
        default=None,
        description="Target engineering or academic role",
    )
    career_goal: Optional[str] = Field(
        default=None,
        description="Target career role or goal provided directly or synonymously",
    )
    declared_skills: List[DeclaredSkill] = Field(
        default_factory=list,
        description="Baseline skills self-assessed by learner",
    )
    interests: List[str] = Field(
        default_factory=list,
        description="Topics and domain areas of interest",
    )
    preferences: Optional[LearningPreferencesInput] = Field(
        default=None,
        description="Study schedule and cognitive preferences",
    )
    motivation_statement: Optional[str] = Field(
        default=None,
        description="Learner's statement of intent or motivation",
    )
    prior_projects_summary: Optional[str] = Field(
        default=None,
        description="Past project or coursework summary",
    )
    learner_state: Optional[LearnerState] = Field(
        default=None,
        description="Active learner state ingested from Learning Engine, KIE, or diagnostic assessments",
    )
    concept_mastery: Optional[Dict[str, float]] = Field(
        default=None,
        description="Concept name mapped to mastery score between 0.0 and 1.0",
    )
    weak_topics: Optional[List[str]] = Field(
        default=None,
        description="Known weak topics from assessments or learning history",
    )
    strong_topics: Optional[List[str]] = Field(
        default=None,
        description="Known strong topics from assessments or learning history",
    )
    learning_preference: Optional[str] = Field(
        default=None,
        description="Primary learning modality preference",
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
            raise ValueError("learner_id contains invalid characters.")
        return cleaned

    @field_validator("interests", mode="before")
    @classmethod
    def sanitize_interests(cls, v: Optional[List[str]]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return []

    @model_validator(mode="after")
    def validate_and_normalize_role(self) -> "OnboardingInputProfile":
        role = self.target_role
        if not role or not str(role).strip():
            role = self.career_goal
        if (not role or not str(role).strip()) and self.learner_state and self.learner_state.career_goal:
            role = self.learner_state.career_goal

        if not role or not str(role).strip():
            raise ValueError("Either 'target_role' or 'career_goal' must be provided.")

        cleaned_role = str(role).strip()
        if len(cleaned_role) < 2:
            raise ValueError("target_role must contain at least 2 characters.")

        self.target_role = cleaned_role
        return self

    def get_effective_target_role(self) -> str:
        return self.target_role or "Software Engineer"

    def get_effective_concept_mastery(self) -> Dict[str, float]:
        mastery: Dict[str, float] = {}
        if self.learner_state and self.learner_state.concept_mastery:
            mastery.update(self.learner_state.concept_mastery)
        if self.concept_mastery:
            mastery.update(self.concept_mastery)
        return mastery

    def get_effective_weak_topics(self) -> List[str]:
        topics: List[str] = []
        if self.learner_state and self.learner_state.weak_topics:
            topics.extend(self.learner_state.weak_topics)
        if self.weak_topics:
            for t in self.weak_topics:
                if t not in topics:
                    topics.append(t)
        return topics

    def get_effective_strong_topics(self) -> List[str]:
        topics: List[str] = []
        if self.learner_state and self.learner_state.strong_topics:
            topics.extend(self.learner_state.strong_topics)
        if self.strong_topics:
            for t in self.strong_topics:
                if t not in topics:
                    topics.append(t)
        return topics

    def get_effective_learning_preference(self) -> Optional[str]:
        if self.preferences and self.preferences.preferred_medium:
            return self.preferences.preferred_medium
        if self.learning_preference:
            return self.learning_preference
        if self.learner_state and self.learner_state.learning_preference:
            return self.learner_state.learning_preference
        return None

    def get_effective_weekly_hours(self) -> Optional[int]:
        if self.preferences and self.preferences.weekly_hours is not None:
            return self.preferences.weekly_hours
        return None

    def get_effective_practical_ratio(self) -> Optional[float]:
        if self.preferences and self.preferences.practical_vs_theory_ratio is not None:
            return self.preferences.practical_vs_theory_ratio
        return None

    def get_effective_pace(self) -> Optional[str]:
        if self.preferences and self.preferences.pace:
            return self.preferences.pace
        return None

    def get_effective_stage(self) -> LearnerStage:
        if self.stage:
            return self.stage
        if self.learner_state and self.learner_state.stage:
            return self.learner_state.stage
        return LearnerStage.BACHELOR

    def to_summary(self) -> LearnerProfileSummary:
        """Helper to create a LearnerProfileSummary from this input profile."""
        top_skills = [s.skill_name for s in self.declared_skills if s.self_rating >= 4]
        return LearnerProfileSummary(
            learner_id=self.learner_id,
            stage=self.stage,
            target_role=self.get_effective_target_role(),
            declared_skills_count=len(self.declared_skills),
            top_skills=top_skills,
            weekly_hours=self.get_effective_weekly_hours(),
            preferred_medium=self.get_effective_learning_preference(),
        )

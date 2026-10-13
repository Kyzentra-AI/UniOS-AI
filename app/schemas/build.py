"""
Sprint 5 — Universal Build Engine Schemas (AI/ML-2)
Task A2-S5-01: Contextual Build Coach
Task A2-S5-02: Project Recommendations

ARCHITECTURAL BOUNDARY:
  - Backend owns authoritative project persistence, artifact binaries, and user records.
  - AI/ML-2 owns pedagogical coaching intelligence and domain-adaptive recommendations.
  - These schemas are the AI/ML-2 side of the Backend-approved contract.
  - request_id is required in every cross-service request and response for tracing.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import re


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ArtifactType(str, Enum):
    """Universal build artifact taxonomy — not limited to software."""
    CODE_PROJECT    = "code_project"      # Software / algorithm implementation
    ESSAY           = "essay"             # Humanities / law / management essay
    RESEARCH_REPORT = "research_report"   # Science lab report, literature review
    BUSINESS_PLAN   = "business_plan"     # Commerce / management capstone
    CASE_ANALYSIS   = "case_analysis"     # Law case brief, business case study
    DATA_ANALYSIS   = "data_analysis"     # Statistics / economics data project
    DESIGN_ARTIFACT = "design_artifact"   # Architecture drawing, UX prototype
    LAB_NOTEBOOK    = "lab_notebook"      # Science practical / experiment log
    ORAL_VIVA       = "oral_viva"         # Verbal examination evidence
    PORTFOLIO       = "portfolio"         # Multi-artifact composite submission
    GENERAL         = "general"           # Domain-agnostic fallback


class BuildDifficulty(str, Enum):
    FOUNDATIONAL   = "foundational"
    INTERMEDIATE   = "intermediate"
    ADVANCED       = "advanced"


class CoachingTone(str, Enum):
    """Pedagogical tone calibrated to learner's mastery and confidence."""
    ENCOURAGING    = "encouraging"    # Low mastery / first attempt
    INSTRUCTIVE    = "instructive"    # Mid-tier / developing learner
    CHALLENGING    = "challenging"    # High mastery / advancement


# ---------------------------------------------------------------------------
# Coaching Request (POST /api/v1/kie/build/coach)
# ---------------------------------------------------------------------------

class BuildCoachRequest(BaseModel):
    """
    Request payload for the Contextual Build Coach endpoint.

    Supplied by Backend / AI/ML-1 carrying authoritative learner context
    and the project being coached. Backend owns project persistence;
    AI/ML-2 generates coaching intelligence only.
    """

    request_id: str = Field(
        ...,
        min_length=1,
        description="Canonical cross-service tracing identifier (required).",
    )
    learner_id: str = Field(
        ...,
        min_length=1,
        description="Learner identifier from Backend / KIE.",
    )

    # --- Project context (provided by Backend) ---
    project_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the active build project.",
    )
    artifact_type: ArtifactType = Field(
        default=ArtifactType.GENERAL,
        description="Category of the build artifact being coached.",
    )
    academic_domain: Optional[str] = Field(
        default=None,
        description="Canonical academic domain: engineering, commerce, humanities, science, management, law.",
    )
    current_milestone: Optional[str] = Field(
        default=None,
        description="Which milestone the learner is currently working on.",
    )
    milestone_description: Optional[str] = Field(
        default=None,
        description="Optional detailed description of the current milestone.",
    )
    submitted_work_summary: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Plain-text summary of what the learner has submitted so far. "
                    "AI/ML-2 never receives or stores the raw artifact binary.",
    )
    struggle_description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Learner's own description of where they are stuck, if any.",
    )

    # --- Learner state (passed from Backend / AI/ML-1) ---
    learner_stage: Optional[str] = Field(
        default=None,
        description="Academic stage: bachelor, master, graduate.",
    )
    concept_mastery: Optional[Dict[str, float]] = Field(
        default=None,
        description="Relevant concept mastery scores (0.0–1.0) from Backend.",
    )
    weak_topics: Optional[List[str]] = Field(
        default=None,
        description="Active weak topics from Backend mastery records.",
    )

    # --- Optional rubric from Backend ---
    rubric_criteria: Optional[List[str]] = Field(
        default=None,
        description="Graded rubric criteria supplied by Backend for this milestone.",
    )

    # --- Memory context (optional, from AI/ML-2 memory engine) ---
    relevant_friction: Optional[List[str]] = Field(
        default=None,
        description="Active friction topics from AI/ML-2 memory context.",
    )

    @field_validator("learner_id", "request_id")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@/]+$", cleaned):
            raise ValueError("Field contains invalid characters.")
        return cleaned

    @field_validator("concept_mastery")
    @classmethod
    def validate_mastery_scores(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if v is None:
            return v
        for concept, score in v.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Mastery score for '{concept}' must be numeric.")
            if not (0.0 <= float(score) <= 1.0):
                raise ValueError(f"Mastery score for '{concept}' must be between 0.0 and 1.0.")
        return v


# ---------------------------------------------------------------------------
# Coaching Response (POST /api/v1/kie/build/coach)
# ---------------------------------------------------------------------------

class CoachingBlock(BaseModel):
    """
    A single structured coaching unit — domain-adaptive, never raw UI code.
    Consumed by UniOS LessonRenderer / BuildRenderer.
    """

    block_type: str = Field(
        ...,
        description="Block type: orientation | gap_analysis | guidance | example | next_step | encouragement",
    )
    title: str = Field(default="", description="Short descriptive heading.")
    content: str = Field(
        ...,
        description="Coaching prose in plain text or structured markdown. "
                    "Never raw HTML, JSX, or frontend code.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional renderer metadata (e.g. rubric criterion references, severity tags).",
    )


class BuildCoachResponse(BaseModel):
    """
    Structured coaching response from AI/ML-2 Universal Build Coach.
    Backend stores this response; AI/ML-2 does not maintain its own project DB.
    """

    request_id: str = Field(..., description="Echoed tracing ID from request.")
    learner_id: str
    project_title: str
    artifact_type: ArtifactType
    coaching_tone: CoachingTone
    coaching_blocks: List[CoachingBlock] = Field(
        ...,
        min_length=1,
        description="Ordered sequence of structured coaching units.",
    )
    gap_summary: Optional[str] = Field(
        default=None,
        description="One-paragraph synthesis of detected gaps vs. rubric criteria.",
    )
    next_milestone_hint: Optional[str] = Field(
        default=None,
        description="AI/ML-2 hint for the next milestone step.",
    )
    remediation_recommended: bool = Field(
        default=False,
        description="True if the coaching analysis recommends a formal remediation lesson before continuing.",
    )
    generated_at: datetime = Field(default_factory=_utc_now)


# ---------------------------------------------------------------------------
# Recommendation Request  (GET /api/v1/kie/build/recommend?learner_id=...)
# ---------------------------------------------------------------------------

class BuildRecommendContext(BaseModel):
    """
    Learner context passed to the recommendation engine.
    Constructed from Backend query parameters; no direct DB access by AI/ML-2.
    """

    learner_id: str
    academic_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    target_role: Optional[str] = None
    completed_milestones: Optional[List[str]] = Field(default=None)
    current_weak_topics: Optional[List[str]] = Field(default=None)
    concept_mastery: Optional[Dict[str, float]] = Field(default=None)
    preferred_artifact_types: Optional[List[ArtifactType]] = Field(default=None)


# ---------------------------------------------------------------------------
# Recommendation Response (GET /api/v1/kie/build/recommend)
# ---------------------------------------------------------------------------

class ProjectRecommendation(BaseModel):
    """A single project recommendation with rationale."""

    recommendation_id: str = Field(
        ...,
        description="Deterministic short identifier for this recommendation.",
    )
    title: str
    artifact_type: ArtifactType
    difficulty: BuildDifficulty
    academic_domain: str
    description: str = Field(
        ...,
        description="Domain-adaptive project description tailored to learner stage and role.",
    )
    rationale: str = Field(
        ...,
        description="Why this project is recommended given the learner's mastery and goals.",
    )
    key_skills_targeted: List[str] = Field(default_factory=list)
    estimated_effort_hours: Optional[float] = None
    prerequisite_topics: List[str] = Field(default_factory=list)


class BuildRecommendResponse(BaseModel):
    """
    Structured project recommendation list from AI/ML-2.
    Backend is responsible for persisting any selected recommendation as a project record.
    """

    request_id: str = Field(
        ...,
        description="Cross-service tracing ID. Backend must supply via query param or header.",
    )
    learner_id: str
    recommendations: List[ProjectRecommendation] = Field(
        ...,
        min_length=1,
    )
    recommendation_rationale: str = Field(
        ...,
        description="Overall reasoning for why these projects were chosen.",
    )
    generated_at: datetime = Field(default_factory=_utc_now)

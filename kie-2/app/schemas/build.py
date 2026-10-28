"""
Sprint 5 — Universal Build Engine Schemas (AI/ML-2)
Task A2-S5-01: Contextual Build Coach
Task A2-S5-02: Project Recommendations

ARCHITECTURAL BOUNDARY:
  - Backend owns authoritative project persistence, artifact binaries, and user records.
  - AI/ML-2 owns pedagogical coaching intelligence and domain-adaptive recommendations.
  - These schemas are the AI/ML-2 side of the Backend-approved contract.
  - Public wire schemas (BuildCoachPublicRequest / BuildCoachPublicResponse) are the
    exact contract fields agreed with Backend.
  - Internal schemas (BuildCoachRequest / BuildCoachResponse) carry rich pedagogical
    context used inside the coaching engine only.
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
# PUBLIC WIRE SCHEMAS — Backend Contract (POST /api/v1/kie/build/coach)
# ---------------------------------------------------------------------------

class ProjectContextInput(BaseModel):
    """
    Nested project context supplied by Backend in the public coach request.
    Maps to the internal coaching engine's project fields.
    """
    id: Optional[str] = Field(default=None, description="Backend project identifier.")
    title: Optional[str] = Field(default=None, description="Project title.")
    type: Optional[str] = Field(
        default=None,
        description="Artifact type string (e.g. 'code_project', 'essay'). Maps to ArtifactType.",
    )
    status: Optional[str] = Field(
        default=None,
        description="Current project status (e.g. 'in_progress', 'draft').",
    )
    skills: Optional[List[str]] = Field(
        default=None,
        description="Skills or rubric criteria associated with this project.",
    )


class BuildCoachPublicRequest(BaseModel):
    """
    Public wire request schema for POST /api/v1/kie/build/coach.

    This is the Backend-approved contract. Fields map to the internal
    coaching engine as follows:
      intent          → coaching focus / requested coaching type
      message         → learner's message / struggle description
      context         → supplementary learner context (stage, domain, etc.)
      project_context → project metadata (title, type, status, skills)
    """
    intent: str = Field(
        ...,
        min_length=1,
        description=(
            "Coaching intent declared by the learner or Backend: "
            "'review', 'guidance', 'next_step', 'general', etc."
        ),
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Learner's message, question, or struggle description.",
    )
    context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description=(
            "Optional supplementary context: learner stage, academic domain, "
            "current milestone, or any enrichment text passed by Backend."
        ),
    )
    project_context: Optional[ProjectContextInput] = Field(
        default=None,
        description="Structured project metadata from Backend.",
    )


class ActionItem(BaseModel):
    """
    A structured action item in the public coach response.
    Consumed by the Frontend / AI/ML-1 to surface actionable next steps.
    """
    type: str = Field(
        ...,
        description=(
            "Action type identifier. Examples: "
            "'DOCUMENTATION_LINK', 'NEXT_STEP', 'REMEDIATION', 'PRACTICE_TASK'."
        ),
    )
    label: str = Field(..., description="Human-readable label for the action.")
    url: Optional[str] = Field(
        default=None,
        description="URL for documentation or resource links. Null for non-link actions.",
    )


class BuildCoachPublicResponse(BaseModel):
    """
    Public wire response schema for POST /api/v1/kie/build/coach.

    Backend-approved contract:
      reply        → main coaching reply synthesized from the coaching engine
      suggestions  → ordered list of coaching suggestions / next actions
      action_items → structured action items (docs, next steps, remediation)
    """
    reply: str = Field(
        ...,
        description="Main coaching reply: synthesized from orientation + gap analysis coaching blocks.",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Ordered coaching suggestions derived from guidance and next-step blocks.",
    )
    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Structured action items for Frontend rendering.",
    )


# ---------------------------------------------------------------------------
# INTERNAL Coaching Request (used by BuildCoachService only)
# ---------------------------------------------------------------------------

class BuildCoachRequest(BaseModel):
    """
    Internal request payload for the Contextual Build Coach service.

    Constructed from BuildCoachPublicRequest + memory enrichment.
    Never exposed directly on the public API.
    """

    request_id: str = Field(
        ...,
        min_length=1,
        description="Cross-service tracing identifier (generated internally).",
    )
    learner_id: str = Field(
        ...,
        min_length=1,
        description="Learner identifier from Backend / KIE.",
    )

    # --- Project context (derived from public project_context) ---
    project_title: str = Field(
        default="Build Project",
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
        description="Plain-text summary of what the learner has submitted so far.",
    )
    struggle_description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Learner's own description of where they are stuck.",
    )

    # --- Learner state (from memory engine or Backend) ---
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
# INTERNAL Coaching Response (produced by BuildCoachService)
# ---------------------------------------------------------------------------

class CoachingBlock(BaseModel):
    """
    A single structured coaching unit — domain-adaptive, never raw UI code.
    Internal to the coaching engine; mapped to the public response before returning.
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
        description="Optional renderer metadata.",
    )


class BuildCoachResponse(BaseModel):
    """
    Internal structured coaching response from AI/ML-2 Universal Build Coach.
    Mapped to BuildCoachPublicResponse before returning to the caller.
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
        description="True if the coaching analysis recommends a formal remediation lesson.",
    )
    generated_at: datetime = Field(default_factory=_utc_now)


# ---------------------------------------------------------------------------
# PUBLIC Recommendation Response (GET /api/v1/kie/build/recommend)
# ---------------------------------------------------------------------------

class ProjectRecommendation(BaseModel):
    """
    A single project recommendation — Backend-approved public wire format.

    Field names are the final Backend contract:
      title       ← project title
      description ← domain-adaptive project description
      type        ← artifact type (maps from ArtifactType enum values)
      skills      ← key skills targeted (list of strings)

    Additional enrichment fields (difficulty, rationale, etc.) are included
    for Frontend and AI/ML-1 consumption but are not required by the contract.
    """

    recommendation_id: str = Field(
        ...,
        description="Deterministic short identifier for this recommendation.",
    )
    title: str = Field(..., description="Project title.")
    type: str = Field(
        ...,
        description="Artifact type string (e.g. 'code_project', 'essay'). Maps to ArtifactType.",
    )
    difficulty: BuildDifficulty = Field(
        default=BuildDifficulty.INTERMEDIATE,
        description="Difficulty level: foundational, intermediate, advanced.",
    )
    academic_domain: str = Field(..., description="Academic domain for this recommendation.")
    description: str = Field(
        ...,
        description="Domain-adaptive project description tailored to learner stage and role.",
    )
    rationale: str = Field(
        ...,
        description="Why this project is recommended given the learner's mastery and goals.",
    )
    skills: List[str] = Field(
        default_factory=list,
        description="Key skills targeted by this project.",
    )
    estimated_effort_hours: Optional[float] = Field(
        default=None,
        description="Estimated effort in hours.",
    )
    prerequisite_topics: List[str] = Field(
        default_factory=list,
        description="Prerequisite topics the learner should address first.",
    )


class BuildRecommendContext(BaseModel):
    """
    Learner context used internally by the recommendation engine.
    Constructed from memory engine retrieval; not exposed on the public API.
    """

    learner_id: str
    academic_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    target_role: Optional[str] = None
    completed_milestones: Optional[List[str]] = Field(default=None)
    current_weak_topics: Optional[List[str]] = Field(default=None)
    concept_mastery: Optional[Dict[str, float]] = Field(default=None)
    preferred_artifact_types: Optional[List[ArtifactType]] = Field(default=None)


class BuildRecommendResponse(BaseModel):
    """
    Public wire response for GET /api/v1/kie/build/recommend.
    Backend-approved contract: recommendations list with title, description, type, skills.
    """

    learner_id: str = Field(..., description="Echoed learner identifier.")
    recommendations: List[ProjectRecommendation] = Field(
        ...,
        min_length=1,
        description="Ranked list of domain-adaptive project recommendations.",
    )
    recommendation_rationale: str = Field(
        ...,
        description="Overall reasoning for why these projects were chosen.",
    )
    generated_at: datetime = Field(default_factory=_utc_now)

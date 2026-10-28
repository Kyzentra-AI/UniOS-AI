import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class MasteryTier(str, Enum):
    """Canonical BRD mastery tiers based on mastery percentage (Section 6.4)."""
    WEAK = "weak"             # < 50% (< 0.50)
    DEVELOPING = "developing" # 50% - 79% (0.50 - 0.79)
    PROFICIENT = "proficient" # 80% - 100% (0.80 - 1.00)


class AssessmentAttemptType(str, Enum):
    """Categorization of assessment event for calibrated weighting."""
    DIAGNOSTIC = "diagnostic"
    FORMATIVE = "formative"
    SUMMATIVE = "summative"
    PRACTICE = "practice"
    REASSESSMENT = "reassessment"


class AssessmentEvidence(BaseModel):
    """Structured assessment evidence consumed by AI/ML-2 Mastery Engine (A2-S4-03).
    
    CRITICAL ARCHITECTURAL BOUNDARY:
    Backend owns the authoritative persistent assessment table (attempts, answers, scores, timestamps).
    AI/ML-2 consumes this evidence to compute mastery, detect weaknesses, and trigger remediation.
    """

    learner_id: str = Field(..., description="Target learner identifier")
    topic: str = Field(..., min_length=1, description="Topic being evaluated")
    subtopic: Optional[str] = Field(default=None, description="Optional subtopic specification")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Assessment score between 0.0 (0%) and 1.0 (100%)",
    )
    attempt_type: AssessmentAttemptType = Field(
        default=AssessmentAttemptType.FORMATIVE,
        description="Type of attempt (diagnostic, formative, summative, practice, reassessment)",
    )
    questions_total: int = Field(default=5, ge=1, description="Total number of evaluated questions")
    questions_correct: int = Field(default=3, ge=0, description="Number of correctly answered questions")
    time_spent_seconds: Optional[int] = Field(default=None, ge=0, description="Time spent on assessment in seconds")
    assessment_id: Optional[str] = Field(default=None, description="Backend assessment record ID")
    attempt_id: Optional[str] = Field(default=None, description="Backend attempt record ID")
    answers: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional detailed question-level responses for granular weakness diagnosis",
    )

    @field_validator("learner_id")
    @classmethod
    def validate_learner_id(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("learner_id cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@]+$", cleaned):
            raise ValueError("learner_id contains invalid characters.")
        return cleaned

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("topic cannot be empty or whitespace.")
        return cleaned

    @field_validator("score", mode="before")
    @classmethod
    def parse_and_clamp_score(cls, v: Any) -> float:
        if isinstance(v, str):
            clean_str = v.replace("%", "").strip()
            val = float(clean_str)
            if val > 1.0 and "%" in v:
                val = val / 100.0
            elif val > 1.0 and val <= 100.0:
                val = val / 100.0
        else:
            val = float(v)
        return max(0.0, min(1.0, val))


class RemediationSignal(BaseModel):
    """Measurable remediation signal generated when weakness or struggle is identified (A2-S4-03 / A2-S4-04)."""

    remediation_required: bool = Field(
        ...,
        description="Whether an active pedagogical intervention is required",
    )
    severity: str = Field(
        default="none",
        description="Friction severity: none | low | moderate | high",
    )
    topic: str = Field(..., description="Target topic for remediation")
    recommended_strategy: str = Field(
        default="remediation",
        description="Pedagogical strategy (remediation, prerequisite_review, guided_practice, advancement)",
    )
    recommended_action: str = Field(
        ...,
        description="Specific actionable next step for the learning engine or tutor",
    )
    weak_concepts: List[str] = Field(
        default_factory=list,
        description="Specific sub-concepts or prerequisite areas identified as weak",
    )
    rationale: str = Field(
        ...,
        description="Explainable reasoning connecting performance evidence to remediation decision",
    )


class MasteryUpdateResult(BaseModel):
    """Deterministic result of evaluating assessment evidence and updating mastery (A2-S4-03)."""

    learner_id: str
    topic: str
    previous_mastery: float = Field(ge=0.0, le=1.0)
    new_mastery: float = Field(ge=0.0, le=1.0)
    mastery_tier: MasteryTier
    mastery_percentage: float = Field(ge=0.0, le=100.0)
    is_proficient: bool
    weak_areas: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    remediation_signal: RemediationSignal
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ClosedLoopStep(BaseModel):
    """A stage within the closed-loop remediation lifecycle (A2-S4-04)."""

    step_name: str # e.g. "initial_assessment", "remediation_plan", "remedial_lesson", "reassessment", "outcome"
    status: str    # e.g. "completed", "active", "pending"
    evidence_score: Optional[float] = None
    mastery_level: Optional[float] = None
    strategy_applied: Optional[str] = None
    notes: Optional[str] = None


class ClosedLoopResult(BaseModel):
    """Complete trace of a closed-loop remediation progression (A2-S4-04)."""

    cycle_id: str
    learner_id: str
    topic: str
    initial_score: float
    initial_tier: MasteryTier
    remediation_applied: bool
    remediation_strategy: str
    reassessment_score: Optional[float] = None
    final_tier: MasteryTier
    progression_status: str # "remediated_proficient", "remediation_in_progress", "escalated"
    next_recommended_action: str
    steps: List[ClosedLoopStep] = Field(default_factory=list)

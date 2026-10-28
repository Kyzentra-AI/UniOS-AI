import re
from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from app.schemas.learner import LearnerStage


class ReadinessTier(str, Enum):
    """Categorical classification of learner onboarding readiness."""
    HIGH = "high"
    MODERATE = "moderate"
    NEEDS_SCAFFOLDING = "needs_scaffolding"


def _normalize_string_list(v: Any) -> List[str]:
    """Helper validator to normalize comma-separated strings or lists from LLM outputs."""
    if v is None:
        return []
    if isinstance(v, str):
        cleaned = v.strip()
        if not cleaned:
            return []
        if "," in cleaned or "\n" in cleaned:
            parts = re.split(r"[,;\n]+", cleaned)
            return [p.strip().lstrip("-*• ") for p in parts if p.strip()]
        return [cleaned]
    if isinstance(v, (list, tuple)):
        result = []
        for item in v:
            if isinstance(item, str):
                s = item.strip().lstrip("-*• ")
                if s:
                    result.append(s)
            elif item is not None:
                result.append(str(item).strip())
        return result
    return []


def _normalize_score_0_to_1(v: Any, field_name: str) -> float:
    """Safely normalizes scores to float [0.0, 1.0] without hiding unparseable data."""
    if isinstance(v, (int, float)):
        val = float(v)
    elif isinstance(v, str):
        cleaned = v.strip().rstrip("%")
        try:
            val = float(cleaned)
            # If provided as percentage like 85 or 85%
            if val > 1.0 and val <= 100.0:
                val = val / 100.0
        except ValueError:
            raise ValueError(f"Field '{field_name}' must be a numeric score between 0.0 and 1.0, got '{v}'.")
    else:
        raise ValueError(f"Field '{field_name}' must be a numeric score between 0.0 and 1.0, got {type(v).__name__}.")

    # Clamp slightly out of range values within [0.0, 1.0] (e.g. 1.02 or -0.01 from LLM floating point noise)
    return max(0.0, min(1.0, val))


class SkillAnalysis(BaseModel):
    """Deep analysis of the learner's technical baseline, strengths, and critical gaps."""

    baseline_summary: str = Field(
        default="Synthesized technical baseline evaluation.",
        description="Narrative synthesis of the learner's current technical proficiency",
    )
    proficiency_level: str = Field(
        default="intermediate",
        description="Overall baseline tier: beginner, intermediate, advanced",
    )
    core_strengths: List[str] = Field(
        default_factory=list,
        description="Verified or self-evident strong skill areas",
    )
    critical_skill_gaps: List[str] = Field(
        default_factory=list,
        description="Missing skills or tools required for their target role",
    )

    @field_validator("core_strengths", "critical_skill_gaps", mode="before")
    @classmethod
    def normalize_lists(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)

    @field_validator("proficiency_level", mode="before")
    @classmethod
    def normalize_proficiency(cls, v: Any) -> str:
        if isinstance(v, str):
            cleaned = v.strip().lower()
            if cleaned in ("beginner", "intermediate", "advanced", "foundational", "expert"):
                return cleaned
            return cleaned
        return "intermediate"


class KnowledgeAnalysis(BaseModel):
    """Analysis of conceptual understanding, prerequisite readiness, and theoretical depth."""

    conceptual_depth: str = Field(
        default="applied",
        description="Foundational, applied, practical, or deep theoretical",
    )
    prerequisite_health: str = Field(
        default="solid",
        description="Health status: solid, minor_gaps, needs_remediation",
    )
    theoretical_vs_applied_balance: str = Field(
        default="balanced",
        description="Assessment of balance between theoretical grasp and applied coding",
    )
    recommended_foundation_topics: List[str] = Field(
        default_factory=list,
        description="Priority concepts to reinforce before advanced material",
    )

    @field_validator("recommended_foundation_topics", mode="before")
    @classmethod
    def normalize_topics(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)


class LearningStyleProfile(BaseModel):
    """Cognitive learning preferences and optimal instructional design configuration."""

    dominant_modality: str = Field(
        default="visual",
        description="Primary learning mode: visual, hands-on, theoretical, interactive",
    )
    secondary_modality: Optional[str] = Field(
        default=None,
        description="Supporting mode (e.g. interactive simulations, text-based guides)",
    )
    recommended_pacing: str = Field(
        default="standard",
        description="Recommended learning velocity: accelerated, standard, scaffolded",
    )
    feedback_cadence: str = Field(
        default="Milestone-based feedback",
        description="Optimal frequency for comprehension checks and practice challenges",
    )
    content_format_priorities: List[str] = Field(
        default_factory=list,
        description="Ordered list of preferred instructional formats (e.g. worked_examples, visual_diagrams, practice_tasks)",
    )

    @field_validator("content_format_priorities", mode="before")
    @classmethod
    def normalize_formats(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)


class CareerGoalProfile(BaseModel):
    """Evaluation of the target role, industry alignment, and milestone trajectory."""

    target_role: str = Field(
        default="Software Engineer",
        description="Target role title",
    )
    role_alignment_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Readiness score for the target career path (0.0 to 1.0)",
    )
    key_milestones: List[str] = Field(
        default_factory=list,
        description="Sequenced key milestones to reach role readiness",
    )
    high_priority_competencies: List[str] = Field(
        default_factory=list,
        description="Non-negotiable competencies required for this role",
    )
    estimated_timeline_months: Optional[int] = Field(
        default=None,
        description="Estimated duration in months with current weekly hours",
    )

    @field_validator("role_alignment_score", mode="before")
    @classmethod
    def validate_role_alignment(cls, v: Any) -> float:
        return _normalize_score_0_to_1(v, "role_alignment_score")

    @field_validator("key_milestones", "high_priority_competencies", mode="before")
    @classmethod
    def normalize_milestones(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)

    @field_validator("estimated_timeline_months", mode="before")
    @classmethod
    def normalize_timeline(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return max(1, int(v))
        if isinstance(v, str):
            match = re.search(r"\d+", v)
            if match:
                return max(1, int(match.group(0)))
        return None


class MotivationProfile(BaseModel):
    """Analysis of intrinsic vs extrinsic motivation, engagement hooks, and frustration risks."""

    primary_driver: str = Field(
        default="career_growth",
        description="Main motivation: career_transition, project_creation, academic_excellence, curiosity",
    )
    intrinsic_vs_extrinsic: str = Field(
        default="balanced",
        description="Assessment: mostly_intrinsic, balanced, mostly_extrinsic",
    )
    engagement_hooks: List[str] = Field(
        default_factory=list,
        description="Topics, formats, or gamification hooks that maximize active engagement",
    )
    potential_frustration_triggers: List[str] = Field(
        default_factory=list,
        description="Cognitive overload triggers or blockers to watch out for",
    )
    resilience_advice: str = Field(
        default="Focus on small, consistent learning sprints and worked examples.",
        description="Guidance to sustain momentum and overcome learning friction",
    )

    @field_validator("engagement_hooks", "potential_frustration_triggers", mode="before")
    @classmethod
    def normalize_motivation_lists(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)


class ReadinessAssessment(BaseModel):
    """Overall onboarding readiness rating and entry point recommendation."""

    overall_readiness_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Overall quantitative readiness score (0.0 to 1.0)",
    )
    readiness_tier: ReadinessTier = Field(
        default=ReadinessTier.MODERATE,
        description="Categorical classification: high, moderate, needs_scaffolding",
    )
    recommended_entry_level: str = Field(
        default="intermediate",
        description="Starting tier: foundational, intermediate, advanced",
    )
    onboarding_recommendations: List[str] = Field(
        default_factory=list,
        description="Immediate actionable next steps for the learner",
    )

    @field_validator("overall_readiness_score", mode="before")
    @classmethod
    def validate_readiness_score(cls, v: Any) -> float:
        return _normalize_score_0_to_1(v, "overall_readiness_score")

    @field_validator("readiness_tier", mode="before")
    @classmethod
    def normalize_readiness_tier(cls, v: Any) -> ReadinessTier:
        if isinstance(v, ReadinessTier):
            return v
        if isinstance(v, str):
            cleaned = v.strip().lower().replace("-", "_").replace(" ", "_")
            for tier in ReadinessTier:
                if tier.value == cleaned:
                    return tier
            # Handle common LLM synonyms
            if "scaffold" in cleaned or "need" in cleaned or "low" in cleaned:
                return ReadinessTier.NEEDS_SCAFFOLDING
            if "high" in cleaned or "ready" in cleaned or "expert" in cleaned:
                return ReadinessTier.HIGH
            if "mod" in cleaned or "mid" in cleaned or "inter" in cleaned:
                return ReadinessTier.MODERATE
            raise ValueError(f"Invalid readiness tier: '{v}'")
        raise ValueError(f"readiness_tier must be string or ReadinessTier, got {type(v).__name__}")

    @field_validator("onboarding_recommendations", mode="before")
    @classmethod
    def normalize_recommendations(cls, v: Any) -> List[str]:
        return _normalize_string_list(v)


class LearnerIntelligenceReport(BaseModel):
    """The complete Sprint-2 Learner Intelligence payload returned to Backend/KIE."""

    learner_id: str = Field(
        ...,
        description="Target learner identifier",
    )
    stage: LearnerStage = Field(
        default=LearnerStage.BACHELOR,
        description="Academic development stage",
    )
    target_role: str = Field(
        ...,
        description="Target role used for gap analysis and alignment",
    )
    executive_summary: str = Field(
        default="",
        description="High-level synthesized summary of the learner's overall profile",
    )
    skill_analysis: SkillAnalysis = Field(default_factory=SkillAnalysis)
    knowledge_analysis: KnowledgeAnalysis = Field(default_factory=KnowledgeAnalysis)
    learning_style: LearningStyleProfile = Field(default_factory=LearningStyleProfile)
    career_goals: CareerGoalProfile = Field(default_factory=CareerGoalProfile)
    motivation: MotivationProfile = Field(default_factory=MotivationProfile)
    readiness: ReadinessAssessment = Field(default_factory=ReadinessAssessment)

    @field_validator("stage", mode="before")
    @classmethod
    def normalize_stage(cls, v: Any) -> LearnerStage:
        if isinstance(v, LearnerStage):
            return v
        if isinstance(v, str):
            cleaned = v.strip().lower()
            for stage in LearnerStage:
                if stage.value == cleaned:
                    return stage
            if "bach" in cleaned:
                return LearnerStage.BACHELOR
            if "mast" in cleaned:
                return LearnerStage.MASTER
            if "grad" in cleaned:
                return LearnerStage.GRADUATE
            raise ValueError(f"Invalid learner stage: '{v}'")
        return LearnerStage.BACHELOR

    @field_validator("learner_id")
    @classmethod
    def validate_report_learner_id(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("learner_id cannot be empty.")
        return v.strip()

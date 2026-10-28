import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PreferenceMemory(BaseModel):
    """Learner preferences and cognitive modalities tracked across learning sessions."""

    dominant_modality: str = Field(
        default="visual",
        description="Primary learning mode (visual, hands-on, theoretical, interactive)",
    )
    secondary_modality: Optional[str] = Field(
        default=None,
        description="Secondary supporting learning mode",
    )
    pacing: str = Field(
        default="standard",
        description="Pacing velocity: accelerated, standard, scaffolded",
    )
    practical_vs_theory_ratio: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Ratio of practical applied work vs theoretical reading (0.0 to 1.0)",
    )
    feedback_frequency: str = Field(
        default="milestone_based",
        description="Cadence of feedback: immediate, milestone_based, summary",
    )
    content_format_priorities: List[str] = Field(
        default_factory=lambda: ["worked_examples", "interactive_challenges"],
        description="Ranked list of preferred instructional formats",
    )
    last_updated: datetime = Field(default_factory=_utc_now)

    @field_validator("dominant_modality", "pacing", mode="before")
    @classmethod
    def normalize_strings(cls, v: Any) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return str(v) if v else "standard"


class ConversationMemory(BaseModel):
    """Signals and context captured from learner dialogue and Q&A."""

    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=_utc_now)
    topic: Optional[str] = Field(default=None, description="Topic being discussed")
    question_summary: Optional[str] = Field(default=None, description="Summary of question or inquiry")
    confusion_points: List[str] = Field(default_factory=list, description="Specific concepts causing confusion")
    expressed_sentiment: Optional[str] = Field(
        default="neutral",
        description="Observed sentiment: confident, curious, confused, frustrated, neutral",
    )


class LearningHistoryMemory(BaseModel):
    """Record of completed or attempted learning units and assessments."""

    history_id: str = Field(default_factory=lambda: f"hist_{uuid.uuid4().hex[:8]}")
    topic: str = Field(..., description="Topic of the learning unit")
    lesson_id: Optional[str] = Field(default=None, description="Lesson identifier if applicable")
    status: str = Field(
        default="completed",
        description="Status: completed, in_progress, struggled, skipped",
    )
    assessment_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Normalized assessment score if applicable (0.0 to 1.0)",
    )
    attempts_count: int = Field(default=1, ge=1, description="Number of attempts on this unit")
    time_spent_minutes: Optional[int] = Field(default=None, ge=0, description="Time spent in minutes")
    mastery_level: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Calculated mastery level on this topic (0.0 to 1.0)",
    )
    timestamp: datetime = Field(default_factory=_utc_now)


class ProjectMemory(BaseModel):
    """Hands-on projects attempted or completed by the learner."""

    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., description="Title of the project")
    description: Optional[str] = Field(default=None, description="Short project overview")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies and libraries used")
    status: str = Field(
        default="completed",
        description="Project status: started, in_progress, completed, abandoned",
    )
    complexity: str = Field(
        default="intermediate",
        description="Complexity level: foundational, intermediate, advanced",
    )
    deliverable_url: Optional[str] = Field(default=None, description="Optional repository or demo URL")
    completed_at: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=_utc_now)


class GoalMemory(BaseModel):
    """Career and milestone targets for the learner."""

    primary_target_role: str = Field(default="Software Engineer", description="Target role")
    target_timeline_months: Optional[int] = Field(default=6, ge=1, description="Target timeline in months")
    milestones: List[str] = Field(default_factory=list, description="All milestones required for goal")
    completed_milestones: List[str] = Field(default_factory=list, description="Milestones completed so far")
    secondary_interests: List[str] = Field(default_factory=list, description="Complementary interests or domains")
    goal_change_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological log of role or timeline updates",
    )
    last_updated: datetime = Field(default_factory=_utc_now)


class AchievementMemory(BaseModel):
    """Badges, streaks, and milestone accomplishments earned by the learner."""

    achievement_id: str = Field(default_factory=lambda: f"ach_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., description="Achievement title")
    category: str = Field(
        default="milestone",
        description="Category: mastery, streak, project, milestone",
    )
    description: str = Field(..., description="Achievement description")
    unlocked_at: datetime = Field(default_factory=_utc_now)


class FrictionMemory(BaseModel):
    """Friction, repeated mistakes, and conceptual struggles requiring remediation."""

    friction_id: str = Field(default_factory=lambda: f"fric_{uuid.uuid4().hex[:8]}")
    topic: str = Field(..., description="Topic where struggle was observed")
    struggle_type: str = Field(
        default="conceptual_gap",
        description="Struggle category: conceptual_gap, repeated_mistake, prerequisite_missing, syntax_confusion, cognitive_overload",
    )
    severity: str = Field(
        default="moderate",
        description="Severity: low, moderate, high",
    )
    mistake_count: int = Field(default=1, ge=1, description="Cumulative error or failure count")
    unresolved: bool = Field(default=True, description="True if remediation has not yet resolved this friction")
    recommended_intervention: Optional[str] = Field(
        default=None,
        description="Pedagogical intervention recommended (e.g. foundational scaffolding)",
    )
    first_observed_at: datetime = Field(default_factory=_utc_now)
    last_observed_at: datetime = Field(default_factory=_utc_now)


class LearnerMemory(BaseModel):
    """Top-level structured container for learner memory intelligence."""

    learner_id: str = Field(..., description="Unique learner identifier")
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    preferences: PreferenceMemory = Field(default_factory=PreferenceMemory)
    conversations: List[ConversationMemory] = Field(default_factory=list)
    learning_history: List[LearningHistoryMemory] = Field(default_factory=list)
    projects: List[ProjectMemory] = Field(default_factory=list)
    goals: GoalMemory = Field(default_factory=GoalMemory)
    achievements: List[AchievementMemory] = Field(default_factory=list)
    friction: List[FrictionMemory] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

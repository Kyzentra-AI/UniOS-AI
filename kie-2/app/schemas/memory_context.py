from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.memory import (
    PreferenceMemory,
    FrictionMemory,
    LearningHistoryMemory,
    ProjectMemory,
    GoalMemory,
    AchievementMemory,
    ConversationMemory,
)
from app.schemas.learner import LearnerState


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RelevantMemoryQuery(BaseModel):
    """Query specification to retrieve tailored learner memory for a specific pedagogical decision."""

    learner_id: str = Field(..., min_length=1, description="Target learner identifier")
    topic: Optional[str] = Field(default=None, description="Topic of the upcoming learning activity")
    objective: Optional[str] = Field(default=None, description="Learning objective")
    target_role: Optional[str] = Field(default=None, description="Target career role")
    current_learner_state: Optional[LearnerState] = Field(
        default=None,
        description="Optional current learner state to correlate with memory",
    )
    max_history_items: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum relevant history/friction items to return",
    )


class RelevantMemoryContext(BaseModel):
    """Scoped, relevant memory intelligence returned to AI/ML-1 or pedagogy engines."""

    learner_id: str
    topic: Optional[str] = None
    relevant_preferences: PreferenceMemory
    relevant_friction: List[FrictionMemory] = Field(
        default_factory=list,
        description="Active friction points relating to the queried topic or general struggle",
    )
    relevant_history: List[LearningHistoryMemory] = Field(
        default_factory=list,
        description="Most relevant past attempts or completions",
    )
    relevant_projects: List[ProjectMemory] = Field(
        default_factory=list,
        description="Projects related to the queried topic or active role",
    )
    active_goal: GoalMemory
    recent_achievements: List[AchievementMemory] = Field(default_factory=list)
    recent_conversations: List[ConversationMemory] = Field(default_factory=list)
    detected_strengths: List[str] = Field(default_factory=list)
    detected_weaknesses: List[str] = Field(default_factory=list)
    recommended_pedagogical_mode: Optional[str] = Field(
        default=None,
        description="Recommended presentation mode based on memory (e.g. interactive, visual)",
    )
    rationale: str = Field(
        ...,
        description="Pedagogical justification for the retrieved context and recommended strategy",
    )


class RoadmapStatus(str, Enum):
    """Overall progression status of the learner along their curriculum roadmap."""

    ON_TRACK = "on_track"
    NEEDS_REMEDIATION = "needs_remediation"
    READY_FOR_ADVANCEMENT = "ready_for_advancement"
    GOAL_SHIFTED = "goal_shifted"


class RoadmapRecommendedAction(str, Enum):
    """Next action recommended to AI/ML-1 orchestration for roadmap adaptation."""

    PROCEED_NEXT_TOPIC = "proceed_next_topic"
    INSERT_REMEDIATION = "insert_remediation"
    ADJUST_MILESTONES = "adjust_milestones"
    ACCELERATE = "accelerate"


class RoadmapAdaptationContext(BaseModel):
    """Intelligence contract consumed by AI/ML-1 to adapt curriculum roadmaps."""

    learner_id: str
    status: RoadmapStatus
    recommended_action: RoadmapRecommendedAction
    remediation_topics: List[str] = Field(
        default_factory=list,
        description="Topics requiring remediation before advancing",
    )
    mastered_topics: List[str] = Field(
        default_factory=list,
        description="Verified mastered topics",
    )
    next_recommended_skills: List[str] = Field(
        default_factory=list,
        description="Prioritized upcoming skills or topics",
    )
    rationale: str = Field(..., description="Justification based on learner evidence and memory")
    generated_at: datetime = Field(default_factory=_utc_now)

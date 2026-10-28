import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryEventType(str, Enum):
    """Categorical classification of incoming learner activity and evidence events."""

    LESSON_COMPLETED = "lesson_completed"
    LESSON_SKIPPED = "lesson_skipped"
    ASSESSMENT_ATTEMPT = "assessment_attempt"
    ASSESSMENT_RESULT = "assessment_result"
    REPEATED_MISTAKE = "repeated_mistake"
    TOPIC_MASTERED = "topic_mastered"
    TOPIC_STRUGGLED = "topic_struggled"
    PROJECT_STARTED = "project_started"
    PROJECT_COMPLETED = "project_completed"
    GOAL_CREATED = "goal_created"
    GOAL_UPDATED = "goal_updated"
    ACHIEVEMENT_EARNED = "achievement_earned"
    PREFERENCE_OBSERVED = "preference_observed"
    CONVERSATION_SIGNAL = "conversation_signal"
    FRICTION_SIGNAL = "friction_signal"


class EvidenceSource(str, Enum):
    """Classification of evidence origin to prevent converting weak inference into permanent facts."""

    EXPLICIT = "explicit"      # Declared explicitly by the learner (e.g. settings or chat prompt)
    OBSERVED = "observed"      # Directly recorded from platform interaction (e.g. test score, time spent)
    INFERRED = "inferred"      # Deduced algorithmically or via AI heuristic


class MemoryUpdateEvent(BaseModel):
    """Event representing new learner activity or evidence to update memory intelligence."""

    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:10]}")
    learner_id: str = Field(..., min_length=1, description="Target learner identifier")
    event_type: MemoryEventType = Field(..., description="Type of learning event")
    evidence_source: EvidenceSource = Field(
        default=EvidenceSource.OBSERVED,
        description="Source credibility classification",
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence weighting of this evidence (0.0 to 1.0)",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event specific payload (e.g. topic, score, project details, new role)",
    )
    timestamp: datetime = Field(default_factory=_utc_now)

    @field_validator("confidence_score", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> float:
        if isinstance(v, (int, float)):
            return max(0.0, min(1.0, float(v)))
        return 1.0


class MemoryUpdateResult(BaseModel):
    """Result report returned after processing an update event."""

    success: bool = True
    event_id: str
    learner_id: str
    event_type: MemoryEventType
    updated_facets: List[str] = Field(
        default_factory=list,
        description="Memory facets modified (e.g. ['learning_history', 'friction'])",
    )
    summary: str = Field(..., description="Human-readable description of the update outcome")
    friction_level_updated: bool = False
    new_mastery_level: Optional[float] = None


class MemorySeedResult(BaseModel):
    """Result report returned after seeding learner memory from onboarding intelligence."""

    success: bool = True
    learner_id: str = Field(..., min_length=1, description="Target learner identifier")
    seeded_facets: List[str] = Field(
        default_factory=list,
        description="Memory facets initialized or updated (e.g. ['goals', 'preferences', 'metadata'])",
    )
    updated_facets: List[str] = Field(
        default_factory=list,
        description="Alias for seeded_facets for consistency with MemoryUpdateResult",
    )
    is_new_initialization: bool = Field(
        ...,
        description="True if memory container was freshly initialized; False if learner was already seeded",
    )
    summary: str = Field(
        default="Learner memory successfully seeded from onboarding intelligence report.",
        description="Human-readable outcome description",
    )

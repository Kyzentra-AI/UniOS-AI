from typing import Any

from pydantic import BaseModel, Field


class LearnerEvent(BaseModel):
    """
    One learner activity event supplied by Backend.
    """

    id: str = Field(
        ...,
        min_length=1,
    )

    learner_id: str = Field(
        ...,
        min_length=1,
    )

    event_type: str = Field(
        ...,
        min_length=1,
    )

    entity_type: str = Field(
        ...,
        min_length=1,
    )

    entity_id: str = Field(
        ...,
        min_length=1,
    )

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: str = Field(
        ...,
        min_length=1,
    )


class MemorySummaryRequest(BaseModel):
    """
    Request sent by Backend to summarize recent
    learner activity.
    """

    events: list[LearnerEvent] = Field(
        default_factory=list,
    )
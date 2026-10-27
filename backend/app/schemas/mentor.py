from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with camelCase serialization and loose parsing."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class MentorMode(str, Enum):
    TUTOR = "tutor"
    STUDY_COACH = "study-coach"
    ACCOUNTABILITY = "accountability"
    MOTIVATION = "motivation"


class MentorContext(CamelModel):
    topic: Optional[str] = None
    lesson_id: Optional[str] = None
    roadmap_id: Optional[str] = None
    mission_id: Optional[str] = None


class MentorHistoryMessage(CamelModel):
    role: Literal["user", "mentor"]
    content: str


class MentorChatRequest(CamelModel):
    mode: str = "tutor"  # tutor, study-coach, accountability, motivation
    message: str
    context: Optional[MentorContext] = None
    history: List[MentorHistoryMessage] = []
    conversation_id: Optional[str] = None


class MentorChatResponse(CamelModel):
    reply: str
    conversation_id: str
    created_at: datetime

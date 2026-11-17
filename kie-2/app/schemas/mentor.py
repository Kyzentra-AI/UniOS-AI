"""
UniOS — Mentor Chat Schemas (AI/ML KIE)
Contracts for:
  - POST /api/v1/kie/mentor/chat (Persona-Driven Interactive AI Mentor)
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class MentorMode(str, Enum):
    """Supported mentor persona modes."""
    TUTOR = "tutor"
    STUDY_COACH = "study-coach"
    ACCOUNTABILITY = "accountability"
    MOTIVATION = "motivation"


class ChatMessage(BaseModel):
    """Conversation history message."""
    model_config = ConfigDict(populate_by_name=True)

    role: str = Field(..., description="Message author role ('user' | 'mentor' | 'assistant')")
    content: str = Field(..., description="Text content of the message")


class MentorChatContext(BaseModel):
    """Contextual academic/roadmap metadata passed with mentor chat request."""
    model_config = ConfigDict(populate_by_name=True)

    topic: Optional[str] = Field(default=None, description="Active topic name")
    lesson_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("lesson_id", "lessonId"),
        description="Active lesson ID",
    )
    roadmap_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("roadmap_id", "roadmapId"),
        description="Active roadmap ID",
    )
    mission_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("mission_id", "missionId"),
        description="Active mission ID",
    )
    step_index: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "step_index", "stepIndex", "current_step", "currentStep", "section_index", "sectionIndex", "step"
        ),
        description="Active step/section index in the learning flow (e.g. 1 to 6)",
    )
    step_title: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "step_title", "stepTitle", "section_title", "sectionTitle", "active_step", "activeStep"
        ),
        description="Title of the active step or section",
    )
    step_content: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "step_content", "stepContent", "section_content", "sectionContent", "content"
        ),
        description="Text content of the active step or section",
    )
    total_steps: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices(
            "total_steps", "totalSteps", "total_sections", "totalSections"
        ),
        description="Total number of steps in the active lesson (e.g. 6)",
    )
    subject: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "subject", "subject_title", "subjectTitle", "course", "course_name"
        ),
        description="Course or academic subject name",
    )


class MentorChatRequest(BaseModel):
    """Inbound request from FastAPI Backend to invoke mentor persona."""
    model_config = ConfigDict(populate_by_name=True)

    learner_id: str = Field(
        ...,
        validation_alias=AliasChoices("learner_id", "learnerId"),
        min_length=1,
        description="Learner identifier",
    )
    mode: str = Field(
        default="tutor",
        description="Persona mode: 'tutor' | 'study-coach' | 'accountability' | 'motivation'",
    )
    message: str = Field(..., min_length=1, description="Student's prompt / question to the mentor")
    context: Optional[Union[MentorChatContext, Dict[str, Any]]] = Field(
        default=None, description="Active lesson, roadmap, or mission context"
    )
    history: Optional[List[Union[ChatMessage, Dict[str, Any]]]] = Field(
        default_factory=list, description="Recent conversation turns"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("message cannot be empty or whitespace.")
        return cleaned

    @field_validator("mode")
    @classmethod
    def normalize_mode(cls, v: str) -> str:
        cleaned = v.strip().lower().replace("_", "-")
        valid_modes = {"tutor", "study-coach", "accountability", "motivation"}
        if cleaned not in valid_modes:
            return "tutor"
        return cleaned


class MentorChatResponse(BaseModel):
    """Outbound response containing the persona-aligned response string."""
    model_config = ConfigDict(populate_by_name=True)

    reply: str = Field(..., description="Mentor's persona-aligned markdown response")

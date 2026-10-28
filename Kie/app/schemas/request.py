from typing import Any

from pydantic import BaseModel, Field, field_validator


class LearnerProfile(BaseModel):
    """
    Normalized learner profile received by KIE.

    UniOS Backend owns persistence of this information.
    KIE consumes it for context and orchestration.
    """

    university: str | None = None
    course: str | None = None
    education_level: str | None = None
    semester: int | None = Field(
        default=None,
        ge=1,
    )
    graduation_status: str | None = None

    career_goal: str | None = None
    skills: list[str] = Field(
        default_factory=list
    )
    learning_style: str | None = None

    knowledge_level: str | None = None
    motivation: str | None = None


class LearnerContext(BaseModel):
    """
    Normalized learner-stage context supplied by
    the UniOS Backend to KIE.

    This represents the current learner state needed
    by KIE orchestration.
    """

    current_lesson: str | None = None
    current_topic: str | None = None

    roadmap_id: str | None = None
    mission_id: str | None = None

    learning_session_id: str | None = None

    project_id: str | None = None
    workspace_id: str | None = None

    current_progress: dict[str, Any] = Field(
        default_factory=dict
    )


class KIERequest(BaseModel):
    """
    Main KIE execution request.

    This represents the normalized contract between
    UniOS Backend and KIE.
    """

    user_id: str = Field(
        ...,
        min_length=1,
    )

    session_id: str = Field(
        ...,
        min_length=1,
    )

    role: str = "student"

    task: str = Field(
        ...,
        min_length=1,
    )

    planning_horizon: str | None = None

    intent: str | None = None

    context: dict[str, Any] = Field(
        default_factory=dict
    )

    learner_stage: str | None = None

    learner_profile: LearnerProfile = Field(
        default_factory=LearnerProfile
    )

    learner_context: LearnerContext = Field(
        default_factory=LearnerContext
    )

    tools: list[str] = Field(
        default_factory=list
    )

    constraints: dict[str, Any] = Field(
        default_factory=dict
    )

    trace: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator(
        "user_id",
        "session_id",
        "task",
        "role",
    )
    @classmethod
    def validate_required_strings(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Field cannot be empty or whitespace"
            )

        return value


class AnalyzeContextRequest(BaseModel):
    """
    Sprint 2 onboarding context analysis request.

    Backend sends the initial onboarding context to KIE.
    KIE analyzes it and identifies missing context.
    """

    user_id: str = Field(
        ...,
        min_length=1,
    )

    session_id: str = Field(
        ...,
        min_length=1,
    )

    initial_context: dict[str, Any] = Field(
        default_factory=dict
    )

    @field_validator(
        "user_id",
        "session_id",
    )
    @classmethod
    def validate_required_strings(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Field cannot be empty or whitespace"
            )

        return value


class ContextAnswer(BaseModel):
    """
    One answer to a missing-context question.

    The answer may be a string, a list of values,
    or another JSON-compatible value depending
    on the question type.
    """

    question_id: str = Field(
        ...,
        min_length=1,
    )

    answer: Any

    @field_validator("question_id")
    @classmethod
    def validate_question_id(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "question_id cannot be empty or whitespace"
            )

        return value


class ResolveContextRequest(BaseModel):
    """
    Sprint 2 onboarding context resolution request.

    Backend sends the user's answers to KIE.
    KIE processes the answers and returns refined
    context properties.
    """

    user_id: str = Field(
        ...,
        min_length=1,
    )

    session_id: str = Field(
        ...,
        min_length=1,
    )

    answers: list[ContextAnswer] = Field(
        default_factory=list
    )

    @field_validator(
        "user_id",
        "session_id",
    )
    @classmethod
    def validate_required_strings(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Field cannot be empty or whitespace"
            )

        return value
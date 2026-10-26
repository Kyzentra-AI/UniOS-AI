from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


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
    Context analysis request.

    Supports both:

    1. Legacy Sprint 2 onboarding contract:
       user_id + session_id + initial_context

    2. Current Context V2 Backend contract:
       learner_id + learner + education + preferences
       + syllabus + roadmap + recent_history
       + memory_summary + scope
    """

    # ---------------------------------------------------------
    # Legacy onboarding contract
    # ---------------------------------------------------------

    user_id: str | None = Field(
        default=None,
        min_length=1,
    )

    session_id: str | None = Field(
        default=None,
        min_length=1,
    )

    initial_context: dict[str, Any] = Field(
        default_factory=dict
    )

    # ---------------------------------------------------------
    # Current Context V2 contract
    # ---------------------------------------------------------

    learner_id: str | None = Field(
        default=None,
        min_length=1,
    )

    learner: dict[str, Any] = Field(
        default_factory=dict
    )

    education: dict[str, Any] = Field(
        default_factory=dict
    )

    preferences: dict[str, Any] = Field(
        default_factory=dict
    )

    syllabus: dict[str, Any] = Field(
        default_factory=dict
    )

    roadmap: dict[str, Any] = Field(
        default_factory=dict
    )

    recent_history: list[Any] = Field(
        default_factory=list
    )

    memory_summary: dict[str, Any] | str = Field(
        default_factory=dict
    )

    scope: str | None = None

    # ---------------------------------------------------------
    # Validation / normalization
    # ---------------------------------------------------------

    @field_validator(
        "user_id",
        "session_id",
        "learner_id",
    )
    @classmethod
    def validate_optional_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "Field cannot be empty or whitespace"
            )

        return value

    @model_validator(mode="after")
    def normalize_context(self):
        """
        Convert the new Context V2 payload into the
        existing initial_context structure used by
        ContextEngine.

        This keeps the old ContextEngine logic reusable
        while supporting the new Backend contract.
        """

        is_legacy_request = (
            self.user_id is not None
            or self.session_id is not None
            or bool(self.initial_context)
        )

        is_context_v2_request = (
            self.learner_id is not None
            or bool(self.learner)
            or bool(self.education)
            or bool(self.preferences)
            or bool(self.syllabus)
            or bool(self.roadmap)
            or bool(self.recent_history)
            or bool(self.memory_summary)
            or self.scope is not None
        )

        if not is_legacy_request and not is_context_v2_request:
            raise ValueError(
                "Request must contain either the legacy "
                "onboarding context or the Context V2 payload"
            )

        # If Backend sent the new Context V2 contract,
        # build the initial_context expected by ContextEngine.
        if is_context_v2_request and not self.initial_context:
            normalized_context: dict[str, Any] = {}

            if self.learner:
                normalized_context["learner"] = self.learner

                # Expose commonly checked learner fields
                # at the top level as well.
                for key in (
                    "primary_goal",
                    "target_skills",
                    "skills",
                    "projects",
                    "research",
                    "experience",
                    "inferred_context",
                ):
                    if key in self.learner:
                        normalized_context[key] = self.learner[key]

            if self.education:
                normalized_context["education"] = self.education

            if self.preferences:
                normalized_context["preferences"] = self.preferences

            if self.syllabus:
                normalized_context["syllabus"] = self.syllabus

            if self.roadmap:
                normalized_context["roadmap"] = self.roadmap

            if self.recent_history:
                normalized_context["recent_history"] = (
                    self.recent_history
                )

            if self.memory_summary:
                normalized_context["memory_summary"] = (
                    self.memory_summary
                )

            if self.scope is not None:
                normalized_context["scope"] = self.scope

            if self.learner_id:
                normalized_context["learner_id"] = (
                    self.learner_id
                )

            self.initial_context = normalized_context

        return self


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
    Context resolution request.

    Supports both:

    Legacy:
        user_id + session_id + answers

    Current Backend contract:
        user_id + answers
    """

    user_id: str = Field(
        ...,
        min_length=1,
    )

    # Optional because the current Backend contract
    # does not send session_id.
    session_id: str | None = Field(
        default=None,
        min_length=1,
    )

    answers: list[ContextAnswer] = Field(
        default_factory=list
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "user_id cannot be empty or whitespace"
            )

        return value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "session_id cannot be empty or whitespace"
            )

        return value
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
    semester: int | None = Field(default=None, ge=1)
    graduation_status: str | None = None

    career_goal: str | None = None
    skills: list[str] = Field(default_factory=list)
    learning_style: str | None = None

    knowledge_level: str | None = None
    motivation: str | None = None


class KIERequest(BaseModel):
    """
    Main KIE execution request.

    This represents the normalized contract between
    UniOS and KIE.
    """

    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)

    role: str = "student"

    task: str = Field(..., min_length=1)

    intent: str | None = None

    context: dict[str, Any] = Field(default_factory=dict)

    learner_stage: str | None = None

    learner_profile: LearnerProfile = Field(
        default_factory=LearnerProfile
    )

    tools: list[str] = Field(default_factory=list)

    constraints: dict[str, Any] = Field(default_factory=dict)

    trace: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "user_id",
        "session_id",
        "task",
        "role",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Field cannot be empty or whitespace"
            )

        return value

from pydantic import BaseModel, Field, field_validator


class AchievementEventRequest(BaseModel):
    learner_id: str = Field(..., min_length=1)
    activity_id: str = Field(..., min_length=1)
    activity_type: str = Field(..., min_length=1)
    activity_title: str = Field(..., min_length=1)
    outcome: str = Field(..., min_length=1)
    evidence: list[str] = Field(..., min_length=1)

    @field_validator(
        "learner_id",
        "activity_id",
        "activity_type",
        "activity_title",
        "outcome",
    )
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

    @field_validator("activity_type")
    @classmethod
    def normalize_activity_type(cls, value: str) -> str:
        return value.lower()

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item.strip()]
        if not cleaned:
            raise ValueError(
                "At least one non-empty evidence item is required."
            )
        return cleaned


class AchievementEventResponse(BaseModel):
    event_type: str = "achievement_candidate"
    learner_id: str
    activity_id: str
    activity_type: str
    activity_title: str
    achievement_title: str
    description: str
    evidence: list[str]
    verification_status: str = "pending_backend_verification"
    persistence_owner: str = "backend"

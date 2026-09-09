from typing import Any

from pydantic import BaseModel, Field, field_validator


class KIERequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    task: str = Field(..., min_length=1)
    intent: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    tools: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)

    @field_validator("user_id", "session_id", "task")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty or whitespace")

        return value
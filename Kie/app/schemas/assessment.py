
from typing import Literal

from pydantic import BaseModel, Field, field_validator


QuestionType = Literal[
    "mcq",
    "subjective",
    "viva",
    "case-study",
    "coding",
]


class AssessmentGenerateRequest(BaseModel):
    learner_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    lesson_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    preferred_type: QuestionType = "mcq"
    question_count: int = Field(default=5, ge=1, le=30)
    difficulty: Literal[
        "NOVICE",
        "DEVELOPING",
        "PROFICIENT",
        "MASTERED",
    ] = "DEVELOPING"

    @field_validator(
        "learner_id",
        "session_id",
        "lesson_id",
        "topic",
    )
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class AssessmentOption(BaseModel):
    id: str
    text: str


class AssessmentQuestion(BaseModel):
    id: str
    type: QuestionType
    question: str
    options: list[AssessmentOption] | None = None
    correct_option_id: str | None = None
    explanation: str | None = None
    rubric: dict | None = None
    code: str | None = None
    language: str | None = None


class AssessmentRubric(BaseModel):
    total_points: float = Field(gt=0)
    passing_threshold: float = Field(ge=0, le=1)


class AssessmentGenerateResponse(BaseModel):
    title: str
    type: QuestionType
    instructions: str
    questions: list[AssessmentQuestion]
    rubric: AssessmentRubric

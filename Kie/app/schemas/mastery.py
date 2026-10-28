
from pydantic import BaseModel, Field


class MasteryAnswer(BaseModel):
    question_id: str = Field(min_length=1)
    answer: str
    hints_used: int = Field(default=0, ge=0)
    time_spent_seconds: int = Field(default=0, ge=0)


class MasteryEvaluateRequest(BaseModel):
    learner_id: str = Field(min_length=1)
    assessment_id: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    total_time_spent_seconds: int = Field(default=0, ge=0)
    answers: list[MasteryAnswer] = Field(min_length=1)


class QuestionEvaluation(BaseModel):
    question_id: str
    is_correct: bool
    score: float = Field(ge=0, le=1)
    feedback: str


class MasteryTopicUpdate(BaseModel):
    score: float = Field(ge=0, le=1)
    status: str
    delta: float
    reason: str


class MasteryEvaluateResponse(BaseModel):
    score: float = Field(ge=0, le=1)
    feedback: str
    question_evaluations: list[QuestionEvaluation]
    mastery_updates: dict[str, dict[str, MasteryTopicUpdate]]

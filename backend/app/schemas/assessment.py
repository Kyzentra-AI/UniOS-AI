from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AssessmentOption(BaseModel):
    id: str
    text: str

    model_config = ConfigDict(extra="ignore")


class AssessmentQuestion(BaseModel):
    id: str
    type: str  # mcq, subjective, viva, case-study, coding
    question: str
    options: Optional[List[AssessmentOption]] = None
    code: Optional[str] = None
    language: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class Assessment(BaseModel):
    id: str
    title: str
    type: str  # mcq, subjective, viva, case-study, coding
    instructions: Optional[str] = None
    questions: List[AssessmentQuestion]

    model_config = ConfigDict(extra="ignore")


class AssessmentGenerateRequest(BaseModel):
    session_id: str
    topic: str


class AssessmentAnswer(BaseModel):
    question_id: str
    answer: Any
    hints_used: int = 0
    time_spent_seconds: int = 0

    model_config = ConfigDict(extra="ignore")


class AssessmentAttemptCreate(BaseModel):
    session_id: Optional[str] = None
    assessment_id: str
    topic: str
    answers: List[AssessmentAnswer] = []
    total_time_spent_seconds: int = 0
    is_completed: bool = False

    model_config = ConfigDict(extra="ignore")


class MasteryStatus(str, Enum):
    NOVICE = "NOVICE"
    DEVELOPING = "DEVELOPING"
    PROFICIENT = "PROFICIENT"
    MASTERED = "MASTERED"


class AssessmentResult(BaseModel):
    score: float
    feedback: Optional[str] = None
    mastery_updates: Optional[Dict[str, Any]] = None


class AssessmentAttemptResponse(BaseModel):
    id: str
    session_id: Optional[str] = None
    learner_id: str
    assessment_id: str
    topic: str
    answers: List[Dict[str, Any]] = []
    score: Optional[float] = None
    total_time_spent_seconds: int = 0
    hints_used_count: int = 0
    is_completed: bool = False
    mastery_updates: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore")

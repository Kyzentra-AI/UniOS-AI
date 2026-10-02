from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from enum import Enum

class AssessmentAnswer(BaseModel):
    question_id: str
    answer: Any
    hints_used: int = 0
    time_spent_seconds: int = 0

class AssessmentAttemptCreate(BaseModel):
    session_id: Optional[UUID] = None
    assessment_id: str
    topic: str
    answers: List[AssessmentAnswer]
    total_time_spent_seconds: int
    is_completed: bool = False

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
    id: UUID
    session_id: Optional[UUID] = None
    learner_id: UUID
    assessment_id: str
    topic: str
    answers: List[Dict[str, Any]]
    score: Optional[float] = None
    total_time_spent_seconds: int
    hints_used_count: int
    is_completed: bool
    mastery_updates: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    created_at: datetime

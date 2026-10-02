from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from enum import Enum

class LessonBlockType(str, Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    INTERACTIVE = "INTERACTIVE"
    QUIZ = "QUIZ"
    CODE = "CODE"

class LessonBlock(BaseModel):
    id: str
    type: LessonBlockType | str
    title: Optional[str] = None
    content: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    url: Optional[str] = None
    caption: Optional[str] = None

class Lesson(BaseModel):
    id: str
    title: str
    objective: str
    prerequisites: Optional[List[str]] = None
    blocks: List[LessonBlock]

class SessionStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

class LearningSessionCreate(BaseModel):
    roadmap_id: Optional[UUID] = None
    mission_id: Optional[UUID] = None
    topic: str
    lesson_id: str

class LearningSessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    checkpoint_block_id: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None

class LearningSessionResponse(BaseModel):
    id: UUID
    learner_id: UUID
    roadmap_id: Optional[UUID] = None
    mission_id: Optional[UUID] = None
    topic: str
    lesson_id: str
    status: SessionStatus | str
    checkpoint_block_id: Optional[str] = None
    progress_percentage: int
    lesson_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ContentReferenceQuery(BaseModel):
    syllabus_id: UUID
    topic: str
    keywords: Optional[List[str]] = None

class ContentReferenceResponse(BaseModel):
    topic: str
    references: List[Dict[str, Any]]

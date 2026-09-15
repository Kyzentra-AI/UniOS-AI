from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class MemoryLogCreate(BaseModel):
    concept: str = Field(..., example="Recursion")
    error_type: Optional[str] = Field(None, example="Stack Overflow Error")
    error_frequency_increment: int = Field(1, ge=1)

class MemoryLogResponse(BaseModel):
    memory_id: str
    user_id: str
    concept: str
    error_frequency: int
    last_observed: datetime
    is_archived: bool

    class Config:
        from_attributes = True

class MemoryResetRequest(BaseModel):
    reset_scope: str = Field("implicit_only", example="implicit_only") # implicit_only, all, or concept name
    concept: Optional[str] = None

class ActiveFrictionPoint(BaseModel):
    concept: str
    error_frequency: int
    last_observed: str

class UserPreferencesPayload(BaseModel):
    language: str
    delivery_mode: str
    code_language: str = "Python"

class ContextPayloadResponse(BaseModel):
    student_id: str
    preferences: UserPreferencesPayload
    mastery_summary: Dict[str, float] = {}
    active_friction_points: List[ActiveFrictionPoint] = []
    explicit_directives: List[str] = []

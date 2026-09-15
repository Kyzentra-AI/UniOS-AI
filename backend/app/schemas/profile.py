from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StudentProfileBase(BaseModel):
    degree_program: str = Field(..., example="B.Tech - Computer Science")
    academic_year: str = Field(..., example="3rd Year / Semester 5")
    primary_language: str = Field("English", example="Hindi")
    preferred_modes: List[str] = Field(default_factory=lambda: ["Visual Diagrams"], example=["Visual Diagrams", "Story Mode"])
    primary_career_goal: str = Field(..., example="Core CS Concepts & Algorithmic Problem Solving")

class StudentProfileCreate(StudentProfileBase):
    explicit_directives: Optional[List[str]] = Field(default=None, example=["Always use Python for code examples", "Explain with analogies"])

class StudentProfileUpdate(BaseModel):
    degree_program: Optional[str] = None
    academic_year: Optional[str] = None
    primary_language: Optional[str] = None
    preferred_modes: Optional[List[str]] = None
    primary_career_goal: Optional[str] = None

class StudentProfileResponse(StudentProfileBase):
    profile_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    explicit_directives: List[str] = []

    class Config:
        from_attributes = True


class ExplicitDirectiveCreate(BaseModel):
    directive_text: str = Field(..., example="Always provide code examples in Python.")

class ExplicitDirectiveResponse(BaseModel):
    directive_id: str
    user_id: str
    directive_text: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

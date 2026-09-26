from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SyllabusStatus(str, Enum):
    PROCESSING = "PROCESSING"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

class Subject(BaseModel):
    name: str
    topics: List[str]

class ParsedContent(BaseModel):
    subjects: List[Subject]

class SyllabusResponse(BaseModel):
    id: str
    status: SyllabusStatus
    parsed_content: Optional[dict] = None  # Return as dict or ParsedContent

class SyllabusStatusResponse(BaseModel):
    id: str
    status: SyllabusStatus

class SyllabusUpdate(BaseModel):
    parsed_content: ParsedContent

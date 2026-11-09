from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SyllabusExtractRequest(BaseModel):
    """Inbound request from Backend: POST /api/v1/kie/syllabus/extract"""
    model_config = ConfigDict(extra="ignore")

    syllabus_id: str = Field(..., min_length=1, description="Unique syllabus document identifier")
    text: str = Field(..., min_length=1, description="Raw extracted plain text from PDF")


class SyllabusSubject(BaseModel):
    """Academic subject and its key curriculum topics."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1, description="Subject name (e.g. Data Structures)")
    topics: List[str] = Field(default_factory=list, description="Curriculum topics within subject")


class SyllabusExtractResponse(BaseModel):
    """
    Required response schema from KIE 2: POST /api/v1/kie/syllabus/extract
    Strictly validated by Backend ParsedContent Pydantic model.
    """
    model_config = ConfigDict(extra="ignore")

    subjects: List[SyllabusSubject] = Field(..., min_length=1, description="Non-empty list of parsed subjects")


# Canonical alias matching Backend ParsedContent schema
ParsedContent = SyllabusExtractResponse


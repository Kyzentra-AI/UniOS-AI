from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SyllabusExtractRequest(BaseModel):
    """Inbound request from Backend: POST /api/v1/kie/syllabus/extract"""
    model_config = ConfigDict(extra="ignore")

    syllabus_id: str = Field(..., min_length=1, description="Unique syllabus document identifier")
    text: Optional[str] = Field(default=None, description="Raw extracted plain text from PDF (if text extraction succeeded in Backend)")
    file_base64: Optional[str] = Field(default=None, description="Optional Base64-encoded PDF or image bytes if scanned/image-based")
    pdf_base64: Optional[str] = Field(default=None, description="Alias for file_base64")
    file_url: Optional[str] = Field(default=None, description="Optional public/pre-signed download URL for PDF or image")
    pdf_url: Optional[str] = Field(default=None, description="Alias for file_url")
    filename: Optional[str] = Field(default=None, description="Optional original filename (e.g. syllabus.pdf)")


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


from __future__ import annotations
from datetime import datetime
from enum import Enum
import re
from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with camelCase serialization and loose parsing."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class ResumeSource(str, Enum):
    PROFILE = "profile"
    MANUAL = "manual"


class ResumeStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"


class ATSAnalysisStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class ATSFileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


URL_REGEX = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def _validate_optional_url(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return ""
    if not URL_REGEX.match(s):
        raise ValueError(f"Invalid URL format: '{v}'")
    return s


class ResumeContact(CamelModel):
    full_name: str = Field(..., min_length=1, alias="fullName", description="Full legal name")
    email: EmailStr = Field(..., description="Valid contact email address")
    phone: str = Field(default="", description="Contact phone number")
    location: str = Field(default="", description="City, State / Country")
    linked_in_url: Optional[str] = Field(default="", alias="linkedInUrl", description="LinkedIn Profile URL")
    github_url: Optional[str] = Field(default="", alias="githubUrl", description="GitHub Profile URL")
    portfolio_url: Optional[str] = Field(default="", alias="portfolioUrl", description="Personal Website or Portfolio URL")

    @field_validator("linked_in_url", "github_url", "portfolio_url", mode="before")
    @classmethod
    def check_urls(cls, v: Any) -> Optional[str]:
        return _validate_optional_url(v)


class ResumeEducation(CamelModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    institution: str = Field(default="", description="School or University name")
    degree: str = Field(default="", description="Degree earned e.g. B.Tech, B.S., M.S.")
    field_of_study: str = Field(default="", alias="fieldOfStudy", description="Major / Specialization")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start year or date")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="Graduation year or date")
    grade: Optional[str] = Field(default=None, description="GPA or Grade")


class ResumeExperience(CamelModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: str = Field(default="", description="Company or Organization")
    role: str = Field(default="", description="Job title")
    location: Optional[str] = Field(default="", description="Location or Remote")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start date")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End date")
    is_current: bool = Field(default=False, alias="isCurrent", description="Whether this is the current role")
    description: str = Field(default="", description="Description of achievements, impact, and responsibilities")


class ResumeProject(CamelModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, description="Project title")
    description: str = Field(default="", description="Project overview, problem solved, impact")
    technologies: List[str] = Field(default_factory=list, description="Technologies, libraries, and tools used")
    project_url: Optional[str] = Field(default=None, alias="projectUrl", description="Live demo or code repository")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start date")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End date")

    @field_validator("project_url", mode="before")
    @classmethod
    def check_project_url(cls, v: Any) -> Optional[str]:
        return _validate_optional_url(v)


class ResumeAchievement(CamelModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, description="Achievement or Award title")
    description: str = Field(default="", description="Details and context of the achievement")
    date: Optional[str] = Field(default=None, description="Date of receipt or recognition")


class ResumeDraft(CamelModel):
    contact: ResumeContact
    headline: str = Field(default="", description="Professional headline")
    summary: str = Field(default="", description="Professional summary / executive overview")
    skills: List[str] = Field(default_factory=list, description="Categorized or listed skills")
    education: List[ResumeEducation] = Field(default_factory=list, description="Academic background")
    experience: List[ResumeExperience] = Field(default_factory=list, description="Work experience")
    projects: List[ResumeProject] = Field(default_factory=list, description="Key projects")
    achievements: List[ResumeAchievement] = Field(default_factory=list, description="Honors and achievements")


class ResumePreferences(CamelModel):
    target_role: Optional[str] = Field(default=None, alias="targetRole", description="Target role e.g. Full Stack Engineer")
    tone: Optional[Literal["professional", "concise"]] = Field(default="professional", description="Writing tone")


class ResumeRecord(CamelModel):
    id: str
    learner_id: Optional[str] = Field(default=None, alias="learnerId")
    title: str
    source: ResumeSource = ResumeSource.MANUAL
    status: ResumeStatus = ResumeStatus.DRAFT
    content: ResumeDraft
    preferences: Optional[ResumePreferences] = None
    provider: Optional[Literal["llm", "template", "hybrid"]] = "template"
    created_at: Optional[str] = Field(default=None, alias="createdAt")
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")


# Request & Response Wrappers

class ProfileResumePreviewResponse(CamelModel):
    content: ResumeDraft
    missing_fields: List[str] = Field(default_factory=list, alias="missingFields")


class CreateResumeRequest(CamelModel):
    title: str = Field(..., min_length=1, description="Resume title")
    source: ResumeSource = Field(default=ResumeSource.MANUAL)
    content: ResumeDraft


class UpdateResumeRequest(CamelModel):
    title: Optional[str] = Field(default=None, min_length=1, description="Optional updated title")
    content: ResumeDraft


class GenerateResumeRequest(CamelModel):
    title: str = Field(..., min_length=1, description="Resume title")
    source: ResumeSource = Field(default=ResumeSource.PROFILE)
    content: ResumeDraft
    preferences: Optional[ResumePreferences] = None


class GenerateResumeResponse(CamelModel):
    resume: ResumeRecord
    provider: Literal["llm", "template", "hybrid"] = "hybrid"


class ResumeListResponse(CamelModel):
    items: List[ResumeRecord] = Field(default_factory=list)


class ResumeDetailResponse(CamelModel):
    resume: ResumeRecord


# ==============================================================================
# ATS RESUME CHECKER SCHEMAS
# ==============================================================================

ATSFindingCategory = Literal[
    "structure",
    "content",
    "formatting",
    "contact_information",
    "missing_information",
    "readability",
]

ATSFindingSeverity = Literal["info", "warning", "critical"]


class ATSFinding(CamelModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: ATSFindingCategory
    severity: ATSFindingSeverity
    title: str
    description: str
    recommendation: str


class ATSScore(CamelModel):
    value: float = Field(..., ge=0, description="Calculated score value")
    max_value: float = Field(..., gt=0, alias="maxValue", description="Maximum achievable score")
    methodology: str = Field(default="defined-rule-based-checks", description="Methodology identifier")
    methodology_version: str = Field(default="1.0", alias="methodologyVersion", description="Methodology version")

    @model_validator(mode="after")
    def validate_score(self) -> ATSScore:
        if self.value > self.max_value:
            raise ValueError(f"Score value ({self.value}) cannot exceed max_value ({self.max_value})")
        return self


class ATSDocumentMetadata(CamelModel):
    file_name: str = Field(..., alias="fileName")
    file_type: Literal["pdf", "docx"] = Field(..., alias="fileType")
    page_count: Optional[int] = Field(default=None, alias="pageCount")
    extracted_character_count: int = Field(default=0, alias="extractedCharacterCount")


class ATSAnalysisRecord(CamelModel):
    id: str
    learner_id: Optional[str] = Field(default=None, alias="learnerId")
    status: Literal["completed", "failed"] = "completed"
    document: ATSDocumentMetadata
    score: Optional[ATSScore] = None
    summary: str = ""
    findings: List[ATSFinding] = Field(default_factory=list)
    created_at: Optional[str] = Field(default=None, alias="createdAt")


class ATSAnalysisResponse(CamelModel):
    analysis: ATSAnalysisRecord


class ATSAnalysisHistoryResponse(CamelModel):
    items: List[ATSAnalysisRecord] = Field(default_factory=list)


class APIError(CamelModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = Field(default=None, alias="requestId")

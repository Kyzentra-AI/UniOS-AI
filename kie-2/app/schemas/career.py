"""
UniOS Sprint 7 — Career Intelligence & ATS Schemas (AI/ML-2 KIE)
Tasks:
  - BE-S7-01 & BE-S7-04: AI Resume Builder (POST /api/v1/kie/career/resume/generate)
  - ATS Resume Checker Refinement (POST /api/v1/kie/career/ats/analyze)

ARCHITECTURAL BOUNDARIES & INVARIANTS:
  - Backend owns authoritative persistence, database models, and artifact storage.
  - AI/ML-2 (KIE) owns stateless generative resume tailoring, alignment, and qualitative ATS refinement.
  - Public wire schemas strictly adhere to `launch_aiml_integration_guide.md`.
  - Pydantic models support both documented snake_case and camelCase aliases with `populate_by_name = True`.
  - Unknown fields are safely ignored (`extra = 'ignore'`) consistent with project conventions.
  - Zero database models or ORM dependencies.
"""

from enum import Enum
import re
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ResumeSource(str, Enum):
    """Source of base resume draft."""
    PROFILE = "profile"
    MANUAL = "manual"


class ResumeTone(str, Enum):
    """Writing tone for AI resume generation."""
    PROFESSIONAL = "professional"
    CONCISE = "concise"


class DocumentFileType(str, Enum):
    """Supported document formats for ATS resume parsing."""
    PDF = "pdf"
    DOCX = "docx"


class ATSFindingSeverity(str, Enum):
    """Severity classification for ATS rule findings."""
    INFO = "info"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Resume Generation Sub-Models
# ---------------------------------------------------------------------------

class ResumeContact(BaseModel):
    """Resume contact information supporting snake_case and camelCase aliases."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    full_name: Optional[str] = Field(default=None, alias="fullName", description="Learner full name")
    email: Optional[str] = Field(default=None, description="Contact email address")
    phone: Optional[str] = Field(default=None, description="Phone number with country/area code")
    location: Optional[str] = Field(default=None, description="City, State / Country")
    linkedin_url: Optional[str] = Field(default=None, alias="linkedInUrl", description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, alias="githubUrl", description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, alias="portfolioUrl", description="Personal portfolio URL")


class ResumeEducation(BaseModel):
    """Education history entry."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Unique education entry identifier")
    institution: str = Field(..., min_length=1, description="College or university name")
    degree: Optional[str] = Field(default=None, description="Degree earned or pursued")
    field_of_study: Optional[str] = Field(default=None, alias="fieldOfStudy", description="Major or specialization")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start year or date")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End year or graduation date")
    grade: Optional[str] = Field(default=None, description="GPA or grade honors")


class ResumeExperience(BaseModel):
    """Professional or internship experience entry."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Unique experience entry identifier")
    company: str = Field(..., min_length=1, description="Employer or organization name")
    role: Optional[str] = Field(default=None, description="Job title / position")
    location: Optional[str] = Field(default=None, description="Work location (city, state, or remote)")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start date (e.g. YYYY-MM)")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End date (e.g. YYYY-MM)")
    is_current: Optional[bool] = Field(default=False, alias="isCurrent", description="Whether currently employed")
    description: Optional[str] = Field(default=None, description="Experience bullet points / duties summary")


class ResumeProject(BaseModel):
    """Highlighted technical or academic project entry."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Unique project identifier")
    name: str = Field(..., min_length=1, description="Project name")
    description: Optional[str] = Field(default=None, description="Description of project scope and outcomes")
    technologies: List[str] = Field(default_factory=list, description="Technologies, libraries, and tools used")
    project_url: Optional[str] = Field(default=None, alias="projectUrl", description="Repository or live URL")
    start_date: Optional[str] = Field(default=None, alias="startDate", description="Start date")
    end_date: Optional[str] = Field(default=None, alias="endDate", description="End date")


class ResumeAchievement(BaseModel):
    """Award, certificate, or milestone achievement entry."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Unique achievement identifier")
    title: str = Field(..., min_length=1, description="Certification or award title")
    description: Optional[str] = Field(default=None, description="Achievement detail or issuing authority")
    date: Optional[str] = Field(default=None, description="Date awarded (e.g. YYYY-MM)")


class ResumePreferences(BaseModel):
    """User preferences for resume generation."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    target_role: Optional[str] = Field(default=None, alias="targetRole", description="Target job title or role")
    tone: Optional[ResumeTone] = Field(default=ResumeTone.PROFESSIONAL, description="Resume writing tone")

    @field_validator("tone", mode="before")
    @classmethod
    def normalize_tone(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ResumeDraft(BaseModel):
    """Complete resume draft content payload."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    contact: Optional[ResumeContact] = Field(default_factory=ResumeContact, description="Contact information")
    headline: Optional[str] = Field(default=None, description="Professional headline or title")
    summary: Optional[str] = Field(default=None, description="Executive summary / professional summary")
    skills: List[str] = Field(default_factory=list, description="Categorized or listed core skills")
    education: List[ResumeEducation] = Field(default_factory=list, description="Education history")
    experience: List[ResumeExperience] = Field(default_factory=list, description="Work experience entries")
    projects: List[ResumeProject] = Field(default_factory=list, description="Highlighted projects")
    achievements: List[ResumeAchievement] = Field(default_factory=list, description="Honors, awards, or certifications")


# ---------------------------------------------------------------------------
# Grounding / Career Context Sub-Models (ContextV2)
# ---------------------------------------------------------------------------

class CareerContextLearner(BaseModel):
    """Learner goal and background context from database."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    primary_goal: Optional[str] = Field(default=None, alias="primaryGoal", description="Target career goal")
    skills: List[str] = Field(default_factory=list, description="Learner verified or active skills")
    experience: Optional[str] = Field(default=None, description="Prior background or experience description")


class CareerContextEducation(BaseModel):
    """Academic background from database."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    university: Optional[str] = Field(default=None, description="University name")
    degree_program: Optional[str] = Field(default=None, alias="degreeProgram", description="Degree program name")
    domain: Optional[str] = Field(default=None, description="Academic domain")
    academic_status: Optional[str] = Field(default=None, alias="academicStatus", description="Status (e.g. graduated, enrolled)")


class CareerReadinessProject(BaseModel):
    """Verified build project for career grounding."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Project ID")
    title: str = Field(..., min_length=1, description="Project title")
    description: Optional[str] = Field(default=None, description="Project description")
    skills: List[str] = Field(default_factory=list, description="Associated skills")
    status: Optional[str] = Field(default=None, description="Project completion status")


class CareerReadinessEvidence(BaseModel):
    """Quantified performance evidence for career grounding."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(default=None, description="Evidence ID")
    title: str = Field(..., min_length=1, description="Evidence title")
    description: Optional[str] = Field(default=None, description="Evidence metric or description")
    skills: List[str] = Field(default_factory=list, description="Demonstrated skills")
    created_at: Optional[str] = Field(default=None, alias="createdAt", description="Timestamp of evidence creation")


class CareerReadinessMastery(BaseModel):
    """Validated topic mastery record."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    subject: Optional[str] = Field(default=None, description="Subject domain")
    topic: str = Field(..., min_length=1, description="Mastery topic name")
    mastery_score: float = Field(..., ge=0.0, le=1.0, alias="masteryScore", description="Mastery score between 0.0 and 1.0")
    status: Optional[str] = Field(default=None, description="Mastery tier (e.g. MASTERED, PROFICIENT)")


class CareerReadiness(BaseModel):
    """Career readiness evidence portfolio."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    projects: List[CareerReadinessProject] = Field(default_factory=list, description="Verified build projects")
    evidence: List[CareerReadinessEvidence] = Field(default_factory=list, description="Quantified performance evidence")
    mastery: List[CareerReadinessMastery] = Field(default_factory=list, description="Validated topic mastery records")


class CareerContext(BaseModel):
    """Holistic career context assembled from database (ContextV2)."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    learner_id: str = Field(..., alias="learnerId", min_length=1, description="Learner profile ID")
    learner: Optional[CareerContextLearner] = Field(default=None, description="Learner goal and background context")
    education: Optional[CareerContextEducation] = Field(default=None, description="Academic background")
    career_readiness: Optional[CareerReadiness] = Field(default=None, alias="careerReadiness", description="Career readiness portfolio")

    @field_validator("learner_id")
    @classmethod
    def validate_learner_id_format(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("learner_id cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@/]+$", cleaned):
            raise ValueError("learner_id contains invalid characters.")
        return cleaned


# Canonical alias matching integration guide references
ContextV2 = CareerContext


# ---------------------------------------------------------------------------
# Resume Generation Wire Schemas
# ---------------------------------------------------------------------------

class ResumeGenerateRequest(BaseModel):
    """
    Request schema for POST /api/v1/kie/career/resume/generate.
    Adheres strictly to Section 3.2 of launch_aiml_integration_guide.md.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    request_id: str = Field(..., alias="requestId", min_length=1, description="Distributed tracing identifier (UUID)")
    learner_id: str = Field(..., alias="learnerId", min_length=1, description="Learner profile ID (UUID)")
    title: str = Field(..., min_length=1, description="Resume title provided by user")
    source: ResumeSource = Field(..., description="Source of the base draft ('profile' | 'manual')")
    preferences: Optional[ResumePreferences] = Field(default=None, description="User preferences for role and tone")
    content: ResumeDraft = Field(..., description="Current draft content to tailor")
    career_context: CareerContext = Field(..., alias="careerContext", description="Grounding context from database")

    @field_validator("request_id", "learner_id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("ID cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@/]+$", cleaned):
            raise ValueError("ID contains invalid characters.")
        return cleaned

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class ResumeGenerateResponse(BaseModel):
    """
    Response schema for POST /api/v1/kie/career/resume/generate.
    Adheres strictly to Section 3.4 of launch_aiml_integration_guide.md.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    content: ResumeDraft = Field(..., description="Synthesized, tailored, and grounded resume draft")


# ---------------------------------------------------------------------------
# ATS Analysis Sub-Models
# ---------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """Metadata of uploaded resume document analyzed by ATS engine."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    file_name: str = Field(..., alias="fileName", min_length=1, description="Uploaded file name")
    file_type: DocumentFileType = Field(..., alias="fileType", description="Document type: 'pdf' | 'docx'")
    page_count: Optional[int] = Field(default=None, alias="pageCount", ge=0, description="Total document pages")
    extracted_character_count: Optional[int] = Field(
        default=None, alias="extractedCharacterCount", ge=0, description="Extracted plain-text character count"
    )

    @field_validator("file_type", mode="before")
    @classmethod
    def normalize_file_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class RuleScore(BaseModel):
    """Deterministic score output from Backend rule engine v1.0."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    value: float = Field(..., ge=0.0, le=100.0, description="Deterministic rule score value (0 to 100)")
    max_value: float = Field(default=100.0, alias="maxValue", ge=0.0, description="Maximum possible score")
    methodology: str = Field(default="defined-rule-based-checks", description="Scoring methodology identifier")
    methodology_version: Optional[str] = Field(default="1.0", alias="methodologyVersion", description="Methodology version")

    @field_validator("value")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        if v < 0.0 or v > 100.0:
            raise ValueError("Rule score value must be between 0.0 and 100.0.")
        return float(v)


class RuleFinding(BaseModel):
    """Deterministic or LLM-refined ATS rule finding."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(..., min_length=1, description="Finding identifier (e.g. f1-contact)")
    category: str = Field(..., min_length=1, description="Finding category (e.g. contact_information)")
    severity: ATSFindingSeverity = Field(..., description="Finding severity: info | suggestion | warning | critical")
    title: str = Field(..., min_length=1, description="Finding headline or title")
    description: str = Field(..., description="Detailed description of the finding")
    recommendation: Optional[str] = Field(default=None, description="Actionable recommendation for improvement")

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


# Canonical alias
ATSFinding = RuleFinding


# ---------------------------------------------------------------------------
# ATS Analysis Wire Schemas
# ---------------------------------------------------------------------------

class ATSAnalyzeRequest(BaseModel):
    """
    Request schema for POST /api/v1/kie/career/ats/analyze.
    Adheres strictly to Section 4.2 of launch_aiml_integration_guide.md.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    request_id: str = Field(..., alias="requestId", min_length=1, description="Trace ID (UUID)")
    learner_id: str = Field(..., alias="learnerId", min_length=1, description="Learner profile ID (UUID)")
    document: DocumentMetadata = Field(..., description="Document metadata")
    extracted_text: str = Field(..., alias="extractedText", min_length=1, description="Raw extracted plain text")
    rule_score: RuleScore = Field(..., alias="ruleScore", description="Deterministic rule score output")
    rule_findings: List[RuleFinding] = Field(default_factory=list, alias="ruleFindings", description="Initial rule-based findings")

    @field_validator("request_id", "learner_id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("ID cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z0-9_\-\.:@/]+$", cleaned):
            raise ValueError("ID contains invalid characters.")
        return cleaned


class ATSAnalyzeResponse(BaseModel):
    """
    Response schema for POST /api/v1/kie/career/ats/analyze.
    Adheres strictly to Section 4.4 of launch_aiml_integration_guide.md.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    summary: str = Field(..., min_length=1, description="Personalized qualitative summary and actionable feedback")
    findings: List[RuleFinding] = Field(default_factory=list, description="Refined and enriched rule findings")

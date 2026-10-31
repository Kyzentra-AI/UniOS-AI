
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ResumePreferences(APIModel):
    targetRole: str | None = None
    tone: Literal["professional", "concise"] = "professional"


class ResumeGenerateRequest(APIModel):
    request_id: str = Field(alias="requestId", min_length=1)
    learner_id: str = Field(alias="learnerId", min_length=1)
    title: str = Field(min_length=1)
    source: Literal["profile", "manual"]
    preferences: ResumePreferences = Field(
        default_factory=ResumePreferences
    )
    content: dict[str, Any]
    career_context: dict[str, Any] = Field(alias="careerContext")


class ResumeGenerateResponse(APIModel):
    content: dict[str, Any]


class ATSFinding(APIModel):
    id: str
    category: str
    severity: Literal["info", "suggestion", "warning", "critical"]
    title: str
    description: str
    recommendation: str | None = None


class ATSRuleScore(APIModel):
    value: float = Field(ge=0, le=100)
    maxValue: float = Field(default=100.0, ge=1)
    methodology: str = "defined-rule-based-checks"
    methodologyVersion: str = "1.0"


class ATSDocumentMetadata(APIModel):
    fileName: str = Field(min_length=1)
    fileType: Literal["pdf", "docx"]
    pageCount: int = Field(default=0, ge=0)
    extractedCharacterCount: int = Field(default=0, ge=0)


class ATSAnalyzeRequest(APIModel):
    request_id: str = Field(alias="requestId", min_length=1)
    learner_id: str = Field(alias="learnerId", min_length=1)
    document: ATSDocumentMetadata
    extracted_text: str = Field(alias="extractedText")
    rule_score: ATSRuleScore = Field(alias="ruleScore")
    rule_findings: list[ATSFinding] = Field(alias="ruleFindings")


class ATSAnalyzeResponse(APIModel):
    summary: str
    findings: list[ATSFinding]

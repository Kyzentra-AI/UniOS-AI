"""
UniOS Sprint 7 — Career Intelligence & ATS Endpoints (AI/ML-2 KIE)
Tasks:
  - BE-S7-01 & BE-S7-04: AI Resume Generator (POST /api/v1/kie/career/resume/generate)
  - ATS Resume Checker Qualitative Refinement (POST /api/v1/kie/career/ats/analyze)

Registered on the /kie/career prefix in api.py.
Route handlers are thin wrappers delegating entirely to CareerService.
Stateless, zero database access, zero ORM models.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.career import (
    ATSAnalyzeRequest,
    ATSAnalyzeResponse,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
)
from app.services.career_service import CareerService, get_career_service
from app.services.llm_provider import LLMParseError, LLMProviderError

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /resume/generate
# ---------------------------------------------------------------------------

@router.post(
    "/resume/generate",
    response_model=ResumeGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Grounded & Tailored Resume Draft (BE-S7-01 & BE-S7-04)",
    description=(
        "Synthesizes and tailors a professional resume draft based on candidate's base draft "
        "and verified career evidence from ContextV2 database grounding. "
        "Strictly anti-hallucinatory: never invents degrees, employers, projects, or metrics. "
        "Missing contact details in draft remain null. Preserves original entry IDs."
    ),
    responses={
        200: {
            "description": "Successfully generated grounded and tailored resume draft.",
            "model": ResumeGenerateResponse,
        },
        422: {
            "description": "Validation error: Malformed or invalid resume request payload.",
        },
        429: {
            "description": "Too Many Requests: LLM provider rate limit exceeded.",
        },
        502: {
            "description": "Bad Gateway: LLM provider unavailable or response could not be validated.",
        },
        504: {
            "description": "Gateway Timeout: LLM provider connection timeout.",
        },
    },
)
def generate_resume(
    request: ResumeGenerateRequest,
    service: CareerService = Depends(get_career_service),
) -> ResumeGenerateResponse:
    """
    AI/ML-2 capability interface: Tailors authentic resume draft targeting specified role and tone.
    """
    try:
        return service.generate_resume(request)
    except LLMParseError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Resume generation response could not be parsed: {err.message}",
        )
    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected internal error during resume generation: {str(err)}",
        )


# ---------------------------------------------------------------------------
# POST /ats/analyze
# ---------------------------------------------------------------------------

@router.post(
    "/ats/analyze",
    response_model=ATSAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="ATS Resume Analysis Feedback Refinement",
    description=(
        "Enriches deterministic rule-based checks with personalized qualitative executive summary "
        "and actionable recommendations (Google XYZ formula). "
        "Preserves deterministic rule score and methodology strictly without alteration. "
        "Preserves original finding IDs and finding counts."
    ),
    responses={
        200: {
            "description": "Successfully refined ATS analysis with qualitative feedback.",
            "model": ATSAnalyzeResponse,
        },
        422: {
            "description": "Validation error: Malformed or invalid ATS request payload.",
        },
        429: {
            "description": "Too Many Requests: LLM provider rate limit exceeded.",
        },
        502: {
            "description": "Bad Gateway: LLM provider unavailable or response could not be validated.",
        },
        504: {
            "description": "Gateway Timeout: LLM provider connection timeout.",
        },
    },
)
def analyze_ats(
    request: ATSAnalyzeRequest,
    service: CareerService = Depends(get_career_service),
) -> ATSAnalyzeResponse:
    """
    AI/ML-2 capability interface: Generates qualitative executive summary and enriches rule findings.
    """
    try:
        return service.analyze_ats(request)
    except LLMParseError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ATS analysis response could not be parsed: {err.message}",
        )
    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected internal error during ATS analysis: {str(err)}",
        )

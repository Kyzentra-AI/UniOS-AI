"""
API Endpoints for Sprint 7 Launch: AI Resume Builder and ATS Resume Checker.
Router prefix: /api/v1/launch
Provides strictly typed, validated endpoints matching the frontend contract.
"""
from __future__ import annotations
from io import BytesIO
import logging
from typing import Optional
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.launch import (
    APIError,
    ATSAnalysisHistoryResponse,
    ATSAnalysisResponse,
    CreateResumeRequest,
    GenerateResumeRequest,
    GenerateResumeResponse,
    ProfileResumePreviewResponse,
    ResumeDetailResponse,
    ResumeListResponse,
    UpdateResumeRequest,
)
from app.services.launch.ats_service import ats_service
from app.services.launch.career_context_service import career_context_service
from app.services.launch.resume_service import resume_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/launch", tags=["Launch"])


def _get_learner_id(user_id: str) -> str:
    """Helper to fetch the learner_profile id for an authenticated user."""
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APIError(
                code="LEARNER_PROFILE_NOT_FOUND",
                message="Learner profile not found for authenticated user.",
            ).model_dump(by_alias=True),
        )
    return str(res.data[0]["id"])


# ==============================================================================
# RESUME BUILDER ENDPOINTS (BE-S7-01 & BE-S7-04)
# ==============================================================================

@router.get("/resumes/profile-preview", response_model=ProfileResumePreviewResponse)
async def get_profile_resume_preview(current_user: dict = Depends(get_current_user)):
    """
    Returns a read-only resume draft preview aggregated from the learner profile,
    academic credentials, mastery topics, and completed build projects/evidence.
    Includes missing field hints. Does not mutate profile tables.
    """
    return career_context_service.get_profile_resume_preview(current_user["user_id"])


@router.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(current_user: dict = Depends(get_current_user)):
    """Lists all resumes created by or generated for the authenticated learner."""
    learner_id = _get_learner_id(current_user["user_id"])
    return resume_service.list_resumes(learner_id)


@router.post("/resumes", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    request: CreateResumeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Creates a new resume draft owned by the authenticated learner."""
    learner_id = _get_learner_id(current_user["user_id"])
    return resume_service.create_resume(learner_id, request)


@router.get("/resumes/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieves a specific resume with learner ownership verification."""
    learner_id = _get_learner_id(current_user["user_id"])
    return resume_service.get_resume(learner_id, resume_id)


@router.patch("/resumes/{resume_id}", response_model=ResumeDetailResponse)
async def update_resume(
    resume_id: str,
    request: UpdateResumeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Updates an existing resume draft owned by the authenticated learner."""
    learner_id = _get_learner_id(current_user["user_id"])
    return resume_service.update_resume(learner_id, resume_id, request)


@router.post("/resumes/generate", response_model=GenerateResumeResponse)
async def generate_resume(
    request: GenerateResumeRequest,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    current_user: dict = Depends(get_current_user),
):
    """
    Assembles holistic career context, invokes KIE for resume generation,
    enforces anti-hallucination verification, persists the result, and returns the generated resume.
    """
    learner_id = _get_learner_id(current_user["user_id"])
    request_id = x_request_id or str(uuid.uuid4())
    return await resume_service.generate_resume(learner_id, request, request_id)


@router.post("/resumes/{resume_id}/export")
async def export_resume_pdf(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Renders the specified resume into an ATS-friendly single-column PDF byte stream.
    Returns a downloadable PDF attachment.
    """
    learner_id = _get_learner_id(current_user["user_id"])
    pdf_bytes = resume_service.export_resume_pdf(learner_id, resume_id)
    slug = f"resume_{resume_id[:8]}"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{slug}.pdf"'},
    )


# ==============================================================================
# ATS RESUME CHECKER ENDPOINTS
# ==============================================================================

@router.post("/ats/analyses", response_model=ATSAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    current_user: dict = Depends(get_current_user),
):
    """
    Synchronously analyzes an uploaded resume (PDF or DOCX).
    Validates file size (max 5 MB) and magic bytes. Extracts text, runs deterministic scoring
    under methodology 'defined-rule-based-checks' v1.0, optionally enriches via KIE with
    graceful degradation, and persists analysis history.
    """
    learner_id = _get_learner_id(current_user["user_id"])
    request_id = x_request_id or str(uuid.uuid4())
    return await ats_service.analyze_resume(learner_id, file, request_id)


@router.get("/ats/analyses/{analysis_id}", response_model=ATSAnalysisResponse)
async def get_ats_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieves an existing ATS analysis record with strict learner ownership verification."""
    learner_id = _get_learner_id(current_user["user_id"])
    return ats_service.get_analysis(learner_id, analysis_id)


@router.get("/ats/analyses", response_model=ATSAnalysisHistoryResponse)
async def list_ats_analyses(
    current_user: dict = Depends(get_current_user),
):
    """Lists ATS analysis history records for the authenticated learner."""
    learner_id = _get_learner_id(current_user["user_id"])
    return ats_service.list_analyses(learner_id)

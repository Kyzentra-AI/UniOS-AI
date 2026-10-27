from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.assessment import (
    Assessment,
    AssessmentAttemptCreate,
    AssessmentAttemptResponse,
    AssessmentGenerateRequest,
)
from app.services.assessment_service import assessment_service

router = APIRouter(prefix="/api/v1/assessments", tags=["Assessments"])


def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner profile not found")
    return str(res.data[0]["id"])


@router.post(
    "/generate",
    response_model=Assessment,
    summary="Generate or retrieve an assessment",
    description="Generates an assessment for the session/topic if none exists; otherwise returns the existing persisted assessment directly.",
)
async def generate_assessment(
    payload: AssessmentGenerateRequest,
    current_user: dict = Depends(get_current_user),
) -> Assessment:
    learner_id = _get_learner_id(current_user["user_id"])
    assessment = await assessment_service.get_or_generate_assessment(
        learner_id=learner_id,
        session_id=payload.session_id,
        topic=payload.topic,
    )
    return Assessment(**assessment)


@router.post(
    "/attempts",
    response_model=AssessmentAttemptResponse,
    summary="Submit an assessment attempt",
    description="Submits and evaluates an assessment attempt server-side, returning score, feedback, hints, and mastery updates.",
)
async def submit_assessment_attempt(
    attempt_in: AssessmentAttemptCreate,
    current_user: dict = Depends(get_current_user),
) -> AssessmentAttemptResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    attempt = await assessment_service.record_attempt(learner_id, attempt_in)
    return AssessmentAttemptResponse(**attempt)

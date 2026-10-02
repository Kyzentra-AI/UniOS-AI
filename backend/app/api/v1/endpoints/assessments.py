from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.schemas.assessment import AssessmentAttemptCreate, AssessmentAttemptResponse
from app.services.assessment_service import assessment_service
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/api/v1/assessments", tags=["Assessments"])

def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return res.data[0]["id"]

@router.post("/attempts", response_model=AssessmentAttemptResponse)
async def submit_assessment_attempt(
    attempt_in: AssessmentAttemptCreate,
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    attempt = await assessment_service.record_attempt(learner_id, attempt_in)
    return attempt

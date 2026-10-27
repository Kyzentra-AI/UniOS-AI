from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.mentor.mentor_service import mentor_service

router = APIRouter(prefix="/api/v1/mentor", tags=["Mentor"])


def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found for authenticated user.",
        )
    return str(res.data[0]["id"])


@router.post(
    "/chat",
    response_model=MentorChatResponse,
    summary="Mentor chat",
    description="Generates persona-aligned mentorship reply for tutor, study-coach, accountability, or motivation modes.",
)
async def mentor_chat(
    payload: MentorChatRequest,
    current_user: dict = Depends(get_current_user),
) -> MentorChatResponse:
    learner_id = _get_learner_id(current_user["user_id"])
    return await mentor_service.chat(learner_id, payload)

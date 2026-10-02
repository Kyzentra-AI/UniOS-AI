import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException
from app.core.deps import get_current_user
from app.schemas.learning import (
    LearningSessionCreate, 
    LearningSessionUpdate, 
    LearningSessionResponse,
    ContentReferenceQuery,
    ContentReferenceResponse,
    Lesson
)
from app.services.learning_session_service import learning_session_service
from app.services.kie_gateway_service import kie_gateway_service
from app.services.content_reference_service import content_reference_service
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/api/v1/learning", tags=["Learning"])

def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return res.data[0]["id"]

@router.post("/sessions", response_model=LearningSessionResponse)
async def start_or_resume_session(
    session_in: LearningSessionCreate, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    session = learning_session_service.create_or_get_session(learner_id, session_in)
    return session

@router.get("/sessions/{session_id}", response_model=LearningSessionResponse)
async def get_session(
    session_id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    session = learning_session_service.get_session(session_id, learner_id)
    return session

@router.patch("/sessions/{session_id}/checkpoint", response_model=LearningSessionResponse)
async def update_checkpoint(
    session_id: str,
    update_in: LearningSessionUpdate,
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    session = learning_session_service.update_checkpoint(session_id, learner_id, update_in)
    return session

@router.post("/sessions/{session_id}/generate-lesson", response_model=Lesson)
async def generate_lesson(
    session_id: str,
    payload: Dict[str, Any],
    x_request_id: str = Header(default_factory=lambda: str(uuid.uuid4())),
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    lesson = await kie_gateway_service.generate_lesson(learner_id, session_id, x_request_id, payload)
    return lesson

@router.get("/references", response_model=ContentReferenceResponse)
async def get_references(
    syllabus_id: str,
    topic: str,
    keywords: str = None,
    current_user: dict = Depends(get_current_user)
):
    kw_list = keywords.split(",") if keywords else []
    query = ContentReferenceQuery(syllabus_id=syllabus_id, topic=topic, keywords=kw_list)
    return content_reference_service.get_references(query)

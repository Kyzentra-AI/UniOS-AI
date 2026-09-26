from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.services.event_service import event_service
from app.schemas.mission import MissionResponse, MissionStatus
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/v1/missions", tags=["Missions"])

def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return res.data[0]["id"]

def _verify_mission_ownership(mission_id: str, learner_id: str) -> dict:
    res = supabase_admin.table("missions").select("*, roadmaps(learner_id)").eq("id", mission_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Mission not found")
    mission = res.data[0]
    if mission["roadmaps"]["learner_id"] != learner_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return mission

@router.get("", response_model=List[MissionResponse])
async def list_missions(roadmap_id: str = None, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    query = supabase_admin.table("missions").select("*, roadmaps!inner(learner_id)").eq("roadmaps.learner_id", learner_id)
    if roadmap_id:
        query = query.eq("roadmap_id", roadmap_id)
    res = query.execute()
    return res.data

@router.get("/{id}", response_model=MissionResponse)
async def get_mission(id: str, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    mission = _verify_mission_ownership(id, learner_id)
    return mission

@router.post("/{id}/start", response_model=MissionResponse)
async def start_mission(id: str, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    mission = _verify_mission_ownership(id, learner_id)
    
    if mission["status"] not in ["PENDING", "DEFERRED"]:
        raise HTTPException(status_code=400, detail="Mission cannot be started from current state")
        
    updated = supabase_admin.table("missions").update({
        "status": "IN_PROGRESS",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    event_service.record_event(learner_id, "MISSION_STARTED", "MISSION", id)
    return updated.data[0]

@router.post("/{id}/complete", response_model=MissionResponse)
async def complete_mission(id: str, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    mission = _verify_mission_ownership(id, learner_id)
    
    if mission["status"] != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Mission must be IN_PROGRESS to complete")
        
    now = datetime.utcnow().isoformat()
    updated = supabase_admin.table("missions").update({
        "status": "COMPLETED",
        "updated_at": now,
        "completed_at": now
    }).eq("id", id).execute()
    
    event_service.record_event(learner_id, "MISSION_COMPLETED", "MISSION", id)
    return updated.data[0]

@router.post("/{id}/defer", response_model=MissionResponse)
async def defer_mission(id: str, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    mission = _verify_mission_ownership(id, learner_id)
    
    updated = supabase_admin.table("missions").update({
        "status": "DEFERRED",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    event_service.record_event(learner_id, "MISSION_DEFERRED", "MISSION", id)
    return updated.data[0]

@router.post("/{id}/skip", response_model=MissionResponse)
async def skip_mission(id: str, current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    mission = _verify_mission_ownership(id, learner_id)
    
    updated = supabase_admin.table("missions").update({
        "status": "SKIPPED",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    event_service.record_event(learner_id, "MISSION_SKIPPED", "MISSION", id)
    return updated.data[0]

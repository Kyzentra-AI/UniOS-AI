from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.history import LearningHistoryResponse, ProjectHistoryResponse, CareerHistoryResponse, AchievementResponse
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/api/v1/history", tags=["History & Achievements"])

@router.get("/learning", response_model=List[LearningHistoryResponse])
async def get_learning_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("learning_history").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=List[ProjectHistoryResponse])
async def get_project_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("project_history").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/career", response_model=List[CareerHistoryResponse])
async def get_career_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("career_history").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("achievements").select("*").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

import datetime
from datetime import timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.planning import RoadmapResponse, GoalResponse, MissionResponse
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.core.kie_client import generate_roadmap_mock

router = APIRouter(prefix="/api/v1/planning", tags=["Planning"])

@router.get("/roadmaps", response_model=List[RoadmapResponse])
async def get_roadmaps(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("roadmaps").select("*, goals(*, missions(*))").eq("user_id", user_id).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(current_user: dict = Depends(get_current_user)):
    """
    Triggers the KIE engine to generate a roadmap. For now, uses dummy KIE logic and saves it to DB.
    """
    user_id = current_user["user_id"]
    now = datetime.datetime.now(timezone.utc).isoformat()
    
    try:
        # Get user profile for context
        profile_res = supabase_admin.table("student_profiles").select("*").eq("user_id", user_id).execute()
        user_profile = profile_res.data[0] if profile_res.data else {}
        
        # Call mock KIE
        kie_plan = await generate_roadmap_mock(user_profile)
        
        # Save Roadmap
        roadmap_res = supabase_admin.table("roadmaps").insert({
            "user_id": user_id,
            "title": kie_plan["title"],
            "type": kie_plan["type"],
            "created_at": now,
            "updated_at": now
        }).execute()
        roadmap = roadmap_res.data[0]
        roadmap_id = roadmap["id"]
        
        # Save Goals and Missions
        for goal_data in kie_plan.get("goals", []):
            goal_res = supabase_admin.table("goals").insert({
                "user_id": user_id,
                "roadmap_id": roadmap_id,
                "title": goal_data["title"],
                "type": goal_data["type"],
                "description": goal_data.get("description"),
                "created_at": now
            }).execute()
            goal = goal_res.data[0]
            goal_id = goal["id"]
            
            missions_to_insert = []
            for mission_data in goal_data.get("missions", []):
                missions_to_insert.append({
                    "user_id": user_id,
                    "goal_id": goal_id,
                    "title": mission_data["title"],
                    "type": mission_data["type"],
                    "content": mission_data.get("content"),
                    "xp_reward": mission_data.get("xp_reward", 10),
                    "created_at": now
                })
            if missions_to_insert:
                supabase_admin.table("missions").insert(missions_to_insert).execute()
                
        # Return full structure
        final_res = supabase_admin.table("roadmaps").select("*, goals(*, missions(*))").eq("id", roadmap_id).execute()
        return final_res.data[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/missions/{mission_id}/status")
async def update_mission_status(mission_id: str, status: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("missions").update({"status": status}).eq("id", mission_id).eq("user_id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Mission not found")
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

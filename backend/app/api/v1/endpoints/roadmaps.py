from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.roadmap import RoadmapRequest
from app.services.roadmap_service import roadmap_service

router = APIRouter(prefix="/api/v1/roadmaps", tags=["Roadmaps"])

@router.post("")
async def generate_roadmap(request: RoadmapRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Get learner id
    learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not learner_res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    learner_id = learner_res.data[0]["id"]
    
    # Verify syllabus ownership and status
    syl_res = supabase_admin.table("syllabus_documents").select("*").eq("id", request.syllabus_id).execute()
    if not syl_res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    syl = syl_res.data[0]
    if syl["learner_id"] != learner_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if syl["status"] != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Syllabus must be CONFIRMED before roadmap generation")
        
    # Kick off background generation
    background_tasks.add_task(roadmap_service.generate_roadmap_background, learner_id, request.scope.value, request.syllabus_id)
    
    return {"message": "Roadmap generation started", "status": "PROCESSING"}

@router.get("/current")
async def get_current_roadmap(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Get learner id
    learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not learner_res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    learner_id = learner_res.data[0]["id"]
    
    # Fetch active roadmap
    roadmap_res = supabase_admin.table("roadmaps").select("*").eq("learner_id", learner_id).eq("status", "ACTIVE").order("created_at", desc=True).limit(1).execute()
    
    if not roadmap_res.data:
        # It's perfectly normal for a user to not have a roadmap yet, frontend handles null.
        return {"roadmap": None}
        
    roadmap_db = roadmap_res.data[0]
    roadmap_id = roadmap_db["id"]
    
    # Fetch associated missions
    missions_res = supabase_admin.table("missions").select("*").eq("roadmap_id", roadmap_id).order("sequence").execute()
    missions = missions_res.data if missions_res.data else []
    
    # Construct response
    roadmap = {
        "id": roadmap_id,
        "version": roadmap_db.get("version", 1),
        "scope": roadmap_db.get("scope"),
        "status": roadmap_db.get("status"),
        "scope_data": roadmap_db.get("plan_data", {}),
        "missions": missions,
        "created_at": roadmap_db.get("created_at"),
        "updated_at": roadmap_db.get("updated_at")
    }
    
    return {"roadmap": roadmap}

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

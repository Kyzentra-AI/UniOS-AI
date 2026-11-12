from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.roadmap import RoadmapRequest
from app.services.roadmap_service import roadmap_service
from typing import Optional

router = APIRouter(prefix="/api/v1/roadmaps", tags=["Roadmaps"])

@router.post("")
async def generate_roadmap(
    request: RoadmapRequest, 
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    
    # 1. Resolve learner_id
    learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not learner_res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    learner_id = learner_res.data[0]["id"]
    
    # 2. Verify syllabus ownership and status
    syl_res = supabase_admin.table("syllabus_documents").select("*").eq("id", request.syllabus_id).execute()
    if not syl_res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    syl = syl_res.data[0]
    if syl["learner_id"] != learner_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if syl["status"] != "CONFIRMED":
        raise HTTPException(status_code=400, detail="Syllabus must be CONFIRMED before roadmap generation")
        
    # 3. Queue generation with optional subject
    background_tasks.add_task(
        roadmap_service.generate_roadmap_background, 
        learner_id, 
        request.scope.value, 
        request.syllabus_id,
        request.subject
    )
    
    return {
        "message": "Roadmap generation started", 
        "status": "PROCESSING",
        "subject": request.subject or "ALL"
    }

@router.get("/current")
async def get_current_roadmap(
    subject: Optional[str] = None,
    scope: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    
    # 1. Resolve learner_id
    learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not learner_res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    learner_id = learner_res.data[0]["id"]
    
    # 2. Fetch active roadmaps query
    query = (
        supabase_admin.table("roadmaps")
        .select("*")
        .eq("learner_id", learner_id)
        .eq("status", "ACTIVE")
    )
    if scope:
        query = query.eq("scope", scope)
        
    roadmap_res = query.order("created_at", desc=True).execute()
    roadmaps_list = roadmap_res.data or []
    
    if not roadmaps_list:
        return {"roadmap": None, "available_subjects": [], "active_subject": subject or "ALL"}
        
    # 3. Roadmap Selection Logic (case-insensitive & master fallback)
    selected_roadmap = None
    normalized_subject = subject.strip().lower() if subject and subject.strip().upper() != "ALL" else None
    
    if normalized_subject:
        # Prioritize dedicated single-subject roadmap
        for r in roadmaps_list:
            if (r.get("subject") or "").strip().lower() == normalized_subject:
                selected_roadmap = r
                break
        # Fallback to master roadmap (where subject is NULL)
        if not selected_roadmap:
            for r in roadmaps_list:
                if not r.get("subject"):
                    selected_roadmap = r
                    break
    else:
        # For ALL or unspecified subject, prioritize master roadmap
        for r in roadmaps_list:
            if not r.get("subject"):
                selected_roadmap = r
                break
                
    # Fallback to the latest active roadmap if neither was matched
    if not selected_roadmap:
        selected_roadmap = roadmaps_list[0]
        
    roadmap_id = selected_roadmap["id"]
    
    # 4. Fetch associated missions for the selected roadmap
    missions_res = (
        supabase_admin.table("missions")
        .select("*")
        .eq("roadmap_id", roadmap_id)
        .order("sequence")
        .execute()
    )
    roadmap_missions = missions_res.data or []
    
    # 5. Compute available subjects across active roadmaps so tabs never disappear
    all_active_ids = [r["id"] for r in roadmaps_list]
    if len(all_active_ids) == 1:
        missions_for_stats = roadmap_missions
    else:
        active_missions_res = (
            supabase_admin.table("missions")
            .select("id, subject, status, roadmap_id")
            .in_("roadmap_id", all_active_ids)
            .execute()
        )
        missions_for_stats = active_missions_res.data or roadmap_missions

    subjects_map = {}
    for m in missions_for_stats:
        subj_name = (m.get("subject") or "").strip() or "General"
        if subj_name not in subjects_map:
            subjects_map[subj_name] = {"total": 0, "completed": 0, "in_progress": 0}
        subjects_map[subj_name]["total"] += 1
        if m.get("status") == "COMPLETED":
            subjects_map[subj_name]["completed"] += 1
        elif m.get("status") == "IN_PROGRESS":
            subjects_map[subj_name]["in_progress"] += 1
            
    available_subjects = []
    for s_name, stats in subjects_map.items():
        pct = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        available_subjects.append({
            "name": s_name,
            "total_missions": stats["total"],
            "completed_missions": stats["completed"],
            "in_progress_missions": stats["in_progress"],
            "progress_percentage": pct
        })
        
    # 6. Filter missions if user requested a specific subject
    displayed_missions = roadmap_missions
    if normalized_subject:
        displayed_missions = [
            m for m in roadmap_missions 
            if (m.get("subject") or "").strip().lower() == normalized_subject
        ]
        
    roadmap_detail = {
        "id": roadmap_id,
        "version": selected_roadmap.get("version", 1),
        "scope": selected_roadmap.get("scope"),
        "subject": selected_roadmap.get("subject"),
        "status": selected_roadmap.get("status"),
        "scope_data": selected_roadmap.get("plan_data", {}),
        "missions": displayed_missions,
        "created_at": selected_roadmap.get("created_at"),
        "updated_at": selected_roadmap.get("updated_at")
    }
    
    return {
        "roadmap": roadmap_detail,
        "available_subjects": available_subjects,
        "active_subject": subject or "ALL"
    }

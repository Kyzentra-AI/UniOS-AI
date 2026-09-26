from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.services.storage_service import storage_service
from app.services.syllabus_service import syllabus_service
from app.services.event_service import event_service
from app.schemas.syllabus import SyllabusResponse, SyllabusStatusResponse, SyllabusUpdate, SyllabusStatus
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/syllabi", tags=["Syllabus"])

@router.post("", response_model=SyllabusStatusResponse)
async def upload_syllabus(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Get learner id
    learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not learner_res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    learner_id = learner_res.data[0]["id"]
    
    # Read file
    file_bytes = await file.read()
    
    # Upload to storage
    storage_key = storage_service.upload_file(file_bytes, file.filename, file.content_type)
    
    # Create syllabus record
    doc_id = str(uuid.uuid4())
    db_data = {
        "id": doc_id,
        "learner_id": learner_id,
        "file_name": file.filename,
        "storage_key": storage_key,
        "file_type": file.content_type,
        "status": "PROCESSING",
        "version": 1
    }
    
    supabase_admin.table("syllabus_documents").insert(db_data).execute()
    
    # Background processing
    background_tasks.add_task(syllabus_service.process_syllabus_background, doc_id, file_bytes)
    
    return {"id": doc_id, "status": SyllabusStatus.PROCESSING}

@router.get("/{id}", response_model=SyllabusResponse)
async def get_syllabus(id: str, current_user: dict = Depends(get_current_user)):
    res = supabase_admin.table("syllabus_documents").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    
    # Verify ownership indirectly
    doc = res.data[0]
    learner_res = supabase_admin.table("learner_profiles").select("user_id").eq("id", doc["learner_id"]).execute()
    if not learner_res.data or learner_res.data[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return doc

@router.get("/{id}/status", response_model=SyllabusStatusResponse)
async def get_syllabus_status(id: str, current_user: dict = Depends(get_current_user)):
    res = supabase_admin.table("syllabus_documents").select("id, status, learner_id").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    doc = res.data[0]
    learner_res = supabase_admin.table("learner_profiles").select("user_id").eq("id", doc["learner_id"]).execute()
    if not learner_res.data or learner_res.data[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return doc

@router.put("/{id}/parsed-content")
async def update_parsed_content(id: str, payload: SyllabusUpdate, current_user: dict = Depends(get_current_user)):
    res = supabase_admin.table("syllabus_documents").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    doc = res.data[0]
    learner_res = supabase_admin.table("learner_profiles").select("user_id").eq("id", doc["learner_id"]).execute()
    if not learner_res.data or learner_res.data[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    supabase_admin.table("syllabus_documents").update({
        "parsed_content": payload.parsed_content.model_dump(),
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    return {"message": "Syllabus updated successfully"}

@router.post("/{id}/reprocess")
async def reprocess_syllabus(id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    res = supabase_admin.table("syllabus_documents").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    doc = res.data[0]
    learner_res = supabase_admin.table("learner_profiles").select("user_id").eq("id", doc["learner_id"]).execute()
    if not learner_res.data or learner_res.data[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    supabase_admin.table("syllabus_documents").update({
        "status": "PROCESSING",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    # We need the full URL for the storage key
    file_url = supabase_admin.storage.from_("syllabi").get_public_url(doc["storage_key"])
    
    background_tasks.add_task(syllabus_service.reprocess_syllabus_background, id, file_url)
    
    return {"message": "Reprocessing started", "status": "PROCESSING"}

@router.post("/{id}/confirm")
async def confirm_syllabus(id: str, current_user: dict = Depends(get_current_user)):
    res = supabase_admin.table("syllabus_documents").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Syllabus not found")
        
    doc = res.data[0]
    learner_res = supabase_admin.table("learner_profiles").select("user_id").eq("id", doc["learner_id"]).execute()
    if not learner_res.data or learner_res.data[0]["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if doc["status"] == "CONFIRMED":
        return {"message": "Already confirmed"}
        
    supabase_admin.table("syllabus_documents").update({
        "status": "CONFIRMED",
        "confirmed_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", id).execute()
    
    event_service.record_event(
        learner_id=doc["learner_id"],
        event_type="SYLLABUS_CONFIRMED",
        entity_type="SYLLABUS",
        entity_id=id
    )
    
    return {"message": "Syllabus confirmed successfully"}

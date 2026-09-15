import datetime
from datetime import timezone
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
from app.schemas.memory import (
    MemoryLogCreate,
    MemoryLogResponse,
    MemoryResetRequest,
    ContextPayloadResponse,
    UserPreferencesPayload,
    ActiveFrictionPoint
)
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/api/v1", tags=["AI Memory & Context Engine"])

@router.get("/context/retrieve", response_model=ContextPayloadResponse)
async def retrieve_student_context(
    student_id: Optional[str] = Query(None, description="Optional student user_id. Defaults to authenticated user."),
    current_user: dict = Depends(get_current_user)
):
    target_user_id = student_id or current_user["user_id"]
    
    try:
        # 1. Fetch Profile
        profile_res = supabase_admin.table("student_profiles").select("*").eq("user_id", target_user_id).execute()
        profile_data = profile_res.data[0] if profile_res.data else {}

        language = profile_data.get("primary_language", "English")
        preferred_modes = profile_data.get("preferred_modes", ["Visual Diagrams"])
        delivery_mode = preferred_modes[0] if preferred_modes else "Visual Diagrams"
        
        # 2. Fetch Active Friction Points (Implicit Memory Logs)
        logs_res = supabase_admin.table("ai_implicit_memory_logs")\
            .select("concept, error_frequency, last_observed")\
            .eq("user_id", target_user_id)\
            .eq("is_archived", False)\
            .order("last_observed", desc=True)\
            .execute()
        
        active_friction_points = [
            ActiveFrictionPoint(
                concept=item["concept"],
                error_frequency=item.get("error_frequency", 1),
                last_observed=str(item.get("last_observed", ""))
            )
            for item in (logs_res.data or [])
        ]

        # 3. Fetch Explicit Directives
        directives_res = supabase_admin.table("ai_explicit_directives")\
            .select("directive_text")\
            .eq("user_id", target_user_id)\
            .eq("is_active", True)\
            .execute()
        
        explicit_directives = [d["directive_text"] for d in (directives_res.data or [])]

        # 4. Construct Context Payload
        return ContextPayloadResponse(
            student_id=target_user_id,
            preferences=UserPreferencesPayload(
                language=language,
                delivery_mode=delivery_mode,
                code_language="Python"
            ),
            mastery_summary={}, # Placeholder for concept mastery evaluation
            active_friction_points=active_friction_points,
            explicit_directives=explicit_directives
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/logs", response_model=MemoryLogResponse, status_code=status.HTTP_201_CREATED)
async def log_implicit_memory(
    request: MemoryLogCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    now = datetime.datetime.now(timezone.utc).isoformat()
    
    try:
        # Check if memory log exists for concept and is not archived
        existing_res = supabase_admin.table("ai_implicit_memory_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("concept", request.concept)\
            .eq("is_archived", False)\
            .execute()

        if existing_res.data:
            existing_record = existing_res.data[0]
            new_freq = existing_record.get("error_frequency", 1) + request.error_frequency_increment
            update_res = supabase_admin.table("ai_implicit_memory_logs")\
                .update({
                    "error_frequency": new_freq,
                    "last_observed": now
                })\
                .eq("memory_id", existing_record["memory_id"])\
                .execute()
            return update_res.data[0]
        else:
            insert_res = supabase_admin.table("ai_implicit_memory_logs")\
                .insert({
                    "user_id": user_id,
                    "concept": request.concept,
                    "error_frequency": request.error_frequency_increment,
                    "last_observed": now,
                    "is_archived": False
                })\
                .execute()
            return insert_res.data[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/reset", status_code=status.HTTP_200_OK)
async def reset_ai_memory(
    request: MemoryResetRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    try:
        if request.concept:
            # Archive specific concept log
            supabase_admin.table("ai_implicit_memory_logs")\
                .update({"is_archived": True})\
                .eq("user_id", user_id)\
                .eq("concept", request.concept)\
                .execute()
            return {"message": f"Implicit memory log for concept '{request.concept}' has been reset."}
        else:
            # Archive all implicit memory logs for user
            supabase_admin.table("ai_implicit_memory_logs")\
                .update({"is_archived": True})\
                .eq("user_id", user_id)\
                .execute()
            return {"message": "All implicit AI learning memory logs have been successfully reset."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/memory/logs/{memory_id}", status_code=status.HTTP_200_OK)
async def delete_memory_log(
    memory_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    try:
        supabase_admin.table("ai_implicit_memory_logs")\
            .delete()\
            .eq("memory_id", memory_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Memory record deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

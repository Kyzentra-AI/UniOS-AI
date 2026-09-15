import datetime
from datetime import timezone
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.profile import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
    ExplicitDirectiveCreate,
    ExplicitDirectiveResponse
)
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin

router = APIRouter(prefix="/api/v1/profile", tags=["Student Profile"])

@router.get("", response_model=StudentProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        profile_res = supabase_admin.table("student_profiles").select("*").eq("user_id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found. Please complete baseline onboarding."
            )
        
        profile = profile_res.data[0]

        # Fetch explicit directives
        directives_res = supabase_admin.table("ai_explicit_directives").select("directive_text").eq("user_id", user_id).eq("is_active", True).execute()
        directives = [d["directive_text"] for d in (directives_res.data or [])]

        return {
            **profile,
            "explicit_directives": directives
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", response_model=StudentProfileResponse, status_code=status.HTTP_200_OK)
async def create_or_update_profile(request: StudentProfileCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    now = datetime.datetime.now(timezone.utc).isoformat()
    
    try:
        # Check if profile already exists
        existing_res = supabase_admin.table("student_profiles").select("profile_id").eq("user_id", user_id).execute()
        
        profile_payload = {
            "user_id": user_id,
            "degree_program": request.degree_program,
            "academic_year": request.academic_year,
            "primary_language": request.primary_language,
            "preferred_modes": request.preferred_modes,
            "primary_career_goal": request.primary_career_goal,
            "updated_at": now
        }

        if existing_res.data:
            # Update
            res = supabase_admin.table("student_profiles").update(profile_payload).eq("user_id", user_id).execute()
        else:
            # Insert
            profile_payload["created_at"] = now
            res = supabase_admin.table("student_profiles").insert(profile_payload).execute()

        saved_profile = res.data[0]

        # Process explicit directives if provided
        if request.explicit_directives is not None:
            # Clear existing directives for user to overwrite or update
            supabase_admin.table("ai_explicit_directives").delete().eq("user_id", user_id).execute()
            
            directive_records = [
                {
                    "user_id": user_id,
                    "directive_text": d,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now
                }
                for d in request.explicit_directives if d.strip()
            ]
            if directive_records:
                supabase_admin.table("ai_explicit_directives").insert(directive_records).execute()

        # Fetch current directives
        directives_res = supabase_admin.table("ai_explicit_directives").select("directive_text").eq("user_id", user_id).eq("is_active", True).execute()
        directives = [d["directive_text"] for d in (directives_res.data or [])]

        return {
            **saved_profile,
            "explicit_directives": directives
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/directives", response_model=ExplicitDirectiveResponse, status_code=status.HTTP_201_CREATED)
async def add_explicit_directive(request: ExplicitDirectiveCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    now = datetime.datetime.now(timezone.utc).isoformat()
    try:
        res = supabase_admin.table("ai_explicit_directives").insert({
            "user_id": user_id,
            "directive_text": request.directive_text,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/directives/{directive_id}", status_code=status.HTTP_200_OK)
async def delete_explicit_directive(directive_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        res = supabase_admin.table("ai_explicit_directives").delete().eq("directive_id", directive_id).eq("user_id", user_id).execute()
        return {"message": "Explicit directive deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

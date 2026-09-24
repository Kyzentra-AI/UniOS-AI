from fastapi import APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from typing import Dict, Any, Optional
from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.onboarding import OnboardingRequest, OnboardingCompleteValidator
from app.schemas.kie import OnboardingAnswersRequest, KIEWebhookQuestionsPayload, KIEWebhookResolvedPayload
from app.services.kie_service import kie_service
from app.core.kie_assembler import LearnerContextAssembler
from app.core.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/v1/onboarding", tags=["Onboarding"])

def _get_learner_profile(user_id: str) -> dict:
    response = supabase_admin.table("learner_profiles").select("*").eq("user_id", user_id).execute()
    if not response.data:
        return {}
    return response.data[0]

def _get_academic_profile(learner_profile_id: str) -> dict:
    response = supabase_admin.table("academic_profiles").select("*").eq("learner_profile_id", learner_profile_id).execute()
    if not response.data:
        return {}
    return response.data[0]

def _get_learning_preferences(learner_profile_id: str) -> dict:
    response = supabase_admin.table("learning_preferences").select("*").eq("learner_profile_id", learner_profile_id).execute()
    if not response.data:
        return {}
    return response.data[0]

@router.get("")
async def get_onboarding_state(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    academic = {}
    preferences = {}
    
    if learner:
        academic = _get_academic_profile(learner["id"])
        preferences = _get_learning_preferences(learner["id"])
        
    context = LearnerContextAssembler.assemble(learner, academic, preferences)
    
    # Return both raw and context to be helpful
    return {
        "status": learner.get("onboarding_status", "NOT_STARTED"),
        "raw_data": {
            "learner_profile": learner,
            "academic_profile": academic,
            "learning_preferences": preferences
        },
        "context": context
    }

@router.post("")
async def init_onboarding(request: OnboardingRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    
    if learner:
        raise HTTPException(status_code=400, detail="Onboarding already initialized. Use PATCH to update.")
        
    learner_data = request.learner_profile.model_dump(exclude_unset=True) if request.learner_profile else {}
    learner_data["user_id"] = user_id
    
    # Insert Learner Profile
    learner_res = supabase_admin.table("learner_profiles").insert(learner_data).execute()
    new_learner = learner_res.data[0]
    learner_id = new_learner["id"]
    
    # Insert Academic Profile
    academic_data = request.academic_profile.model_dump(exclude_unset=True) if request.academic_profile else {}
    academic_data["learner_profile_id"] = learner_id
    supabase_admin.table("academic_profiles").insert(academic_data).execute()
    
    # Insert Learning Preferences
    pref_data = request.learning_preferences.model_dump(exclude_unset=True) if request.learning_preferences else {}
    pref_data["learner_profile_id"] = learner_id
    supabase_admin.table("learning_preferences").insert(pref_data).execute()
    
    return await get_onboarding_state(current_user)

@router.patch("")
async def update_onboarding(request: OnboardingRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    
    if not learner:
        raise HTTPException(status_code=404, detail="Onboarding not started. Use POST to initialize.")
        
    learner_id = learner["id"]
    
    # Update Learner Profile
    if request.learner_profile:
        update_data = request.learner_profile.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            supabase_admin.table("learner_profiles").update(update_data).eq("id", learner_id).execute()
            
    # Update Academic Profile
    if request.academic_profile:
        update_data = request.academic_profile.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            academic = _get_academic_profile(learner_id)
            if academic:
                supabase_admin.table("academic_profiles").update(update_data).eq("learner_profile_id", learner_id).execute()
            else:
                update_data["learner_profile_id"] = learner_id
                supabase_admin.table("academic_profiles").insert(update_data).execute()
                
    # Update Learning Preferences
    if request.learning_preferences:
        update_data = request.learning_preferences.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            prefs = _get_learning_preferences(learner_id)
            if prefs:
                supabase_admin.table("learning_preferences").update(update_data).eq("learner_profile_id", learner_id).execute()
            else:
                update_data["learner_profile_id"] = learner_id
                supabase_admin.table("learning_preferences").insert(update_data).execute()
                
    return await get_onboarding_state(current_user)

@router.post("/complete")
async def complete_onboarding(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    
    if not learner:
        raise HTTPException(status_code=404, detail="Onboarding not started.")
        
    if learner.get("onboarding_status") == "COMPLETED":
        return {"message": "Onboarding already completed."}
        
    academic = _get_academic_profile(learner["id"])
    prefs = _get_learning_preferences(learner["id"])
    
    # Assemble current state for validation
    validation_data = {}
    validation_data.update(learner)
    validation_data.update(academic)
    validation_data.update(prefs)
    
    try:
        # This will run all the strict validation logic on the merged dictionary
        OnboardingCompleteValidator(**validation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Mark as completed
    now = datetime.utcnow().isoformat()
    supabase_admin.table("learner_profiles").update({
        "onboarding_status": "COMPLETED",
        "completed_at": now,
        "updated_at": now
    }).eq("id", learner["id"]).execute()
    
    return {"message": "Onboarding successfully completed."}

# =============================================================================
# KIE Integration Endpoints
# =============================================================================

@router.get("/questions")
async def get_kie_questions(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    
    if not learner:
        raise HTTPException(status_code=404, detail="Onboarding not started.")
        
    # If questions already exist, return them
    if learner.get("pending_kie_questions"):
        return {
            "status": "pending_context",
            "questions": learner["pending_kie_questions"]
        }
        
    # Otherwise, trigger analysis
    academic = _get_academic_profile(learner["id"])
    preferences = _get_learning_preferences(learner["id"])
    context = LearnerContextAssembler.assemble(learner, academic, preferences)
    
    background_tasks.add_task(kie_service.analyze_context, context)
    
    return {
        "status": "processing",
        "message": "KIE is analyzing your profile."
    }

@router.post("/answers")
async def submit_kie_answers(request: OnboardingAnswersRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    learner = _get_learner_profile(user_id)
    
    if not learner:
        raise HTTPException(status_code=404, detail="Onboarding not started.")
        
    # Clear pending questions
    supabase_admin.table("learner_profiles").update({
        "pending_kie_questions": None,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", learner["id"]).execute()
    
    background_tasks.add_task(kie_service.resolve_context, user_id, request.answers)
    
    return {
        "status": "processing",
        "message": "Answers submitted to KIE."
    }

def verify_kie_webhook_secret(x_kie_signature: str = Header(...)):
    if x_kie_signature != settings.KIE_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

@router.post("/kie/webhook/questions")
async def kie_webhook_questions(payload: KIEWebhookQuestionsPayload, _: None = Depends(verify_kie_webhook_secret)):
    # Save the questions back to the user's profile
    learner = _get_learner_profile(payload.user_id)
    if not learner:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    questions_data = [q.model_dump() for q in payload.questions]
    
    supabase_admin.table("learner_profiles").update({
        "pending_kie_questions": questions_data,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", learner["id"]).execute()
    
    return {"status": "ok"}

@router.post("/kie/webhook/resolved")
async def kie_webhook_resolved(payload: KIEWebhookResolvedPayload, _: None = Depends(verify_kie_webhook_secret)):
    learner = _get_learner_profile(payload.user_id)
    if not learner:
        raise HTTPException(status_code=404, detail="User profile not found")
        
    new_context = payload.new_context
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    # Example mapping logic:
    # Append new skills
    if "primary_languages" in new_context:
        existing_skills = learner.get("skills") or []
        new_skills = [s for s in new_context["primary_languages"] if s not in existing_skills]
        update_data["skills"] = existing_skills + new_skills
        
    # Update experience level text if provided
    if "experience_level" in new_context:
        update_data["experience"] = new_context["experience_level"]
        
    # Save unstructured data to inferred_context
    existing_inferred = learner.get("inferred_context") or {}
    existing_inferred.update(new_context)
    update_data["inferred_context"] = existing_inferred
    
    supabase_admin.table("learner_profiles").update(update_data).eq("id", learner["id"]).execute()
    
    return {"status": "ok"}

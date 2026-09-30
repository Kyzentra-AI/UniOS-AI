from typing import Dict, Any
from app.core.supabase import supabase_admin
from app.services.event_service import event_service
from app.services.kie_service import kie_service

class ContextV2Assembler:
    @staticmethod
    async def assemble(learner_id: str, scope: str = None, syllabus_id: str = None) -> Dict[str, Any]:
        # Fetch learner
        learner_res = supabase_admin.table("learner_profiles").select("*").eq("id", learner_id).execute()
        learner = learner_res.data[0] if learner_res.data else {}

        # Fetch education (academic)
        academic_res = supabase_admin.table("academic_profiles").select("*").eq("learner_profile_id", learner_id).execute()
        academic = academic_res.data[0] if academic_res.data else {}

        # Fetch preferences
        pref_res = supabase_admin.table("learning_preferences").select("*").eq("learner_profile_id", learner_id).execute()
        preferences = pref_res.data[0] if pref_res.data else {}

        # Fetch Syllabus
        syllabus = {}
        if syllabus_id:
            syllabus_res = supabase_admin.table("syllabus_documents").select("*").eq("id", syllabus_id).execute()
            syllabus = syllabus_res.data[0] if syllabus_res.data else {}

        # Fetch Active Roadmap
        active_roadmap = {}
        if scope:
            roadmap_res = supabase_admin.table("roadmaps").select("*").eq("learner_id", learner_id).eq("scope", scope).eq("status", "ACTIVE").execute()
            active_roadmap = roadmap_res.data[0] if roadmap_res.data else {}

        # Fetch recent events
        recent_events = event_service.get_recent_events(learner_id, limit=20)

        # Get Memory Summary from AI/ML-2
        memory_summary = await kie_service.get_memory_summary(recent_events)

        learner_clean = {k: v for k, v in learner.items() if k not in [
            "id", "user_id", "onboarding_status", "onboarding_version", 
            "pending_kie_questions", "created_at", "updated_at", "completed_at"
        ]}
        academic_clean = {k: v for k, v in academic.items() if k not in [
            "id", "learner_profile_id", "created_at", "updated_at"
        ]}
        preferences_clean = {k: v for k, v in preferences.items() if k not in [
            "id", "learner_profile_id", "created_at", "updated_at"
        ]}

        return {
            "learner_id": learner_id,
            "learner": learner_clean,
            "education": academic_clean,
            "preferences": preferences_clean,
            "syllabus": syllabus.get("parsed_content", {}),
            "roadmap": active_roadmap.get("plan_data", {}),
            "recent_history": recent_events,
            "memory_summary": memory_summary,
            "scope": scope
        }

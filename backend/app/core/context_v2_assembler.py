from typing import Dict, Any, Optional
from app.core.supabase import supabase_admin
from app.services.event_service import event_service
from app.services.kie_service import kie_service

class ContextV2Assembler:
    @staticmethod
    async def assemble(
        learner_id: str, 
        scope: str = None, 
        syllabus_id: str = None,
        target_subject: str = None
    ) -> Dict[str, Any]:
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
            roadmap_query = (
                supabase_admin.table("roadmaps")
                .select("*")
                .eq("learner_id", learner_id)
                .eq("scope", scope)
                .eq("status", "ACTIVE")
            )
            if target_subject:
                # Prioritize the active roadmap for this target subject
                target_rm_res = roadmap_query.eq("subject", target_subject).order("created_at", desc=True).limit(1).execute()
                if target_rm_res.data:
                    active_roadmap = target_rm_res.data[0]
                else:
                    # Fallback to master roadmap (subject is null)
                    master_rm_res = (
                        supabase_admin.table("roadmaps")
                        .select("*")
                        .eq("learner_id", learner_id)
                        .eq("scope", scope)
                        .eq("status", "ACTIVE")
                        .is_("subject", "null")
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
                    active_roadmap = master_rm_res.data[0] if master_rm_res.data else {}
            else:
                master_rm_res = (
                    roadmap_query
                    .is_("subject", "null")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                if master_rm_res.data:
                    active_roadmap = master_rm_res.data[0]
                else:
                    any_rm_res = (
                        supabase_admin.table("roadmaps")
                        .select("*")
                        .eq("learner_id", learner_id)
                        .eq("scope", scope)
                        .eq("status", "ACTIVE")
                        .order("created_at", desc=True)
                        .limit(1)
                        .execute()
                    )
                    active_roadmap = any_rm_res.data[0] if any_rm_res.data else {}

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

        parsed_syllabus = syllabus.get("parsed_content", {})
        if target_subject and isinstance(parsed_syllabus, dict) and "subjects" in parsed_syllabus:
            filtered_subjects = [
                s for s in parsed_syllabus["subjects"] 
                if isinstance(s, dict) and s.get("name", "").strip().lower() == target_subject.strip().lower()
            ]
            if filtered_subjects:
                parsed_syllabus = dict(parsed_syllabus, subjects=filtered_subjects)

        return {
            "learner_id": learner_id,
            "learner": learner_clean,
            "education": academic_clean,
            "preferences": preferences_clean,
            "syllabus": parsed_syllabus,
            "roadmap": active_roadmap.get("plan_data", {}),
            "recent_history": recent_events,
            "memory_summary": memory_summary,
            "scope": scope,
            "target_subject": target_subject
        }

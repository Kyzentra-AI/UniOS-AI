from uuid import UUID
from datetime import datetime
from fastapi import HTTPException
from app.core.supabase import supabase_admin
from app.schemas.learning import LearningSessionCreate, LearningSessionUpdate, SessionStatus
from app.services.event_service import event_service

class LearningSessionService:
    @staticmethod
    def create_or_get_session(learner_id: str, session_in: LearningSessionCreate) -> dict:
        """
        Creates a new learning session or gets an existing active one for the same lesson.
        """
        # Check for existing IN_PROGRESS session
        existing = supabase_admin.table("learning_sessions").select("*").eq(
            "learner_id", learner_id
        ).eq("lesson_id", session_in.lesson_id).eq("status", "IN_PROGRESS").execute()

        if existing.data:
            return existing.data[0]

        # Create new
        data = {
            "learner_id": learner_id,
            "roadmap_id": str(session_in.roadmap_id) if session_in.roadmap_id else None,
            "mission_id": str(session_in.mission_id) if session_in.mission_id else None,
            "topic": session_in.topic,
            "lesson_id": session_in.lesson_id,
            "status": "IN_PROGRESS"
        }
        res = supabase_admin.table("learning_sessions").insert(data).execute()
        
        event_service.record_event(learner_id, "SESSION_STARTED", "LESSON", session_in.lesson_id)
        return res.data[0]
        
    @staticmethod
    def get_session(session_id: str, learner_id: str) -> dict:
        res = supabase_admin.table("learning_sessions").select("*").eq("id", session_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        session = res.data[0]
        if session["learner_id"] != learner_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return session

    @staticmethod
    def update_checkpoint(session_id: str, learner_id: str, update_in: LearningSessionUpdate) -> dict:
        """
        Updates session checkpoint and progress.
        """
        session = LearningSessionService.get_session(session_id, learner_id)
        
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        if update_in.status is not None:
            update_data["status"] = update_in.status
        if update_in.checkpoint_block_id is not None:
            update_data["checkpoint_block_id"] = update_in.checkpoint_block_id
        if update_in.progress_percentage is not None:
            update_data["progress_percentage"] = update_in.progress_percentage
        if update_in.notes is not None:
            update_data["notes"] = update_in.notes
            
        res = supabase_admin.table("learning_sessions").update(update_data).eq("id", session_id).execute()
        updated_session = res.data[0]
        
        if updated_session["status"] == "COMPLETED" and session["status"] != "COMPLETED":
            event_service.record_event(learner_id, "SESSION_COMPLETED", "LESSON", updated_session["lesson_id"])
            
        return updated_session

learning_session_service = LearningSessionService()

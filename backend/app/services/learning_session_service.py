from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.supabase import supabase_admin
from app.schemas.learning import LearningSessionCreate, LearningSessionUpdate, SessionStatus
from app.services.event_service import event_service

class LearningSessionService:
    @staticmethod
    def create_or_get_session(learner_id: str, session_in: LearningSessionCreate) -> dict:
        """
        Creates a new learning session or gets an existing active/paused one for the same lesson.
        """
        # Check for existing IN_PROGRESS or PAUSED session for this lesson
        query = supabase_admin.table("learning_sessions").select("*").eq(
            "learner_id", learner_id
        ).eq("lesson_id", session_in.lesson_id).in_("status", ["IN_PROGRESS", "PAUSED"]).order("updated_at", desc=True)
        existing = query.execute()

        # If not found by lesson_id but mission_id was provided, check by mission_id as fallback
        if not existing.data and session_in.mission_id:
            existing = supabase_admin.table("learning_sessions").select("*").eq(
                "learner_id", learner_id
            ).eq("mission_id", str(session_in.mission_id)).in_("status", ["IN_PROGRESS", "PAUSED"]).order("updated_at", desc=True).execute()

        if existing.data:
            session = existing.data[0]
            # If the session was PAUSED, resume it back to IN_PROGRESS
            if session.get("status") == "PAUSED":
                res = supabase_admin.table("learning_sessions").update({
                    "status": "IN_PROGRESS",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", session["id"]).execute()
                event_service.record_event(learner_id, "SESSION_RESUMED", "LESSON", session.get("lesson_id", session_in.lesson_id))
                return res.data[0] if (res and res.data) else session
            return session

        # Create new
        data = {
            "learner_id": learner_id,
            "roadmap_id": str(session_in.roadmap_id) if session_in.roadmap_id else None,
            "mission_id": str(session_in.mission_id) if session_in.mission_id else None,
            "topic": session_in.topic,
            "lesson_id": session_in.lesson_id,
            "status": "IN_PROGRESS",
            "completed_block_ids": [],
            "progress_percentage": 0
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
        
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        # Checkpoint validation against lesson blocks if available
        lesson_data = update_in.lesson_data or session.get("lesson_data")
        blocks = (lesson_data or {}).get("blocks", []) if isinstance(lesson_data, dict) else []
        valid_block_ids = {b.get("id") if isinstance(b, dict) else getattr(b, "id", None) for b in blocks}

        if update_in.checkpoint_block_id is not None:
            if valid_block_ids and update_in.checkpoint_block_id not in valid_block_ids:
                # Do not set invalid block id; fallback to existing or first block
                first_block_id = blocks[0].get("id") if isinstance(blocks[0], dict) else getattr(blocks[0], "id", None) if blocks else None
                update_data["checkpoint_block_id"] = session.get("checkpoint_block_id") or first_block_id
            else:
                update_data["checkpoint_block_id"] = update_in.checkpoint_block_id

        if update_in.completed_block_ids is not None:
            update_data["completed_block_ids"] = update_in.completed_block_ids

        # Status and progress percentage clamping
        is_completed = (
            update_in.status == SessionStatus.COMPLETED
            or update_in.status == "COMPLETED"
        )
        if update_in.status is not None:
            update_data["status"] = update_in.status

        if is_completed:
            update_data["status"] = "COMPLETED"
            update_data["progress_percentage"] = 100
        elif update_in.progress_percentage is not None:
            # Clamp intermediate step transitions between 0 and 90
            update_data["progress_percentage"] = max(0, min(update_in.progress_percentage, 90))

        if update_in.notes is not None:
            update_data["notes"] = update_in.notes
        if update_in.lesson_data is not None:
            update_data["lesson_data"] = update_in.lesson_data
            
        res = supabase_admin.table("learning_sessions").update(update_data).eq("id", session_id).execute()
        updated_session = res.data[0]
        
        if updated_session["status"] == "COMPLETED" and session["status"] != "COMPLETED":
            event_service.record_event(learner_id, "SESSION_COMPLETED", "LESSON", updated_session["lesson_id"])
        elif updated_session["status"] == "PAUSED" and session["status"] != "PAUSED":
            event_service.record_event(learner_id, "SESSION_PAUSED", "LESSON", updated_session["lesson_id"])
        elif updated_session["status"] == "IN_PROGRESS" and session["status"] == "PAUSED":
            event_service.record_event(learner_id, "SESSION_RESUMED", "LESSON", updated_session["lesson_id"])
            
        return updated_session

    @staticmethod
    def complete_session(session_id: str, learner_id: str) -> dict:
        """Explicitly marks a learning session as completed with 100% progress."""
        session = LearningSessionService.get_session(session_id, learner_id)
        update_data = {
            "status": "COMPLETED",
            "progress_percentage": 100,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase_admin.table("learning_sessions").update(update_data).eq("id", session_id).execute()
        updated_session = res.data[0]
        if session["status"] != "COMPLETED":
            event_service.record_event(learner_id, "SESSION_COMPLETED", "LESSON", updated_session["lesson_id"])
        return updated_session

learning_session_service = LearningSessionService()

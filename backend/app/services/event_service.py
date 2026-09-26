from app.core.supabase import supabase_admin
from typing import Dict, Any

class EventService:
    @staticmethod
    def record_event(learner_id: str, event_type: str, entity_type: str, entity_id: str, payload: Dict[str, Any] = None):
        if payload is None:
            payload = {}
        data = {
            "learner_id": learner_id,
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload": payload
        }
        try:
            supabase_admin.table("learner_events").insert(data).execute()
        except Exception as e:
            import logging
            logging.error(f"Failed to record event {event_type} for learner {learner_id}: {e}")
        
    @staticmethod
    def get_recent_events(learner_id: str, limit: int = 20) -> list:
        try:
            res = supabase_admin.table("learner_events").select("*").eq("learner_id", learner_id).order("created_at", desc=True).limit(limit).execute()
            return res.data if res.data else []
        except Exception:
            return []

event_service = EventService()

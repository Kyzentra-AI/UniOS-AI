import httpx
from datetime import datetime
from typing import Dict, Any, Tuple
from fastapi import HTTPException
from app.core.supabase import supabase_admin
from app.core.config import settings
from app.schemas.assessment import AssessmentAttemptCreate
from app.services.event_service import event_service

class AssessmentService:
    @staticmethod
    async def _evaluate_with_kie(attempt_in: AssessmentAttemptCreate, learner_id: str) -> Tuple[float, Dict[str, Any], str]:
        """
        Calls KIE Mastery/Remediation engine to evaluate answers.
        Returns (score, mastery_updates, feedback)
        """
        payload = {
            "learner_id": learner_id,
            "assessment_id": attempt_in.assessment_id,
            "topic": attempt_in.topic,
            "answers": [a.model_dump() for a in attempt_in.answers],
            "total_time_spent_seconds": attempt_in.total_time_spent_seconds
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/mastery/evaluate",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return (
                    data.get("score", 0.0),
                    data.get("mastery_updates", {}),
                    data.get("feedback", "")
                )
            except Exception as e:
                # If KIE is unavailable, we might do a simple fallback or just record 0
                return (0.0, {}, f"Evaluation failed: {str(e)}")

    @staticmethod
    async def record_attempt(learner_id: str, attempt_in: AssessmentAttemptCreate) -> dict:
        hints_used_count = sum(a.hints_used for a in attempt_in.answers)
        
        # Call KIE for scoring and mastery updates
        score, mastery_updates, feedback = await AssessmentService._evaluate_with_kie(attempt_in, learner_id)
        
        # Persist attempt
        attempt_data = {
            "session_id": str(attempt_in.session_id) if attempt_in.session_id else None,
            "learner_id": learner_id,
            "assessment_id": attempt_in.assessment_id,
            "topic": attempt_in.topic,
            "answers": [a.model_dump() for a in attempt_in.answers],
            "score": score,
            "total_time_spent_seconds": attempt_in.total_time_spent_seconds,
            "hints_used_count": hints_used_count,
            "is_completed": attempt_in.is_completed,
            "mastery_updates": mastery_updates,
            "feedback": feedback
        }
        
        res = supabase_admin.table("assessment_attempts").insert(attempt_data).execute()
        attempt = res.data[0]
        
        # Persist mastery updates to learner_mastery
        if attempt_in.is_completed and mastery_updates:
            for subject, topics in mastery_updates.items():
                for topic, details in topics.items():
                    new_score = details.get("score", 0.0)
                    new_status = details.get("status", "NOVICE")
                    
                    # Upsert mastery
                    supabase_admin.table("learner_mastery").upsert({
                        "learner_id": learner_id,
                        "subject": subject,
                        "topic": topic,
                        "mastery_score": new_score,
                        "status": new_status,
                        "last_assessed_at": datetime.utcnow().isoformat()
                    }, on_conflict="learner_id,subject,topic").execute()
                    
        # Emit event
        event_service.record_event(learner_id, "ASSESSMENT_COMPLETED", "ASSESSMENT", attempt_in.assessment_id)
        
        return attempt

assessment_service = AssessmentService()

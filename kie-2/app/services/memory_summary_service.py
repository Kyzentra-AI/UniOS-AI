import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemorySummaryService:
    """
    KIE Memory Summary Engine (Endpoint 5: POST /api/v1/kie/memory/summary).
    Analyzes learner event streams and produces a pedagogical memory summary for ContextV2Assembler.
    """

    def summarize(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the last 20 learner events and derives mastered concepts,
        friction points, engagement velocity, and pacing recommendations.
        """
        if not events:
            return {
                "mastered_concepts": [],
                "struggling_concepts": [],
                "recommended_pacing": "Standard with worked examples",
                "recent_activity_summary": "New learner profile; no previous activity recorded.",
                "engagement_level": "normal",
            }

        completed_missions = 0
        skipped_missions = 0
        assessments_taken = 0
        mastered_concepts: List[str] = []
        struggling_concepts: List[str] = []

        for ev in events:
            etype = ev.get("event_type", "").upper()
            payload = ev.get("payload") or {}

            if etype == "MISSION_COMPLETED":
                completed_missions += 1
                topic = payload.get("topic") or payload.get("title") or payload.get("subject")
                if topic and topic not in mastered_concepts:
                    mastered_concepts.append(str(topic))
            elif etype in {"MISSION_SKIPPED", "MISSION_DEFERRED"}:
                skipped_missions += 1
                topic = payload.get("topic") or payload.get("title") or payload.get("subject")
                if topic and topic not in struggling_concepts:
                    struggling_concepts.append(str(topic))
            elif etype == "ASSESSMENT_COMPLETED":
                assessments_taken += 1
                score = payload.get("score")
                topic = payload.get("topic")
                if score is not None:
                    try:
                        s_float = float(score)
                        if s_float >= 0.85 and topic and topic not in mastered_concepts:
                            mastered_concepts.append(str(topic))
                        elif s_float < 0.60 and topic and topic not in struggling_concepts:
                            struggling_concepts.append(str(topic))
                    except (ValueError, TypeError):
                        pass

        # Determine pacing & engagement
        if skipped_missions > completed_missions:
            pacing = "Deliberate with high visual scaffolding & remediation"
            engagement = "needs_intervention"
        elif completed_missions >= 4:
            pacing = "Accelerated / Intermediate"
            engagement = "high"
        else:
            pacing = "Moderate with balanced worked examples"
            engagement = "steady"

        summary_text = (
            f"Learner completed {completed_missions} missions, "
            f"skipped/deferred {skipped_missions}, and submitted {assessments_taken} assessments."
        )

        return {
            "mastered_concepts": mastered_concepts[:5],
            "struggling_concepts": struggling_concepts[:5],
            "recommended_pacing": pacing,
            "recent_activity_summary": summary_text,
            "engagement_level": engagement,
        }


_memory_summary_service_instance: Optional[MemorySummaryService] = None


def get_memory_summary_service() -> MemorySummaryService:
    global _memory_summary_service_instance
    if _memory_summary_service_instance is None:
        _memory_summary_service_instance = MemorySummaryService()
    return _memory_summary_service_instance


from collections import Counter
from typing import Any

from app.schemas.memory_summary import (
    MemorySummaryRequest,
)


class MemorySummaryEngine:
    """
    Creates a short-term summary of recent learner
    activity events.

    Backend owns event persistence.
    KIE only summarizes the supplied events.
    """

    def summarize(
        self,
        request: MemorySummaryRequest,
    ) -> dict[str, Any]:
        events = request.events

        if not events:
            return {
                "summary": "No recent learner activity.",
                "event_count": 0,
                "event_types": [],
                "recent_activity": [],
            }

        event_types = Counter(
            event.event_type
            for event in events
        )

        recent_activity = []

        for event in events:
            recent_activity.append(
                {
                    "event_type": event.event_type,
                    "entity_type": event.entity_type,
                    "entity_id": event.entity_id,
                    "payload": event.payload,
                    "created_at": event.created_at,
                }
            )

        type_summary = ", ".join(
            f"{event_type}: {count}"
            for event_type, count
            in event_types.items()
        )

        return {
            "summary": (
                f"Learner has {len(events)} recent "
                f"activity events. "
                f"Activity breakdown: {type_summary}."
            ),
            "event_count": len(events),
            "event_types": list(
                event_types.keys()
            ),
            "recent_activity": recent_activity,
        }
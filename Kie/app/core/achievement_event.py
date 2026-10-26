
from app.schemas.achievement_event import (
    AchievementEventRequest,
    AchievementEventResponse,
)


class AchievementEventEngine:
    """Create achievement proposals without persisting business state."""

    def generate(
        self,
        request: AchievementEventRequest,
    ) -> AchievementEventResponse:
        achievement_title = f"Completed: {request.activity_title}"

        description = (
            f"The learner completed an activity of type "
            f"'{request.activity_type}'. Reported outcome: "
            f"{request.outcome}. The backend must validate the "
            "evidence before confirming or recording the achievement."
        )

        return AchievementEventResponse(
            learner_id=request.learner_id,
            activity_id=request.activity_id,
            activity_type=request.activity_type,
            activity_title=request.activity_title,
            achievement_title=achievement_title,
            description=description,
            evidence=request.evidence,
            verification_status="pending_backend_verification",
            persistence_owner="backend",
        )

from app.schemas.response import PlanStep
from app.schemas.roadmap import (
    RoadmapContract,
    RoadmapMilestone,
)


class RoadmapContractBuilder:
    """
    Builds a Backend-ready roadmap contract from
    the KIE planning result.

    KIE is responsible for generating the roadmap
    structure.

    Backend is responsible for persistent storage,
    retrieval, and synchronization.
    """

    def build(
        self,
        user_id: str,
        session_id: str,
        planning_horizon: str | None,
        learner_stage: str | None,
        career_goal: str | None,
        plan: list[PlanStep],
    ) -> RoadmapContract:
        """
        Convert a KIE plan into a typed structured
        roadmap contract.
        """

        milestones = [
            RoadmapMilestone(
                milestone_id=step.step_id,
                description=step.description,
                agent=step.agent,
                status="planned",
            )
            for step in plan
        ]

        return RoadmapContract(
            user_id=user_id,
            session_id=session_id,
            planning_horizon=planning_horizon,
            learner_stage=learner_stage,
            career_goal=career_goal,
            milestones=milestones,
            milestone_count=len(milestones),
            planning_status="generated",
        )
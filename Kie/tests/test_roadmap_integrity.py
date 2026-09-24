import pytest
from pydantic import ValidationError

from app.schemas.roadmap import (
    RoadmapContract,
    RoadmapMilestone,
)


def test_milestone_count_matches_milestones():
    milestones = [
        RoadmapMilestone(
            milestone_id="step-1",
            description="Learn Python",
            agent="tutor-agent",
        ),
        RoadmapMilestone(
            milestone_id="step-2",
            description="Practice Python",
            agent="tutor-agent",
        ),
    ]

    roadmap = RoadmapContract(
        user_id="integrity-user-001",
        session_id="integrity-session-001",
        planning_horizon="weekly",
        learner_stage="final-year",
        career_goal="Software Engineer",
        milestones=milestones,
        milestone_count=2,
        planning_status="generated",
    )

    assert roadmap.milestone_count == len(
        roadmap.milestones
    )


def test_mismatched_milestone_count_is_rejected():
    milestones = [
        RoadmapMilestone(
            milestone_id="step-1",
            description="Learn Python",
            agent="tutor-agent",
        ),
        RoadmapMilestone(
            milestone_id="step-2",
            description="Practice Python",
            agent="tutor-agent",
        ),
    ]

    with pytest.raises(ValidationError):
        RoadmapContract(
            user_id="integrity-user-002",
            session_id="integrity-session-002",
            planning_horizon="weekly",
            learner_stage="final-year",
            career_goal="Software Engineer",
            milestones=milestones,
            milestone_count=3,
            planning_status="generated",
        )


def test_zero_milestones_requires_zero_count():
    roadmap = RoadmapContract(
        user_id="integrity-user-003",
        session_id="integrity-session-003",
        planning_horizon="daily",
        learner_stage="final-year",
        career_goal=None,
        milestones=[],
        milestone_count=0,
        planning_status="generated",
    )

    assert roadmap.milestone_count == 0
    assert roadmap.milestones == []


def test_zero_milestones_cannot_have_positive_count():
    with pytest.raises(ValidationError):
        RoadmapContract(
            user_id="integrity-user-004",
            session_id="integrity-session-004",
            planning_horizon="daily",
            learner_stage="final-year",
            career_goal=None,
            milestones=[],
            milestone_count=1,
            planning_status="generated",
        )
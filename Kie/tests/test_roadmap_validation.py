import pytest
from pydantic import ValidationError

from app.schemas.roadmap import RoadmapContract


def test_all_supported_planning_horizons_are_valid():
    horizons = [
        "semester",
        "career",
        "monthly",
        "weekly",
        "daily",
        "mission",
    ]

    for horizon in horizons:
        roadmap = RoadmapContract(
            user_id="validation-user-001",
            session_id="validation-session-001",
            planning_horizon=horizon,
            learner_stage="final-year",
            career_goal="Software Engineer",
            milestones=[],
            milestone_count=0,
            planning_status="generated",
        )

        assert roadmap.planning_horizon == horizon


def test_invalid_planning_horizon_is_rejected():
    with pytest.raises(ValidationError):
        RoadmapContract(
            user_id="validation-user-002",
            session_id="validation-session-002",
            planning_horizon="yearly",
            learner_stage="final-year",
            career_goal="Software Engineer",
            milestones=[],
            milestone_count=0,
            planning_status="generated",
        )


def test_planning_horizon_is_normalized():
    roadmap = RoadmapContract(
        user_id="validation-user-003",
        session_id="validation-session-003",
        planning_horizon="  WEEKLY  ",
        learner_stage="final-year",
        career_goal="Software Engineer",
        milestones=[],
        milestone_count=0,
        planning_status="generated",
    )

    assert roadmap.planning_horizon == "weekly"


def test_none_planning_horizon_is_allowed():
    roadmap = RoadmapContract(
        user_id="validation-user-004",
        session_id="validation-session-004",
        planning_horizon=None,
        learner_stage=None,
        career_goal=None,
        milestones=[],
        milestone_count=0,
        planning_status="generated",
    )

    assert roadmap.planning_horizon is None
    
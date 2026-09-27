from app.core.roadmap import RoadmapContractBuilder
from app.schemas.response import PlanStep


def test_roadmap_contract_contains_required_fields():
    builder = RoadmapContractBuilder()

    plan = [
        PlanStep(
            step_id="step-1",
            description="Learn Python decorators",
            agent="tutor-agent",
        ),
        PlanStep(
            step_id="step-2",
            description="Practice decorator examples",
            agent="tutor-agent",
        ),
    ]

    roadmap = builder.build(
        user_id="student-001",
        session_id="session-001",
        planning_horizon="weekly",
        learner_stage="final-year",
        career_goal="Software Engineer",
        plan=plan,
    )

    assert roadmap["user_id"] == "student-001"
    assert roadmap["session_id"] == "session-001"
    assert roadmap["planning_horizon"] == "weekly"
    assert roadmap["learner_stage"] == "final-year"
    assert roadmap["career_goal"] == "Software Engineer"

    assert roadmap["milestone_count"] == 2
    assert roadmap["planning_status"] == "generated"


def test_roadmap_contract_converts_plan_to_milestones():
    builder = RoadmapContractBuilder()

    plan = [
        PlanStep(
            step_id="step-1",
            description="Analyze current skills",
            agent="career-agent",
        ),
        PlanStep(
            step_id="step-2",
            description="Identify skill gaps",
            agent="career-agent",
        ),
    ]

    roadmap = builder.build(
        user_id="student-002",
        session_id="session-002",
        planning_horizon="career",
        learner_stage="final-year",
        career_goal="AI Engineer",
        plan=plan,
    )

    milestones = roadmap["milestones"]

    assert len(milestones) == 2

    assert milestones[0]["milestone_id"] == "step-1"
    assert milestones[0]["description"] == (
        "Analyze current skills"
    )
    assert milestones[0]["agent"] == "career-agent"
    assert milestones[0]["status"] == "planned"

    assert milestones[1]["milestone_id"] == "step-2"
    assert milestones[1]["description"] == (
        "Identify skill gaps"
    )
    assert milestones[1]["agent"] == "career-agent"
    assert milestones[1]["status"] == "planned"


def test_roadmap_contract_supports_empty_plan():
    builder = RoadmapContractBuilder()

    roadmap = builder.build(
        user_id="student-003",
        session_id="session-003",
        planning_horizon="daily",
        learner_stage="final-year",
        career_goal=None,
        plan=[],
    )

    assert roadmap["milestones"] == []
    assert roadmap["milestone_count"] == 0
    assert roadmap["planning_status"] == "generated"


def test_roadmap_contract_preserves_optional_values():
    builder = RoadmapContractBuilder()

    plan = [
        PlanStep(
            step_id="step-1",
            description="Review today's tasks",
            agent="general-agent",
        )
    ]

    roadmap = builder.build(
        user_id="student-004",
        session_id="session-004",
        planning_horizon=None,
        learner_stage=None,
        career_goal=None,
        plan=plan,
    )

    assert roadmap["planning_horizon"] is None
    assert roadmap["learner_stage"] is None
    assert roadmap["career_goal"] is None
    assert roadmap["milestone_count"] == 1
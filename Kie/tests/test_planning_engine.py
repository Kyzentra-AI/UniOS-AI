from app.core.planner import PlanningEngine


def test_semester_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my semester roadmap",
        planning_horizon="semester",
    )

    assert len(plan) == 4
    assert plan[0].step_id == "step-1"
    assert plan[0].agent == "tutor-agent"


def test_career_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LAUNCH",
        task="Create my career roadmap",
        planning_horizon="career",
    )

    assert len(plan) == 4
    assert plan[0].agent == "career-agent"


def test_monthly_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my monthly learning plan",
        planning_horizon="monthly",
    )

    assert len(plan) == 3
    assert plan[0].step_id == "step-1"


def test_weekly_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="BUILD",
        task="Create my weekly project plan",
        planning_horizon="weekly",
    )

    assert len(plan) == 3
    assert plan[0].agent == "project-agent"


def test_daily_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my daily learning plan",
        planning_horizon="daily",
    )

    assert len(plan) == 3
    assert plan[0].agent == "tutor-agent"


def test_mission_planning():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="BUILD",
        task="Complete my project mission",
        planning_horizon="mission",
    )

    assert len(plan) == 3
    assert plan[0].agent == "project-agent"


def test_invalid_planning_horizon_defaults_to_daily():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Plan my learning",
        planning_horizon="invalid-horizon",
    )

    assert len(plan) == 3


def test_sprint2_backward_compatibility():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Explain Python",
    )

    assert len(plan) == 1
    assert plan[0].step_id == "step-1"
    assert plan[0].agent == "tutor-agent"
from app.core.planner import PlanningEngine


def test_weekly_plan_uses_current_lesson_and_topic():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": ["Python", "SQL"],
        },
        "learner_context": {
            "current_lesson": "Python Functions",
            "current_topic": "Decorators",
        },
        "memory": {},
    }

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my weekly learning roadmap",
        planning_horizon="weekly",
        context=context,
    )

    assert len(plan) == 3

    assert "Python Functions" in plan[0].description

    assert "Decorators" in plan[0].description


def test_project_context_is_used_for_build_planning():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Full Stack Developer",
            "skills": ["Python", "React"],
        },
        "learner_context": {
            "project_id": "project-123",
            "workspace_id": "workspace-123",
        },
        "memory": {},
    }

    plan = planner.create_plan(
        intent="BUILD",
        task="Create my daily project plan",
        planning_horizon="daily",
        context=context,
    )

    assert len(plan) == 3

    description = plan[0].description

    assert "project-123" in description

    assert "workspace-123" in description


def test_progress_context_is_used_for_planning():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Data Scientist",
            "skills": ["Python"],
        },
        "learner_context": {
            "current_progress": {
                "completion_percentage": 65,
                "completed_topics": 8,
            }
        },
        "memory": {},
    }

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my daily learning plan",
        planning_horizon="daily",
        context=context,
    )

    assert len(plan) == 3

    description = plan[0].description

    assert "65" in description

    assert "completed_topics" in description


def test_roadmap_and_mission_context_are_used():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": ["Python"],
        },
        "learner_context": {
            "roadmap_id": "roadmap-456",
            "mission_id": "mission-456",
        },
        "memory": {},
    }

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my mission plan",
        planning_horizon="mission",
        context=context,
    )

    assert len(plan) == 3

    description = plan[0].description

    assert "roadmap-456" in description

    assert "mission-456" in description
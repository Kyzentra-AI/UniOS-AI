from app.core.planner import PlanningEngine


def test_career_plan_uses_learner_profile():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
                "React",
            ],
        },
        "memory": {},
    }

    plan = planner.create_plan(
        intent="LAUNCH",
        task="Create my career roadmap",
        planning_horizon="career",
        context=context,
    )

    assert len(plan) == 4

    assert "Software Engineer" in plan[0].description

    assert "Python" in plan[0].description

    assert "SQL" in plan[0].description

    assert "React" in plan[0].description


def test_weekly_plan_uses_learning_history():
    planner = PlanningEngine()

    context = {
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": ["Python"],
        },
        "memory": {
            "learning_history": [
                {
                    "content": "Completed Python basics"
                },
                {
                    "content": "Completed Python OOP"
                },
            ],
            "goals": [],
        },
    }

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my weekly learning plan",
        planning_horizon="weekly",
        context=context,
    )

    assert len(plan) == 3

    assert "2 learning history item(s)" in (
        plan[0].description
    )


def test_plan_uses_stored_goals():
    planner = PlanningEngine()

    context = {
        "learner_profile": {},
        "memory": {
            "goals": [
                {
                    "content": "Improve DSA"
                }
            ],
            "learning_history": [],
        },
    }

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my daily plan",
        planning_horizon="daily",
        context=context,
    )

    assert len(plan) == 3

    assert "1 stored learner goal(s)" in (
        plan[1].description
    )


def test_plan_works_without_learner_context():
    planner = PlanningEngine()

    plan = planner.create_plan(
        intent="LEARN",
        task="Create my weekly plan",
        planning_horizon="weekly",
    )

    assert len(plan) == 3

    assert plan[0].agent == "tutor-agent"


def test_different_learners_produce_different_contextual_plans():
    planner = PlanningEngine()

    learner_one_context = {
        "learner_profile": {
            "career_goal": "Data Scientist",
            "skills": [
                "Python",
                "Machine Learning",
            ],
        },
        "memory": {},
    }

    learner_two_context = {
        "learner_profile": {
            "career_goal": "Full Stack Developer",
            "skills": [
                "JavaScript",
                "React",
            ],
        },
        "memory": {},
    }

    plan_one = planner.create_plan(
        intent="LAUNCH",
        task="Create my career roadmap",
        planning_horizon="career",
        context=learner_one_context,
    )

    plan_two = planner.create_plan(
        intent="LAUNCH",
        task="Create my career roadmap",
        planning_horizon="career",
        context=learner_two_context,
    )

    assert plan_one[0].description != (
        plan_two[0].description
    )

    assert "Data Scientist" in (
        plan_one[0].description
    )

    assert "Full Stack Developer" in (
        plan_two[0].description
    )
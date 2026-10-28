from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_kie_execute_returns_backend_contract():
    payload = {
        "user_id": "backend-demo-001",
        "session_id": "backend-session-001",
        "role": "student",
        "task": "Create my weekly learning roadmap",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "university": "Demo University",
            "course": "Computer Science",
            "semester": 8,
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
        },
        "learner_context": {
            "current_lesson": "Python Functions",
            "current_topic": "Decorators",
            "roadmap_id": "roadmap-demo-001",
            "mission_id": "mission-demo-001",
            "learning_session_id": "session-demo-001",
            "current_progress": {
                "completion_percentage": 65
            },
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert "request_id" in data

    assert data["session_id"] == (
        "backend-session-001"
    )

    assert "identity" in data

    assert "context" in data

    assert "intent" in data

    assert "plan" in data

    assert "result" in data

    assert "metadata" in data

    assert "roadmap_contract" in data[
        "metadata"
    ]


def test_kie_contract_contains_learner_context():
    payload = {
        "user_id": "backend-demo-002",
        "session_id": "backend-session-002",
        "role": "student",
        "task": "Continue my current lesson",
        "learner_stage": "final-year",
        "learner_context": {
            "current_lesson": "Machine Learning",
            "current_topic": "Regression",
            "project_id": "project-001",
            "workspace_id": "workspace-001",
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    context = data["context"]

    assert context["learner_stage"] == (
        "final-year"
    )

    assert context["learner_context"][
        "current_lesson"
    ] == "Machine Learning"

    assert context["learner_context"][
        "current_topic"
    ] == "Regression"

    assert context["learner_context"][
        "project_id"
    ] == "project-001"

    assert context["learner_context"][
        "workspace_id"
    ] == "workspace-001"


def test_kie_contract_roadmap_matches_plan():
    payload = {
        "user_id": "backend-demo-003",
        "session_id": "backend-session-003",
        "role": "student",
        "task": "Create my career roadmap",
        "planning_horizon": "career",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "AI Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    plan = data["plan"]

    roadmap = data[
        "metadata"
    ]["roadmap_contract"]

    assert roadmap["planning_horizon"] == "career"

    assert roadmap["career_goal"] == (
        "AI Engineer"
    )

    assert roadmap["milestone_count"] == len(
        roadmap["milestones"]
    )

    assert roadmap["milestone_count"] == len(
        plan
    )

    for milestone, plan_step in zip(
        roadmap["milestones"],
        plan,
    ):
        assert milestone["milestone_id"] == (
            plan_step["step_id"]
        )

        assert milestone["description"] == (
            plan_step["description"]
        )
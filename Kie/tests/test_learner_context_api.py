from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_returns_learner_context():
    payload = {
        "user_id": "context-api-001",
        "session_id": "context-api-session-001",
        "role": "student",
        "task": "Continue my current lesson",
        "learner_stage": "final-year",
        "learner_context": {
            "current_lesson": "Python Functions",
            "current_topic": "Decorators",
            "roadmap_id": "roadmap-001",
            "mission_id": "mission-001",
            "learning_session_id": "learning-session-001",
            "project_id": "project-001",
            "workspace_id": "workspace-001",
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

    learner_context = data["context"]["learner_context"]

    assert learner_context["current_lesson"] == (
        "Python Functions"
    )

    assert learner_context["current_topic"] == (
        "Decorators"
    )

    assert learner_context["roadmap_id"] == (
        "roadmap-001"
    )

    assert learner_context["mission_id"] == (
        "mission-001"
    )

    assert learner_context["learning_session_id"] == (
        "learning-session-001"
    )

    assert learner_context["project_id"] == (
        "project-001"
    )

    assert learner_context["workspace_id"] == (
        "workspace-001"
    )

    assert learner_context["current_progress"][
        "completion_percentage"
    ] == 65


def test_api_returns_empty_learner_context_when_not_provided():
    payload = {
        "user_id": "context-api-002",
        "session_id": "context-api-session-002",
        "role": "student",
        "task": "Create my daily plan",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    learner_context = data["context"]["learner_context"]

    assert learner_context["current_lesson"] is None

    assert learner_context["current_topic"] is None

    assert learner_context["roadmap_id"] is None

    assert learner_context["mission_id"] is None

    assert learner_context["learning_session_id"] is None

    assert learner_context["project_id"] is None

    assert learner_context["workspace_id"] is None

    assert learner_context["current_progress"] == {}


def test_api_tracks_learner_context_source():
    payload = {
        "user_id": "context-api-003",
        "session_id": "context-api-session-003",
        "role": "student",
        "task": "Create my weekly roadmap",
        "learner_context": {
            "roadmap_id": "roadmap-003",
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["context"]["sources"][
        "learner_context"
    ] == "request"
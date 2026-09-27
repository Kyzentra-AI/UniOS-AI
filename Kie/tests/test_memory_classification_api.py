from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_returns_project_memory_category():
    payload = {
        "user_id": "memory-api-001",
        "session_id": "memory-api-session-001",
        "role": "student",
        "task": "Remember this project",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["metadata"]["memory"][
        "updated"
    ] is True

    assert data["metadata"]["memory"][
        "updated_category"
    ] == "projects"

    assert data["metadata"]["memory"][
        "user_id"
    ] == "memory-api-001"


def test_api_returns_goal_memory_category():
    payload = {
        "user_id": "memory-api-002",
        "session_id": "memory-api-session-002",
        "role": "student",
        "task": "Save my career goal",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["metadata"]["memory"][
        "updated"
    ] is True

    assert data["metadata"]["memory"][
        "updated_category"
    ] == "goals"


def test_api_returns_learning_history_for_normal_request():
    payload = {
        "user_id": "memory-api-003",
        "session_id": "memory-api-session-003",
        "role": "student",
        "task": "Create my project plan",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["metadata"]["memory"][
        "updated_category"
    ] == "learning_history"


def test_api_returns_friction_memory_category():
    payload = {
        "user_id": "memory-api-004",
        "session_id": "memory-api-session-004",
        "role": "student",
        "task": "I am struggling with Python",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["metadata"]["memory"][
        "updated_category"
    ] == "friction_context"
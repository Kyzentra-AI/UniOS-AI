from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sprint3_full_roadmap_memory_vertical_slice():
    payload = {
        "user_id": "sprint3-student-001",
        "session_id": "sprint3-session-001",
        "role": "student",
        "task": "Create my weekly learning roadmap",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "university": "Example University",
            "course": "Computer Science",
            "education_level": "B.Tech",
            "semester": 8,
            "graduation_status": "final-year",
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
            "learning_style": "practical",
            "knowledge_level": "intermediate",
            "motivation": "career",
        },
        "learner_context": {
            "current_lesson": "Python Functions",
            "current_topic": "Decorators",
            "roadmap_id": "roadmap-001",
            "mission_id": "mission-001",
            "learning_session_id": "learning-session-001",
            "project_id": "project-001",
            "workspace_id": "workspace-001",
            "current_progress": {
                "completion_percentage": 65,
            },
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    # -------------------------------------------------
    # Identity
    # -------------------------------------------------

    assert data["identity"]["user_id"] == (
        "sprint3-student-001"
    )

    assert data["identity"]["session_id"] == (
        "sprint3-session-001"
    )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    assert data["context"]["learner_stage"] == (
        "final-year"
    )

    assert data["context"]["learner_profile"][
        "career_goal"
    ] == "Software Engineer"

    assert data["context"]["learner_context"][
        "current_topic"
    ] == "Decorators"

    assert data["context"]["learner_context"][
        "project_id"
    ] == "project-001"

    # -------------------------------------------------
    # Intent
    # -------------------------------------------------

    assert data["intent"]["name"] == "LEARN"

    assert data["intent"]["confidence"] == 0.8

    # -------------------------------------------------
    # Planning
    # -------------------------------------------------

    assert len(data["plan"]) == 3

    assert data["metadata"]["roadmap"][
        "planning_horizon"
    ] == "weekly"

    assert data["metadata"]["roadmap"][
        "learner_stage"
    ] == "final-year"

    assert data["metadata"]["roadmap"][
        "career_goal"
    ] == "Software Engineer"

    assert data["metadata"]["roadmap"][
        "milestone_count"
    ] == len(data["plan"])

    assert data["metadata"]["roadmap"][
        "planning_status"
    ] == "generated"

    # -------------------------------------------------
    # Memory
    # -------------------------------------------------

    assert data["metadata"]["memory"][
        "updated"
    ] is True

    assert data["metadata"]["memory"][
        "updated_category"
    ] == "learning_history"

    assert data["metadata"]["memory"][
        "user_id"
    ] == "sprint3-student-001"

    # -------------------------------------------------
    # Trace
    # -------------------------------------------------

    assert data["metadata"]["trace"][
        "request_id"
    ].startswith("req_")

    assert data["metadata"]["trace"][
        "session_id"
    ] == "sprint3-session-001"


def test_sprint3_memory_is_available_on_follow_up():
    payload = {
        "user_id": "sprint3-student-002",
        "session_id": "sprint3-session-002",
        "role": "student",
        "task": "Learn Python decorators",
        "planning_horizon": "daily",
    }

    first_response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert first_response.status_code == 200

    second_payload = {
        "user_id": "sprint3-student-002",
        "session_id": "sprint3-session-003",
        "role": "student",
        "task": "Create my daily learning plan",
        "planning_horizon": "daily",
    }

    second_response = client.post(
        "/kie/execute",
        json=second_payload,
    )

    assert second_response.status_code == 200

    data = second_response.json()

    learning_history = data["context"]["memory"][
        "learning_history"
    ]

    assert len(learning_history) >= 1

    assert learning_history[0]["user_id"] == (
        "sprint3-student-002"
    )

    assert learning_history[0]["content"]["task"] == (
        "Learn Python decorators"
    )


def test_sprint3_different_users_do_not_share_memory():
    first_payload = {
        "user_id": "sprint3-user-A",
        "session_id": "sprint3-session-A",
        "role": "student",
        "task": "Learn Python decorators",
        "planning_horizon": "daily",
    }

    second_payload = {
        "user_id": "sprint3-user-B",
        "session_id": "sprint3-session-B",
        "role": "student",
        "task": "Create my daily learning plan",
        "planning_horizon": "daily",
    }

    first_response = client.post(
        "/kie/execute",
        json=first_payload,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/kie/execute",
        json=second_payload,
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    learning_history = second_data[
        "context"
    ]["memory"]["learning_history"]

    assert learning_history == []
    
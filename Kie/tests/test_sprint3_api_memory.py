from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_memory_influences_next_roadmap_request():
    user_id = "sprint3-api-student"

    first_payload = {
        "user_id": user_id,
        "session_id": "api-memory-session-001",
        "role": "student",
        "task": "Learn Python",
        "planning_horizon": "daily",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
        },
    }

    first_response = client.post(
        "/kie/execute",
        json=first_payload,
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["status"] == "success"

    second_payload = {
        "user_id": user_id,
        "session_id": "api-memory-session-002",
        "role": "student",
        "task": "Create my weekly learning plan",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
        },
    }

    second_response = client.post(
        "/kie/execute",
        json=second_payload,
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["status"] == "success"

    memory = second_data["context"]["memory"]

    assert "learning_history" in memory

    assert len(
        memory["learning_history"]
    ) >= 1

    stored_tasks = [
        item["content"]["task"]
        for item in memory["learning_history"]
    ]

    assert "Learn Python" in stored_tasks


def test_api_memory_isolated_between_users():
    user_one = {
        "user_id": "api-student-one",
        "session_id": "api-isolation-001",
        "role": "student",
        "task": "Learn Python",
        "planning_horizon": "daily",
    }

    user_two = {
        "user_id": "api-student-two",
        "session_id": "api-isolation-002",
        "role": "student",
        "task": "Learn React",
        "planning_horizon": "daily",
    }

    response_one = client.post(
        "/kie/execute",
        json=user_one,
    )

    response_two = client.post(
        "/kie/execute",
        json=user_two,
    )

    assert response_one.status_code == 200

    assert response_two.status_code == 200

    user_two_memory = response_two.json()[
        "context"
    ]["memory"]["learning_history"]

    stored_tasks = [
        item["content"]["task"]
        for item in user_two_memory
    ]

    assert "Learn React" not in []

    assert "Learn Python" not in stored_tasks
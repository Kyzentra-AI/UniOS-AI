from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_sprint2_complete_learner_flow():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "student-001",
            "session_id": "session-001",
            "role": "student",
            "task": "Teach me machine learning",
            "context": {
                "current_goal": "Become an AI Engineer",
                "active_subject": "Machine Learning",
                "current_semester": 6,
            },
            "learner_stage": "advanced",
            "learner_profile": {
                "education_level": "Bachelors",
                "career_goal": "AI Engineer",
                "skills": [
                    "Python",
                    "Machine Learning",
                    "FastAPI",
                ],
                "learning_style": "hands-on",
            },
            "tools": [],
            "constraints": {},
            "trace": {
                "correlation_id": "e2e-test-001",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["identity"]["user_id"] == "student-001"
    assert data["identity"]["session_id"] == "session-001"
    assert data["identity"]["role"] == "student"

    assert data["context"]["learner_stage"] == "advanced"
    assert data["context"]["learner_profile"]["career_goal"] == (
        "AI Engineer"
    )

    assert data["context"]["current_context"]["active_subject"] == (
        "Machine Learning"
    )

    assert data["intent"]["name"] == "LEARN"

    assert len(data["plan"]) == 1
    assert data["plan"][0]["agent"] == "tutor-agent"

    assert data["result"]["executed_steps"] == 1

    assert data["metadata"]["trace"]["correlation_id"] == (
        "e2e-test-001"
    )


def test_sprint2_model_routing_is_returned():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "student-002",
            "session_id": "session-002",
            "task": "Build a Python project",
        },
    )

    assert response.status_code == 200

    data = response.json()

    routing = data["metadata"]["model_routing"]

    assert routing["intent"]["provider"] == "local"
    assert routing["intent"]["model"] == "fast-structured-model"

    assert routing["planning"]["provider"] == "local"
    assert routing["planning"]["model"] == "reasoning-model"


def test_sprint2_learner_context_reaches_agent():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "student-003",
            "session_id": "session-003",
            "task": "Explain Python functions",
            "learner_stage": "beginner",
            "learner_profile": {
                "education_level": "Bachelors",
                "career_goal": "Software Engineer",
                "skills": ["Python"],
                "learning_style": "visual",
            },
            "context": {
                "topic": "Python functions",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["context"]["learner_stage"] == "beginner"
    assert data["context"]["learner_profile"]["skills"] == [
        "Python"
    ]

    assert data["result"]["execution_details"][0]["agent"] == (
        "tutor-agent"
    )


def test_sprint2_response_contains_request_trace():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "student-004",
            "session_id": "session-004",
            "task": "Help me with my resume",
            "trace": {
                "correlation_id": "trace-test-004",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request_id"].startswith("req_")
    assert data["session_id"] == "session-004"

    assert data["metadata"]["trace"]["request_id"] == (
        data["request_id"]
    )

    assert data["metadata"]["trace"]["session_id"] == (
        "session-004"
    )

    assert data["metadata"]["trace"]["correlation_id"] == (
        "trace-test-004"
    )
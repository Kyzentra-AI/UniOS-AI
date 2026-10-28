from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_kie_execute_backend_contract():
    payload = {
        "user_id": "integration-user",
        "session_id": "integration-session",
        "role": "student",
        "task": "Create my weekly study plan",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "university": "Example University",
            "course": "B.Tech CSE",
            "semester": 8,
            "career_goal": "Software Engineer",
            "skills": ["Python", "SQL"],
        },
        "learner_context": {
            "current_topic": "Data Structures",
            "current_progress": {
                "completed_topics": 5,
            },
        },
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    # Top-level response contract
    assert "request_id" in body
    assert body["session_id"] == "integration-session"
    assert "status" in body

    # Identity contract
    assert body["identity"]["user_id"] == "integration-user"
    assert body["identity"]["session_id"] == "integration-session"
    assert body["identity"]["role"] == "student"

    # Context contract
    assert "context" in body
    assert body["context"]["task"] == "Create my weekly study plan"
    assert body["context"]["learner_stage"] == "final-year"

    # Intent contract
    assert "intent" in body
    assert "name" in body["intent"]
    assert "confidence" in body["intent"]

    # Planning contract
    assert isinstance(body["plan"], list)

    # Result contract
    assert "result" in body

    # Metadata contract
    assert "metadata" in body
    assert "planning" in body["metadata"]
    assert "roadmap" in body["metadata"]
    assert "roadmap_contract" in body["metadata"]
    assert "memory" in body["metadata"]


def test_kie_health_endpoint_contract():
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, dict)
    assert "status" in body
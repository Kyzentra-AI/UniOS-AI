
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_build_request_with_artifact_type_succeeds():
    payload = {
        "user_id": "sprint5-build-user",
        "session_id": "sprint5-build-session",
        "role": "student",
        "task": "Build a Python coding project",
        "learner_stage": "final-year",
        "context": {
            "artifact_type": "CODING"
        },
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": ["Python", "SQL"]
        }
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert body["intent"]["name"]
    assert isinstance(body["plan"], list)
    assert len(body["plan"]) > 0
    assert body["result"]["executed_steps"] > 0


def test_build_request_without_artifact_type_still_succeeds():
    payload = {
        "user_id": "sprint5-default-user",
        "session_id": "sprint5-default-session",
        "role": "student",
        "task": "Build a Python project",
        "learner_stage": "final-year"
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert isinstance(body["plan"], list)
    assert body["result"]["executed_steps"] > 0

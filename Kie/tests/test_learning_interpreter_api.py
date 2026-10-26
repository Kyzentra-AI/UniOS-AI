
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_learning_interpret_clarification():
    response = client.post(
        "/api/v1/kie/learn/interpret",
        json={
            "request_id": "test-clarification-001",
            "learner_id": "learner-001",
            "topic": "Python recursion",
            "user_intent": "Explain recursion to me",
            "context": {
                "learner": {"knowledge_level": "beginner"},
                "knowledge_gaps": ["Base cases"],
            },
            "references": [],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["request_id"] == "test-clarification-001"
    assert data["intent_category"] == "CLARIFICATION"
    assert data["pedagogical_strategy"] == "CONCEPT_EXPLANATION"
    assert data["knowledge_gaps_identified"] == ["Base cases"]
    assert data["recommended_difficulty"] == 1


def test_learning_interpret_remediation():
    response = client.post(
        "/api/v1/kie/learn/interpret",
        json={
            "request_id": "test-remediation-001",
            "learner_id": "learner-001",
            "topic": "Python recursion",
            "user_intent": "I'm struggling and need more practice",
            "context": {},
            "references": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["intent_category"] == "REMEDIATION"


def test_learning_interpret_invalid_request():
    response = client.post(
        "/api/v1/kie/learn/interpret",
        json={"request_id": "test-invalid-001"},
    )

    assert response.status_code == 400

    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Invalid request data"

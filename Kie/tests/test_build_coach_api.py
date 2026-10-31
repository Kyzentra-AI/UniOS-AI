from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


def test_build_coach_calls_aiml2(monkeypatch):
    captured = {}

    def mock_coach_build(payload):
        captured.update(payload)
        return {
            "reply": "Let's solve your project step by step.",
            "suggestions": [
                "Review the algorithm.",
                "Write a small test case."
            ],
            "action_items": [
                {
                    "type": "NEXT_STEP",
                    "label": "Test the algorithm",
                    "url": None
                }
            ]
        }

    monkeypatch.setattr(
        routes.aiml2_client,
        "coach_build",
        mock_coach_build
    )

    response = client.post(
        "/api/v1/kie/build/coach",
        json={
            "intent": "guidance",
            "message": "Help me with my Python project",
            "context": {
                "domain": "engineering",
                "stage": "development"
            },
            "project_context": {
                "id": "project-001",
                "title": "Python Graph Project",
                "type": "code_project",
                "status": "in_progress",
                "skills": ["Python", "Algorithms"]
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reply"] == (
        "Let's solve your project step by step."
    )

    assert len(data["suggestions"]) == 2

    assert captured["intent"] == "guidance"
    assert captured["message"] == (
        "Help me with my Python project"
    )

    assert "engineering" in captured["context"]
    assert captured["project_context"]["title"] == (
        "Python Graph Project"
    )


def test_build_coach_handles_aiml2_error(monkeypatch):

    def mock_coach_build(payload):
        raise routes.AIML2ClientError(
            "Unable to communicate with AI/ML-2."
        )

    monkeypatch.setattr(
        routes.aiml2_client,
        "coach_build",
        mock_coach_build
    )

    response = client.post(
        "/api/v1/kie/build/coach",
        json={
            "intent": "guidance",
            "message": "Help me with my project"
        }
    )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == (
        "AIML2_SERVICE_ERROR"
    )
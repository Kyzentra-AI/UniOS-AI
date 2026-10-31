
from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


def test_resume_generation_calls_aiml2(monkeypatch):
    captured = {}

    def mock_generate_resume(payload):
        captured.update(payload)

        return {
            "content": {
                "headline": "Python Full Stack Developer",
                "summary": "Experienced in Python and React.",
                "skills": ["Python", "React", "FastAPI"],
                "education": [],
                "experience": [],
                "projects": [],
                "achievements": [],
            }
        }

    monkeypatch.setattr(
        routes.aiml2_client,
        "generate_resume",
        mock_generate_resume,
    )

    response = client.post(
        "/api/v1/kie/career/resume/generate",
        json={
            "request_id": "req-resume-001",
            "learner_id": "learner-001",
            "title": "Python Developer",
            "source": "manual",
            "preferences": {
                "targetRole": "Python Developer",
                "tone": "professional",
            },
            "content": {
                "skills": ["Python", "React"],
            },
            "career_context": {
                "learnerId": "learner-001",
                "learner": {
                    "skills": ["Python", "React"],
                },
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"]["headline"] == (
        "Python Full Stack Developer"
    )

    assert captured["requestId"] == "req-resume-001"
    assert captured["learnerId"] == "learner-001"
    assert captured["title"] == "Python Developer"

    assert captured["careerContext"]["learnerId"] == (
        "learner-001"
    )


def test_resume_generation_handles_aiml2_error(monkeypatch):

    def mock_generate_resume(payload):
        raise routes.AIML2ClientError(
            "Unable to communicate with AI/ML-2."
        )

    monkeypatch.setattr(
        routes.aiml2_client,
        "generate_resume",
        mock_generate_resume,
    )

    response = client.post(
        "/api/v1/kie/career/resume/generate",
        json={
            "request_id": "req-resume-002",
            "learner_id": "learner-002",
            "title": "Software Engineer",
            "source": "manual",
            "content": {},
            "career_context": {
                "learnerId": "learner-002",
            },
        },
    )

    assert response.status_code == 502

    assert response.json()["detail"]["code"] == (
        "AIML2_SERVICE_ERROR"
    )


def test_resume_generation_rejects_mismatched_learner(
    monkeypatch,
):
    def mock_generate_resume(payload):
        raise AssertionError(
            "AI/ML-2 should not be called for mismatched learners."
        )

    monkeypatch.setattr(
        routes.aiml2_client,
        "generate_resume",
        mock_generate_resume,
    )

    response = client.post(
        "/api/v1/kie/career/resume/generate",
        json={
            "request_id": "req-resume-003",
            "learner_id": "learner-001",
            "title": "Software Engineer",
            "source": "manual",
            "content": {},
            "career_context": {
                "learnerId": "learner-999",
            },
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"]["code"] == (
        "CAREER_CONTEXT_LEARNER_MISMATCH"
    )

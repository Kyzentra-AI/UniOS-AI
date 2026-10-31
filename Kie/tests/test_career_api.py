
from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


client = TestClient(app)


def test_ats_analysis_calls_aiml2(monkeypatch):
    captured = {}

    def mock_analyze_ats(payload):
        captured.update(payload)

        return {
            "summary": "The resume has good technical skills but needs stronger measurable achievements.",
            "findings": [
                {
                    "id": "finding-001",
                    "category": "achievements",
                    "severity": "warning",
                    "title": "Add measurable achievements",
                    "description": "The resume needs measurable results.",
                    "recommendation": "Add quantified project outcomes.",
                }
            ],
        }

    monkeypatch.setattr(
        routes.aiml2_client,
        "analyze_ats",
        mock_analyze_ats,
    )

    response = client.post(
        "/api/v1/kie/career/ats/analyze",
        json={
            "request_id": "ats-001",
            "learner_id": "learner-001",
            "document": {
                "fileName": "resume.pdf",
                "fileType": "pdf",
                "pageCount": 2,
                "extractedCharacterCount": 1200,
            },
            "extracted_text": "Python developer with project experience.",
            "rule_score": {
                "value": 76.5,
                "maxValue": 100,
                "methodology": "defined-rule-based-checks",
                "methodologyVersion": "1.0",
            },
            "rule_findings": [
                {
                    "id": "rule-001",
                    "category": "achievements",
                    "severity": "warning",
                    "title": "Add measurable achievements",
                    "description": "No measurable achievements found.",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert "measurable achievements" in response.json()["summary"]
    assert response.json()["findings"][0]["severity"] == "warning"

    assert captured["requestId"] == "ats-001"
    assert captured["learnerId"] == "learner-001"
    assert captured["ruleScore"]["value"] == 76.5
    assert captured["extractedText"] == (
        "Python developer with project experience."
    )


def test_ats_analysis_handles_aiml2_error(monkeypatch):

    def mock_analyze_ats(payload):
        raise routes.AIML2ClientError(
            "Unable to communicate with AI/ML-2."
        )

    monkeypatch.setattr(
        routes.aiml2_client,
        "analyze_ats",
        mock_analyze_ats,
    )

    response = client.post(
        "/api/v1/kie/career/ats/analyze",
        json={
            "request_id": "ats-002",
            "learner_id": "learner-001",
            "document": {
                "fileName": "resume.pdf",
                "fileType": "pdf",
            },
            "extracted_text": "Python developer.",
            "rule_score": {
                "value": 75,
            },
            "rule_findings": [],
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == (
        "AIML2_SERVICE_ERROR"
    )


def test_build_recommendations_calls_aiml2(monkeypatch):
    captured = {}

    def mock_recommend_builds(learner_id):
        captured["learner_id"] = learner_id

        return {
            "learner_id": learner_id,
            "recommendations": [
                {
                    "recommendation_id": "rec-001",
                    "title": "Python Task Worker",
                    "type": "code_project",
                    "difficulty": "intermediate",
                    "academic_domain": "computer_science",
                    "description": "Build an asynchronous task worker.",
                    "rationale": "Improves backend engineering skills.",
                    "skills": ["Python", "FastAPI"],
                    "estimated_effort_hours": 15.0,
                    "prerequisite_topics": ["Data Structures"],
                }
            ],
            "recommendation_rationale": "Based on learner skills.",
            "generated_at": "2026-10-30T16:27:02Z",
        }

    monkeypatch.setattr(
        routes.aiml2_client,
        "recommend_builds",
        mock_recommend_builds,
    )

    response = client.get(
        "/api/v1/kie/build/recommend",
        params={"learner_id": "learner-001"},
    )

    assert response.status_code == 200
    assert captured["learner_id"] == "learner-001"

    data = response.json()
    assert data["learner_id"] == "learner-001"
    assert data["recommendations"][0]["title"] == (
        "Python Task Worker"
    )
    assert data["recommendations"][0]["difficulty"] == (
        "intermediate"
    )


def test_build_recommendations_handles_aiml2_error(monkeypatch):

    def mock_recommend_builds(learner_id):
        raise routes.AIML2ClientError(
            "Unable to communicate with AI/ML-2."
        )

    monkeypatch.setattr(
        routes.aiml2_client,
        "recommend_builds",
        mock_recommend_builds,
    )

    response = client.get(
        "/api/v1/kie/build/recommend",
        params={"learner_id": "learner-001"},
    )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == (
        "AIML2_SERVICE_ERROR"
    )

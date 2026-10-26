
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/kie/achievement/event"


def test_achievement_event_returns_candidate():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-101",
            "activity_id": "activity-501",
            "activity_type": "project",
            "activity_title": "Build a REST API",
            "outcome": "Implemented CRUD endpoints and tests",
            "evidence": [
                "Repository test report",
                "API implementation summary",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["event_type"] == "achievement_candidate"
    assert data["learner_id"] == "learner-101"
    assert data["activity_id"] == "activity-501"
    assert data["achievement_title"] == "Completed: Build a REST API"
    assert data["verification_status"] == "pending_backend_verification"
    assert data["persistence_owner"] == "backend"
    assert len(data["evidence"]) == 2


def test_achievement_event_normalizes_text():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": " learner-102 ",
            "activity_id": " activity-502 ",
            "activity_type": " PROJECT ",
            "activity_title": " Build a dashboard ",
            "outcome": " Completed a working prototype ",
            "evidence": [" Test report "],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["learner_id"] == "learner-102"
    assert data["activity_id"] == "activity-502"
    assert data["activity_type"] == "project"
    assert data["activity_title"] == "Build a dashboard"
    assert data["evidence"] == ["Test report"]


def test_achievement_event_requires_evidence():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-103",
            "activity_id": "activity-503",
            "activity_type": "research",
            "activity_title": "Research report",
            "outcome": "Completed the report",
            "evidence": [],
        },
    )

    assert response.status_code in (400, 422)


def test_blank_evidence_is_rejected():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-104",
            "activity_id": "activity-504",
            "activity_type": "competition",
            "activity_title": "Data challenge",
            "outcome": "Submitted the analysis",
            "evidence": ["   "],
        },
    )

    assert response.status_code == 400

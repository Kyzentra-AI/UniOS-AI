
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_competition_plan_endpoint_returns_hackathon_plan():
    response = client.post(
        "/api/v1/kie/competition/plan",
        json={
            "challenge_title": "Green Tech Hackathon",
            "challenge_statement": "Build a prototype and present a demo.",
            "challenge_type": "hackathon",
            "deadline_days": 4,
            "learner_context": {"skills": ["Python"]},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["challenge_title"] == "Green Tech Hackathon"
    assert len(data["preparation_plan"]) == 4
    assert data["success_checklist"]
    assert data["collaboration_guidance"]


def test_competition_plan_endpoint_supports_research():
    response = client.post(
        "/api/v1/kie/competition/plan",
        json={
            "challenge_title": "Research Challenge",
            "challenge_statement": "Analyze data and report findings.",
            "challenge_type": "research",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["preparation_plan"][0]["title"] == "Define the research question"


def test_competition_plan_endpoint_validates_deadline():
    response = client.post(
        "/api/v1/kie/competition/plan",
        json={
            "challenge_title": "Test Challenge",
            "challenge_statement": "Complete the task.",
            "deadline_days": 0,
        },
    )

    assert response.status_code == 422

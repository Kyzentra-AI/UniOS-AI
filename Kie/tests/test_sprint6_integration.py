
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_all_sprint6_endpoints_are_registered():
    paths = app.openapi()["paths"]

    assert "/api/v1/kie/challenge/analyze" in paths
    assert "/api/v1/kie/competition/plan" in paths
    assert "/api/v1/kie/competition/collaborate" in paths

    assert "post" in paths["/api/v1/kie/challenge/analyze"]
    assert "post" in paths["/api/v1/kie/competition/plan"]
    assert "post" in paths["/api/v1/kie/competition/collaborate"]


def test_challenge_analysis_accepts_non_hackathon_type():
    response = client.post(
        "/api/v1/kie/challenge/analyze",
        json={
            "challenge_title": "Research Challenge",
            "challenge_statement": (
                "Investigate the issue and analyze the evidence."
            ),
            "challenge_type": "research",
        },
    )

    assert response.status_code == 200
    assert response.json()["challenge_type"] == "research"


def test_competition_planning_accepts_business_challenge():
    response = client.post(
        "/api/v1/kie/competition/plan",
        json={
            "challenge_title": "Startup Challenge",
            "challenge_statement": (
                "Validate the business idea and present a pitch."
            ),
            "challenge_type": "business",
            "deadline_days": 8,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["challenge_type"] == "business"
    assert len(data["preparation_plan"]) == 4


def test_collaboration_returns_dependency_order():
    response = client.post(
        "/api/v1/kie/competition/collaborate",
        json={
            "challenge_title": "Research Challenge",
            "challenge_statement": "Research and present the findings.",
            "challenge_type": "research",
            "team_members": ["Alex", "Sam"],
        },
    )

    assert response.status_code == 200
    tasks = response.json()["tasks"]

    assert tasks[0]["depends_on"] == []
    assert tasks[1]["depends_on"] == ["Understand requirements"]
    assert tasks[2]["depends_on"] == ["Plan the approach"]
    assert tasks[3]["depends_on"] == ["Complete the main work"]

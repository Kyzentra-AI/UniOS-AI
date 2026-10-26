
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_collaboration_endpoint_returns_team_tasks():
    response = client.post(
        "/api/v1/kie/competition/collaborate",
        json={
            "challenge_title": "Green Tech Challenge",
            "challenge_statement": "Build a prototype and present a demo.",
            "challenge_type": "hackathon",
            "team_members": ["Priya", "Alex"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["challenge_title"] == "Green Tech Challenge"
    assert len(data["tasks"]) == 4
    assert data["tasks"][0]["suggested_owner"] == "Priya"
    assert data["tasks"][1]["suggested_owner"] == "Alex"
    assert "version_control" in data["suggested_tool_categories"]


def test_collaboration_endpoint_supports_research():
    response = client.post(
        "/api/v1/kie/competition/collaborate",
        json={
            "challenge_title": "Research Challenge",
            "challenge_statement": "Analyze data and evaluate evidence.",
            "challenge_type": "research",
            "team_members": ["Sam"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["tasks"][2]["title"] == "Gather and analyze evidence"
    assert "research_sources" in data["suggested_tool_categories"]


def test_collaboration_endpoint_accepts_missing_optional_members():
    response = client.post(
        "/api/v1/kie/competition/collaborate",
        json={
            "challenge_title": "Community Challenge",
            "challenge_statement": "Propose a community solution.",
        },
    )

    assert response.status_code == 200
    assert all(
        task["suggested_owner"] is None
        for task in response.json()["tasks"]
    )


def test_collaboration_endpoint_rejects_missing_required_fields():
    response = client.post(
        "/api/v1/kie/competition/collaborate",
        json={"challenge_title": "Incomplete"},
    )

    assert response.status_code == 422

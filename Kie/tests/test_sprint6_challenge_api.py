
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_challenge_analyze_endpoint_returns_analysis():
    response = client.post(
        "/api/v1/kie/challenge/analyze",
        json={
            "challenge_title": "Clean Water Challenge",
            "challenge_statement": (
                "Develop a prototype. Present the findings. "
                "Submit the final solution."
            ),
            "challenge_type": "general",
            "learner_context": {"skills": ["Python"]},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["challenge_title"] == "Clean Water Challenge"
    assert data["challenge_type"] == "general"
    assert len(data["requirements"]) == 3
    assert data["suggested_deliverables"]


def test_challenge_analyze_supports_research_challenges():
    response = client.post(
        "/api/v1/kie/challenge/analyze",
        json={
            "challenge_title": "Research Challenge",
            "challenge_statement": "Investigate the issue and analyze evidence.",
            "challenge_type": "research",
        },
    )

    assert response.status_code == 200
    assert response.json()["challenge_type"] == "research"


def test_challenge_analyze_rejects_missing_required_fields():
    response = client.post(
        "/api/v1/kie/challenge/analyze",
        json={"challenge_title": "Incomplete Challenge"},
    )

    assert response.status_code == 422

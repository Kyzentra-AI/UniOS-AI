
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINT = "/api/v1/kie/competition/recommend"


def test_competition_recommendations_success():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-1",
            "learner_context": {
                "skills": ["Python", "programming"],
                "interests": ["coding", "technology"],
                "goals": ["build software"],
            },
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data["recommendations"]) == 3
    assert all(item["title"] for item in data["recommendations"])
    assert all(
        0 <= item["relevance_score"] <= 100
        for item in data["recommendations"]
    )


def test_different_contexts_change_top_recommendation():
    coding_response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-coding",
            "learner_context": {
                "skills": ["Python", "programming"],
                "interests": ["coding", "technology"],
            },
        },
    )

    research_response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-research",
            "learner_context": {
                "skills": ["research", "data analysis"],
                "interests": ["research", "science", "data"],
            },
        },
    )

    assert coding_response.status_code == 200
    assert research_response.status_code == 200

    coding_top = coding_response.json()["recommendations"][0]
    research_top = research_response.json()["recommendations"][0]

    assert coding_top["challenge_type"] != research_top["challenge_type"]
    assert research_top["challenge_type"] == "research"


def test_recommendation_limit_is_respected():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-2",
            "learner_context": {"interests": ["design"]},
            "limit": 2,
        },
    )

    assert response.status_code == 200
    assert len(response.json()["recommendations"]) == 2


def test_invalid_recommendation_limit_returns_validation_error():
    response = client.post(
        ENDPOINT,
        json={
            "learner_id": "learner-3",
            "learner_context": {},
            "limit": 0,
        },
    )

    # Accept the project's existing validation behavior.
    assert response.status_code in (400, 422)

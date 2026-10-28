from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_returns_roadmap_contract():
    payload = {
        "user_id": "roadmap-api-001",
        "session_id": "roadmap-api-session-001",
        "role": "student",
        "task": "Create my weekly learning roadmap",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
            ],
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    roadmap = data["metadata"]["roadmap_contract"]

    assert roadmap["user_id"] == "roadmap-api-001"

    assert roadmap["session_id"] == (
        "roadmap-api-session-001"
    )

    assert roadmap["planning_horizon"] == "weekly"

    assert roadmap["learner_stage"] == "final-year"

    assert roadmap["career_goal"] == (
        "Software Engineer"
    )

    assert roadmap["milestone_count"] == 3

    assert roadmap["planning_status"] == "generated"


def test_api_roadmap_contract_contains_milestones():
    payload = {
        "user_id": "roadmap-api-002",
        "session_id": "roadmap-api-session-002",
        "role": "student",
        "task": "Create my career roadmap",
        "planning_horizon": "career",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "AI Engineer",
            "skills": [
                "Python",
            ],
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    roadmap = data["metadata"]["roadmap_contract"]

    milestones = roadmap["milestones"]

    assert len(milestones) == 4

    assert milestones[0]["milestone_id"] == "step-1"

    assert milestones[0]["status"] == "planned"

    assert milestones[0]["agent"] == "career-agent"


def test_api_roadmap_contract_matches_plan_count():
    payload = {
        "user_id": "roadmap-api-003",
        "session_id": "roadmap-api-session-003",
        "role": "student",
        "task": "Create my daily learning plan",
        "planning_horizon": "daily",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    roadmap = data["metadata"]["roadmap_contract"]

    assert roadmap["milestone_count"] == len(
        data["plan"]
    )

    assert roadmap["milestone_count"] == len(
        roadmap["milestones"]
    )
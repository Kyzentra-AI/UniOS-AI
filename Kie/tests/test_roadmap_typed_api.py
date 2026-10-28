from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_serializes_typed_roadmap_contract():
    payload = {
        "user_id": "typed-roadmap-001",
        "session_id": "typed-roadmap-session-001",
        "role": "student",
        "task": "Create my weekly roadmap",
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

    assert isinstance(roadmap, dict)

    assert roadmap["user_id"] == "typed-roadmap-001"

    assert roadmap["session_id"] == (
        "typed-roadmap-session-001"
    )

    assert roadmap["planning_horizon"] == "weekly"

    assert roadmap["learner_stage"] == "final-year"

    assert roadmap["career_goal"] == (
        "Software Engineer"
    )

    assert isinstance(
        roadmap["milestones"],
        list,
    )

    assert len(roadmap["milestones"]) == (
        roadmap["milestone_count"]
    )


def test_api_serializes_typed_milestones():
    payload = {
        "user_id": "typed-roadmap-002",
        "session_id": "typed-roadmap-session-002",
        "role": "student",
        "task": "Create my career roadmap",
        "planning_horizon": "career",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "AI Engineer",
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    milestones = data[
        "metadata"
    ]["roadmap_contract"]["milestones"]

    assert len(milestones) == 4

    for milestone in milestones:
        assert isinstance(
            milestone,
            dict,
        )

        assert "milestone_id" in milestone

        assert "description" in milestone

        assert "agent" in milestone

        assert milestone["status"] == "planned"


def test_api_roadmap_contract_matches_response_plan():
    payload = {
        "user_id": "typed-roadmap-003",
        "session_id": "typed-roadmap-session-003",
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

    roadmap = data[
        "metadata"
    ]["roadmap_contract"]

    plan = data["plan"]

    milestones = roadmap["milestones"]

    assert len(milestones) == len(plan)

    for milestone, plan_step in zip(
        milestones,
        plan,
    ):
        assert milestone["milestone_id"] == (
            plan_step["step_id"]
        )

        assert milestone["description"] == (
            plan_step["description"]
        )

        assert milestone["agent"] == (
            plan_step["agent"]
        )
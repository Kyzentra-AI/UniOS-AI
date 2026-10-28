from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_weekly_roadmap_metadata():
    payload = {
        "user_id": "roadmap-student-001",
        "session_id": "roadmap-session-001",
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

    roadmap = data["metadata"]["roadmap"]

    assert roadmap["planning_horizon"] == "weekly"

    assert roadmap["learner_stage"] == "final-year"

    assert roadmap["career_goal"] == "Software Engineer"

    assert roadmap["milestone_count"] == 3

    assert roadmap["planning_status"] == "generated"


def test_career_roadmap_metadata():
    payload = {
        "user_id": "roadmap-student-002",
        "session_id": "roadmap-session-002",
        "role": "student",
        "task": "Create my career roadmap",
        "planning_horizon": "career",
        "learner_profile": {
            "career_goal": "Data Scientist",
            "skills": [
                "Python",
                "Machine Learning",
            ],
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    roadmap = data["metadata"]["roadmap"]

    assert roadmap["planning_horizon"] == "career"

    assert roadmap["career_goal"] == "Data Scientist"

    assert roadmap["milestone_count"] == 4

    assert roadmap["planning_status"] == "generated"


def test_semester_roadmap_metadata():
    payload = {
        "user_id": "roadmap-student-003",
        "session_id": "roadmap-session-003",
        "role": "student",
        "task": "Create my semester roadmap",
        "planning_horizon": "semester",
        "learner_stage": "final-year",
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    roadmap = data["metadata"]["roadmap"]

    assert roadmap["planning_horizon"] == "semester"

    assert roadmap["milestone_count"] == 4

    assert roadmap["planning_status"] == "generated"


def test_roadmap_metadata_matches_plan():
    payload = {
        "user_id": "roadmap-student-004",
        "session_id": "roadmap-session-004",
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

    roadmap = data["metadata"]["roadmap"]

    assert roadmap["milestone_count"] == len(
        data["plan"]
    )

    assert roadmap["planning_status"] == "generated"
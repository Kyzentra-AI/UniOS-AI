from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_weekly_planning_through_kie_api():
    payload = {
        "user_id": "student-001",
        "session_id": "session-sprint3-001",
        "role": "student",
        "task": "Create my weekly learning plan for Python",
        "planning_horizon": "weekly",
        "learner_stage": "final-year",
        "learner_profile": {
            "university": "Raghu Engineering College",
            "course": "CSE Data Science",
            "education_level": "B.Tech",
            "semester": 8,
            "graduation_status": "final-year",
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "SQL",
                "React",
            ],
            "learning_style": "practical",
            "knowledge_level": "intermediate",
            "motivation": "career preparation",
        },
    }

    response = client.post(
        "/kie/execute",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["session_id"] == "session-sprint3-001"

    assert data["metadata"]["planning"]["horizon"] == "weekly"

    assert len(data["plan"]) == 3

    assert data["plan"][0]["step_id"] == "step-1"

    assert data["plan"][0]["agent"] == "tutor-agent"

    assert data["plan"][1]["step_id"] == "step-2"

    assert data["plan"][2]["step_id"] == "step-3"


def test_career_planning_through_kie_api():
    payload = {
        "user_id": "student-002",
        "session_id": "session-sprint3-002",
        "role": "student",
        "task": "Create my career roadmap for software engineering",
        "planning_horizon": "career",
        "learner_stage": "final-year",
        "learner_profile": {
            "career_goal": "Software Engineer",
            "skills": [
                "Python",
                "JavaScript",
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

    assert data["status"] == "success"

    assert data["metadata"]["planning"]["horizon"] == "career"

    assert len(data["plan"]) == 4

    assert data["plan"][0]["agent"] == "career-agent"
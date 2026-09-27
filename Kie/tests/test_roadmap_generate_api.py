from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_roadmap_generate_academic():

    payload = {
        "learner": {
            "id": "learner-001",
            "primary_goal": "Become a strong software engineer",
        },
        "education": {
            "degree": "B.Tech",
            "semester": 7,
        },
        "career": {
            "target_skills": [
                "Python",
                "SQL",
            ]
        },
        "skills": [
            "Python",
            "JavaScript",
        ],
        "preferences": {
            "learning_style": "hands-on",
        },
        "syllabus": {
            "subjects": [
                {
                    "name": "Data Structures",
                    "topics": [
                        "Arrays",
                        "Linked Lists",
                        "Trees",
                    ],
                }
            ]
        },
        "roadmap": {},
        "recent_history": [],
        "memory_summary": "",
        "scope": "ACADEMIC",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scope"] == "ACADEMIC"

    assert len(
        data["semesters"]
    ) >= 1

    assert data["semesters"][0][
        "subjects"
    ][0]["name"] == "Data Structures"

    assert len(
        data["missions"]
    ) > 0


def test_roadmap_generate_career():

    payload = {
        "learner": {
            "id": "learner-002",
            "primary_goal": "Become an AI Engineer",
        },
        "education": {},
        "career": {
            "target_skills": [
                "Python",
                "Machine Learning",
                "FastAPI",
            ]
        },
        "skills": [
            "Python",
        ],
        "preferences": {},
        "syllabus": {},
        "roadmap": {},
        "recent_history": [],
        "memory_summary": "Learner prefers practical projects.",
        "scope": "CAREER",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scope"] == "CAREER"

    assert data["semesters"] == []

    assert data["career"] is not None

    assert (
        "Become an AI Engineer"
        in data["career"]["goals"]
    )

    assert len(
        data["missions"]
    ) > 0


def test_roadmap_generate_both():

    payload = {
        "learner": {
            "id": "learner-003",
            "primary_goal": "Become a Data Scientist",
        },
        "education": {
            "degree": "B.Tech",
        },
        "career": {
            "target_skills": [
                "Python",
                "SQL",
                "Machine Learning",
            ]
        },
        "skills": [
            "Python",
            "SQL",
        ],
        "preferences": {},
        "syllabus": {
            "subjects": [
                {
                    "name": "Machine Learning",
                    "topics": [
                        "Regression",
                        "Classification",
                    ],
                }
            ]
        },
        "roadmap": {},
        "recent_history": [
            {
                "event": "completed_python",
            }
        ],
        "memory_summary": "Python fundamentals completed.",
        "scope": "BOTH",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["scope"] == "BOTH"

    assert len(
        data["semesters"]
    ) >= 1

    assert data["career"] is not None

    assert len(
        data["goals"]
    ) > 0

    assert len(
        data["milestones"]
    ) > 0

    assert len(
        data["missions"]
    ) > 0


def test_roadmap_generate_mission_enum_values():

    payload = {
        "learner": {
            "id": "learner-004",
            "primary_goal": "Become a backend developer",
        },
        "career": {
            "target_skills": [
                "FastAPI",
            ]
        },
        "scope": "CAREER",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 200

    allowed_types = {
        "LEARNING",
        "REVISION",
        "ASSIGNMENT",
        "PRACTICAL",
        "ARTIFACT",
        "CAREER",
    }

    for mission in response.json()[
        "missions"
    ]:

        assert mission["type"] in allowed_types

        assert mission["estimated_minutes"] > 0

        assert mission["week"] >= 1

        assert mission["sequence"] >= 1


def test_roadmap_generate_invalid_scope():

    payload = {
        "learner": {
            "id": "learner-005",
            "primary_goal": "Learn Python",
        },
        "scope": "INVALID",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 400


def test_roadmap_generate_requires_learner():

    payload = {
        "scope": "ACADEMIC",
    }

    response = client.post(
        "/api/v1/kie/roadmap/generate",
        json=payload,
    )

    assert response.status_code == 400
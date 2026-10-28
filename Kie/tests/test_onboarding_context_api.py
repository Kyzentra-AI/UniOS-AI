from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_onboarding_context():
    response = client.post(
        "/api/v1/kie/context/analyze",
        json={
            "user_id": "usr_12345abc",
            "session_id": "sess_9876xyz",
            "initial_context": {
                "role": "Software Engineer",
                "industry": "Fintech",
                "goals": [
                    "Improve coding speed",
                    "Learn new frameworks",
                ],
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["requires_more_info"] is True
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) >= 1

    question_ids = {
        question["question_id"]
        for question in data["questions"]
    }

    assert "q_001" in question_ids
    assert "q_002" in question_ids


def test_resolve_onboarding_context():
    response = client.post(
        "/api/v1/kie/context/resolve",
        json={
            "user_id": "usr_12345abc",
            "session_id": "sess_9876xyz",
            "answers": [
                {
                    "question_id": "q_001",
                    "answer": ["Python", "Go"],
                },
                {
                    "question_id": "q_002",
                    "answer": "Senior",
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "new_context" in data

    assert data["new_context"]["primary_languages"] == [
        "Python",
        "Go",
    ]

    assert (
        data["new_context"]["experience_level"]
        == "Senior"
    )


def test_analyze_onboarding_context_validation():
    response = client.post(
        "/api/v1/kie/context/analyze",
        json={
            "user_id": "",
            "session_id": "sess_9876xyz",
            "initial_context": {},
        },
    )

    assert response.status_code == 400


def test_resolve_onboarding_context_validation():
    response = client.post(
        "/api/v1/kie/context/resolve",
        json={
            "user_id": "usr_12345abc",
            "session_id": "",
            "answers": [],
        },
    )

    assert response.status_code == 400
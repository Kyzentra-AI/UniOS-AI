from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "kie-core",
    }


def test_kie_execute_success():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "task": "Explain binary search",
            "context": {
                "topic": "data structures",
            },
            "tools": [],
            "constraints": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["intent"]["name"] == "LEARN"
    assert data["plan"][0]["agent"] == "tutor-agent"


def test_kie_execute_validation_error():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "",
            "session_id": "session-001",
            "task": "",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_learn_request_selects_tutor_agent():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "task": "Teach me Python",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "LEARN"
    assert data["plan"][0]["agent"] == "tutor-agent"


def test_build_request_selects_project_agent():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "task": "Build a Python project",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "BUILD"
    assert data["plan"][0]["agent"] == "project-agent"


def test_compete_request_selects_hackathon_agent():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "task": "Help me with a hackathon",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "COMPETE"
    assert data["plan"][0]["agent"] == "hackathon-agent"


def test_launch_request_selects_career_agent():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-001",
            "session_id": "session-001",
            "task": "Help me prepare for an interview",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "LAUNCH"
    assert data["plan"][0]["agent"] == "career-agent"


def test_identity_and_context_are_processed():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-002",
            "session_id": "session-002",
            "role": "student",
            "task": "Teach me Python functions",
            "context": {
                "topic": "Python",
                "current_goal": "Learn programming",
            },
            "learner_stage": "beginner",
            "learner_profile": {
                "education_level": "Bachelors",
                "career_goal": "Software Engineer",
                "skills": [
                    "Python",
                    "JavaScript",
                ],
                "learning_style": "visual",
            },
            "tools": [],
            "constraints": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["identity"]["user_id"] == "user-002"
    assert data["identity"]["session_id"] == "session-002"
    assert data["identity"]["role"] == "student"

    assert data["context"]["current_context"]["topic"] == "Python"
    assert (
        data["context"]["current_context"]["current_goal"]
        == "Learn programming"
    )

    assert data["context"]["learner_stage"] == "beginner"

    assert (
        data["context"]["learner_profile"]["education_level"]
        == "Bachelors"
    )

    assert (
        data["context"]["learner_profile"]["career_goal"]
        == "Software Engineer"
    )

    assert data["context"]["learner_profile"]["skills"] == [
        "Python",
        "JavaScript",
    ]

    assert (
        data["context"]["learner_profile"]["learning_style"]
        == "visual"
    )

    assert data["context"]["task"] == "Teach me Python functions"

    assert data["context"]["sources"]["current_context"] == "request"
    assert data["context"]["sources"]["learner_stage"] == "request"
    assert data["context"]["sources"]["learner_profile"] == "request"
    assert data["context"]["sources"]["task"] == "request"

    assert data["intent"]["name"] == "LEARN"
    assert data["plan"][0]["agent"] == "tutor-agent"


def test_role_defaults_to_student():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-003",
            "session_id": "session-003",
            "task": "Explain variables",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["identity"]["role"] == "student"


def test_learner_profile_reaches_kie_response():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-004",
            "session_id": "session-004",
            "role": "student",
            "task": "Help me plan my learning",
            "learner_stage": "intermediate",
            "learner_profile": {
                "education_level": "Bachelors",
                "career_goal": "AI Engineer",
                "skills": [
                    "Python",
                    "Machine Learning",
                ],
                "learning_style": "hands-on",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    profile = data["context"]["learner_profile"]

    assert profile["education_level"] == "Bachelors"
    assert profile["career_goal"] == "AI Engineer"
    assert profile["skills"] == [
        "Python",
        "Machine Learning",
    ]
    assert profile["learning_style"] == "hands-on"

    assert data["context"]["learner_stage"] == "intermediate"
    assert (
        data["context"]["sources"]["learner_profile"]
        == "request"
    )


def test_unios_style_learner_context():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "unios-user-001",
            "session_id": "unios-session-001",
            "role": "student",
            "task": "Create a roadmap for becoming an AI Engineer",
            "context": {
                "current_goal": "Become an AI Engineer",
                "active_subject": "Machine Learning",
                "current_semester": 6,
            },
            "learner_stage": "advanced",
            "learner_profile": {
                "education_level": "Bachelors",
                "career_goal": "AI Engineer",
                "skills": [
                    "Python",
                    "Machine Learning",
                    "FastAPI",
                ],
                "learning_style": "hands-on",
            },
            "tools": [],
            "constraints": {},
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert data["identity"]["user_id"] == "unios-user-001"
    assert data["identity"]["session_id"] == "unios-session-001"
    assert data["identity"]["role"] == "student"

    assert (
        data["context"]["current_context"]["current_goal"]
        == "Become an AI Engineer"
    )

    assert (
        data["context"]["current_context"]["active_subject"]
        == "Machine Learning"
    )

    assert data["context"]["current_context"]["current_semester"] == 6

    assert data["context"]["learner_stage"] == "advanced"

    assert (
        data["context"]["learner_profile"]["education_level"]
        == "Bachelors"
    )

    assert (
        data["context"]["learner_profile"]["career_goal"]
        == "AI Engineer"
    )

    assert data["context"]["learner_profile"]["skills"] == [
        "Python",
        "Machine Learning",
        "FastAPI",
    ]

    assert (
        data["context"]["learner_profile"]["learning_style"]
        == "hands-on"
    )

    assert (
        data["context"]["sources"]["learner_profile"]
        == "request"
    )

    assert data["intent"]["name"] == "GENERAL"


def test_trace_correlation_id_is_preserved():
    response = client.post(
        "/kie/execute",
        json={
            "user_id": "user-005",
            "session_id": "session-005",
            "task": "Explain Python decorators",
            "trace": {
                "correlation_id": "unios-correlation-001",
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert (
        data["metadata"]["trace"]["correlation_id"]
        == "unios-correlation-001"
    )

    assert (
        data["metadata"]["trace"]["session_id"]
        == "session-005"
    )

    assert data["metadata"]["trace"]["request_id"].startswith(
        "req_"
    )
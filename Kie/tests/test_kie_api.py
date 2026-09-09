from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_kie_execute_success():
    payload = {
        "user_id": "user-001",
        "session_id": "session-001",
        "task": "Explain how binary search works",
        "intent": None,
        "context": {
            "topic": "data structures"
        },
        "tools": [],
        "constraints": {}
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["session_id"] == "session-001"
    assert data["intent"]["name"] == "LEARN"
    assert data["intent"]["confidence"] == 0.8
    assert len(data["plan"]) == 1
    assert data["result"]["executed_steps"] == 1


def test_kie_execute_validation_error():
    payload = {
        "user_id": "   ",
        "session_id": "session-001",
        "task": "   "
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 400

    data = response.json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "VALIDATION_ERROR"
def test_learn_request_selects_tutor_agent():
    payload = {
        "user_id": "user-001",
        "session_id": "session-001",
        "task": "Teach me Python basics",
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "LEARN"
    assert data["plan"][0]["agent"] == "tutor-agent"
    assert data["result"]["execution_details"][0]["agent"] == "tutor-agent"


def test_build_request_selects_project_agent():
    payload = {
        "user_id": "user-001",
        "session_id": "session-001",
        "task": "Build a React project",
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "BUILD"
    assert data["plan"][0]["agent"] == "project-agent"
    assert data["result"]["execution_details"][0]["agent"] == "project-agent"


def test_compete_request_selects_hackathon_agent():
    payload = {
        "user_id": "user-001",
        "session_id": "session-001",
        "task": "Help me prepare for a hackathon",
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "COMPETE"
    assert data["plan"][0]["agent"] == "hackathon-agent"
    assert data["result"]["execution_details"][0]["agent"] == "hackathon-agent"


def test_launch_request_selects_career_agent():
    payload = {
        "user_id": "user-001",
        "session_id": "session-001",
        "task": "Help me prepare my resume",
    }

    response = client.post("/kie/execute", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"]["name"] == "LAUNCH"
    assert data["plan"][0]["agent"] == "career-agent"
    assert data["result"]["execution_details"][0]["agent"] == "career-agent"

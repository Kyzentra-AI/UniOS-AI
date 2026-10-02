import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

from app.core.deps import get_current_user

@pytest.fixture
def mock_get_current_user():
    user = {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def mock_supabase_admin():
    with patch("app.api.v1.endpoints.learning.supabase_admin") as mock_learn, \
         patch("app.api.v1.endpoints.assessments.supabase_admin") as mock_assess:
        yield mock_learn

def test_start_session_learner_not_found(mock_get_current_user, mock_supabase_admin):
    # Setup mock to return empty data for learner
    mock_supabase_admin.table().select().eq().execute.return_value.data = []
    
    response = client.post("/api/v1/learning/sessions", json={
        "topic": "Python 101",
        "lesson_id": "py-101"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Learner profile not found"

@patch("app.api.v1.endpoints.learning.learning_session_service")
def test_get_session(mock_service, mock_get_current_user, mock_supabase_admin):
    mock_supabase_admin.table().select().eq().execute.return_value.data = [{"id": "00000000-0000-0000-0000-000000000001"}]
    mock_service.get_session.return_value = {
        "id": "00000000-0000-0000-0000-000000000002",
        "learner_id": "00000000-0000-0000-0000-000000000001",
        "topic": "Python 101",
        "lesson_id": "py-101",
        "status": "IN_PROGRESS",
        "progress_percentage": 0,
        "created_at": "2026-10-02T12:00:00Z",
        "updated_at": "2026-10-02T12:00:00Z"
    }
    
    response = client.get("/api/v1/learning/sessions/00000000-0000-0000-0000-000000000002")
    
    assert response.status_code == 200
    assert response.json()["id"] == "00000000-0000-0000-0000-000000000002"
    assert response.json()["topic"] == "Python 101"

@patch("app.api.v1.endpoints.assessments.assessment_service")
def test_submit_assessment_attempt(mock_service, mock_get_current_user, mock_supabase_admin):
    mock_supabase_admin.table().select().eq().execute.return_value.data = [{"id": "00000000-0000-0000-0000-000000000001"}]
    
    # We mock the async record_attempt method
    async def mock_record(*args, **kwargs):
        return {
            "id": "00000000-0000-0000-0000-000000000003",
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "assessment_id": "quiz-001",
            "topic": "Python",
            "answers": [],
            "score": 0.8,
            "total_time_spent_seconds": 60,
            "hints_used_count": 0,
            "is_completed": True,
            "created_at": "2026-10-02T12:00:00Z"
        }
    
    mock_service.record_attempt = mock_record
    
    response = client.post("/api/v1/assessments/attempts", json={
        "assessment_id": "quiz-001",
        "topic": "Python",
        "total_time_spent_seconds": 60,
        "answers": []
    })
    
    assert response.status_code == 200
    assert response.json()["id"] == "00000000-0000-0000-0000-000000000003"
    assert response.json()["score"] == 0.8

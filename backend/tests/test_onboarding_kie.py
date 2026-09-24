import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.deps import get_current_user

# Setup client and dependency overrides
client = TestClient(app)

def override_get_current_user():
    return {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def mock_supabase_admin():
    with patch("app.api.v1.endpoints.onboarding.supabase_admin") as mock:
        yield mock

@pytest.fixture
def mock_kie_service():
    with patch("app.api.v1.endpoints.onboarding.kie_service") as mock:
        yield mock

def test_get_kie_questions_existing(mock_supabase_admin, mock_kie_service):
    # Mock learner profile with pending questions
    mock_res = MagicMock()
    mock_res.data = [{
        "id": "l-123",
        "pending_kie_questions": [{"question_id": "q1", "text": "Test?"}]
    }]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    response = client.get("/api/v1/onboarding/questions")
    assert response.status_code == 200
    assert response.json()["status"] == "pending_context"
    assert len(response.json()["questions"]) == 1
    assert mock_kie_service.analyze_context.call_count == 0

def test_get_kie_questions_triggers_analysis(mock_supabase_admin, mock_kie_service):
    # Mock learner profile with NO pending questions
    mock_res = MagicMock()
    mock_res.data = [{
        "id": "l-123",
        "pending_kie_questions": None
    }]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    response = client.get("/api/v1/onboarding/questions")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    # Wait, TestClient runs background tasks synchronously after returning response
    # so analyze_context should have been called.
    assert mock_kie_service.analyze_context.call_count == 1

def test_submit_kie_answers(mock_supabase_admin, mock_kie_service):
    mock_res = MagicMock()
    mock_res.data = [{"id": "l-123"}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    # Mock the update call
    mock_update_res = MagicMock()
    mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_res

    payload = {
        "answers": [{"question_id": "q1", "answer": "Python"}]
    }
    
    response = client.post("/api/v1/onboarding/answers", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert mock_kie_service.resolve_context.call_count == 1

def test_kie_webhook_questions(mock_supabase_admin):
    mock_res = MagicMock()
    mock_res.data = [{"id": "l-123"}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    payload = {
        "user_id": "user-123",
        "questions": [
            {"question_id": "q1", "text": "Lang?", "type": "multi", "options": []}
        ]
    }
    
    # We must patch settings or provide the exact header
    from app.core.config import settings
    headers = {"X-Kie-Signature": settings.KIE_WEBHOOK_SECRET}
    
    response = client.post("/api/v1/onboarding/kie/webhook/questions", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    # Ensure update was called
    assert mock_supabase_admin.table.return_value.update.call_count == 1

def test_kie_webhook_resolved(mock_supabase_admin):
    mock_res = MagicMock()
    # Initial learner profile
    mock_res.data = [{
        "id": "l-123",
        "skills": ["Java"],
        "inferred_context": {"foo": "bar"}
    }]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    payload = {
        "user_id": "user-123",
        "new_context": {
            "primary_languages": ["Python", "Java"],
            "experience_level": "Senior",
            "tags": ["AI"]
        }
    }
    
    from app.core.config import settings
    headers = {"X-Kie-Signature": settings.KIE_WEBHOOK_SECRET}
    
    response = client.post("/api/v1/onboarding/kie/webhook/resolved", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    # Ensure update was called and we can assume the mapping logic ran correctly
    assert mock_supabase_admin.table.return_value.update.call_count == 1

def test_kie_webhook_invalid_signature():
    payload = {"user_id": "user-123", "questions": []}
    headers = {"X-Kie-Signature": "wrong-secret"}
    response = client.post("/api/v1/onboarding/kie/webhook/questions", json=payload, headers=headers)
    assert response.status_code == 401

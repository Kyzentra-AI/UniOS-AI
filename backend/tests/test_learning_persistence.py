import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_current_user
from app.schemas.learning import LearningSessionCreate, LearningSessionUpdate, Lesson, LessonBlock

client = TestClient(app)

def override_get_current_user():
    return {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}

app.dependency_overrides[get_current_user] = override_get_current_user

@patch("app.services.learning_session_service.supabase_admin")
def test_update_checkpoint_saves_lesson_data(mock_supabase):
    from app.services.learning_session_service import learning_session_service

    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": "session-1",
        "learner_id": "learner-1",
        "status": "IN_PROGRESS",
        "completed_block_ids": [],
        "lesson_id": "l-1"
    }]

    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
        "id": "session-1",
        "learner_id": "learner-1",
        "status": "IN_PROGRESS",
        "checkpoint_block_id": "b-1",
        "completed_block_ids": ["b-1"],
        "progress_percentage": 25,
        "lesson_id": "l-1",
        "lesson_data": {"id": "l-1", "title": "Test", "objective": "Obj", "blocks": []}
    }]

    sample_lesson_data = {"id": "l-1", "title": "Test", "objective": "Obj", "blocks": []}
    update_in = LearningSessionUpdate(
        checkpoint_block_id="b-1",
        completed_block_ids=["b-1"],
        progress_percentage=25,
        lesson_data=sample_lesson_data
    )

    result = learning_session_service.update_checkpoint("session-1", "learner-1", update_in)
    assert result["lesson_data"] == sample_lesson_data
    
    update_call_args = mock_supabase.table().update.call_args[0][0]
    assert update_call_args["lesson_data"] == sample_lesson_data

@patch("app.services.learning_session_service.event_service")
@patch("app.services.learning_session_service.supabase_admin")
def test_create_or_get_session_resumes_paused_session(mock_supabase, mock_event):
    from app.services.learning_session_service import learning_session_service

    # Paused session in DB
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.in_.return_value.order.return_value.execute.return_value.data = [{
        "id": "session-1",
        "learner_id": "learner-1",
        "lesson_id": "l-1",
        "status": "PAUSED",
        "checkpoint_block_id": "b-2",
        "completed_block_ids": ["b-1"],
        "progress_percentage": 50,
        "lesson_data": {"id": "l-1", "title": "Test", "objective": "Obj", "blocks": []}
    }]

    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
        "id": "session-1",
        "learner_id": "learner-1",
        "lesson_id": "l-1",
        "status": "IN_PROGRESS",
        "checkpoint_block_id": "b-2",
        "completed_block_ids": ["b-1"],
        "progress_percentage": 50,
        "lesson_data": {"id": "l-1", "title": "Test", "objective": "Obj", "blocks": []}
    }]

    session_in = LearningSessionCreate(topic="Testing", lesson_id="l-1")
    result = learning_session_service.create_or_get_session("learner-1", session_in)

    assert result["status"] == "IN_PROGRESS"
    assert result["checkpoint_block_id"] == "b-2"
    mock_event.record_event.assert_called_with("learner-1", "SESSION_RESUMED", "LESSON", "l-1")

@pytest.mark.asyncio
@patch("app.services.kie_gateway_service.learning_session_service")
async def test_generate_lesson_returns_cached_lesson_data(mock_session_service):
    from app.services.kie_gateway_service import kie_gateway_service

    cached_lesson = {
        "id": "l-1",
        "title": "Cached Lesson",
        "objective": "To test caching",
        "blocks": [
            {"id": "b-1", "type": "TEXT", "content": "Hello World"}
        ]
    }
    mock_session_service.get_session.return_value = {
        "id": "s-1",
        "learner_id": "learner-1",
        "lesson_data": cached_lesson,
        "checkpoint_block_id": "b-1"
    }

    # Should return cached lesson without making any HTTP request
    result = await kie_gateway_service.generate_lesson(
        learner_id="learner-1",
        session_id="s-1",
        request_id="req-1",
        payload={}
    )

    assert isinstance(result, Lesson)
    assert result.id == "l-1"
    assert result.title == "Cached Lesson"
    assert len(result.blocks) == 1
    assert result.blocks[0].content == "Hello World"

@patch("app.api.v1.endpoints.learning.supabase_admin")
def test_list_sessions_endpoint(mock_supabase):
    # Mock learner profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "00000000-0000-0000-0000-000000000001"}]

    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "mission_id": "00000000-0000-0000-0000-000000000003",
            "topic": "Python 101",
            "lesson_id": "py-101",
            "status": "PAUSED",
            "checkpoint_block_id": "b-2",
            "completed_block_ids": ["b-1"],
            "progress_percentage": 50,
            "lesson_data": {"id": "py-101", "title": "Py", "objective": "Obj", "blocks": []},
            "created_at": "2026-10-02T12:00:00Z",
            "updated_at": "2026-10-02T12:00:00Z"
        }
    ]

    response = client.get("/api/v1/learning/sessions?mission_id=00000000-0000-0000-0000-000000000003")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "PAUSED"
    assert data[0]["checkpoint_block_id"] == "b-2"
    assert data[0]["lesson_data"]["title"] == "Py"

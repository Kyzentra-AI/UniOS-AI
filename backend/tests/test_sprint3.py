import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
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
    with patch("app.api.v1.endpoints.syllabus.supabase_admin") as mock_syl, \
         patch("app.api.v1.endpoints.roadmaps.supabase_admin") as mock_rm, \
         patch("app.api.v1.endpoints.missions.supabase_admin") as mock_miss:
        yield mock_syl

def test_get_syllabus_not_found(mock_get_current_user, mock_supabase_admin):
    mock_supabase_admin.table().select().eq().execute.return_value.data = []
    response = client.get("/api/v1/syllabi/test-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Syllabus not found"

def test_generate_roadmap_syllabus_not_found(mock_get_current_user, mock_supabase_admin):
    # Mock learner profile found
    mock_supabase_admin.table().select().eq().execute.return_value.data = [{"id": "learner-123"}]
    # But syllabus not found
    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            # First call for learner profile
            type('obj', (object,), {'data': [{"id": "learner-123"}]}),
            # Second call for syllabus
            type('obj', (object,), {'data': []})
        ]
        
        response = client.post("/api/v1/roadmaps", json={"syllabus_id": "missing", "scope": "BOTH"})
        assert response.status_code == 404

def test_mission_start_not_found(mock_get_current_user, mock_supabase_admin):
    # Mock learner profile found
    mock_supabase_admin.table().select().eq().execute.return_value.data = [{"id": "learner-123"}]
    with patch("app.api.v1.endpoints.missions.supabase_admin.table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            type('obj', (object,), {'data': [{"id": "learner-123"}]}),
            type('obj', (object,), {'data': []}) # Mission not found
        ]
        response = client.post("/api/v1/missions/m-1/start")
        assert response.status_code == 404

def test_mission_start_already_in_progress(mock_get_current_user, mock_supabase_admin):
    sample_mission = {
        "id": "m-1",
        "roadmap_id": "rm-1",
        "title": "Build a REST API",
        "description": "API description",
        "mission_type": "LEARNING",
        "subject": "CS",
        "priority": "HIGH",
        "estimated_minutes": 60,
        "week": 1,
        "sequence": 1,
        "status": "IN_PROGRESS",
        "roadmaps": {"learner_id": "learner-123"}
    }
    with patch("app.api.v1.endpoints.missions.supabase_admin.table") as mock_table, \
         patch("app.api.v1.endpoints.missions.event_service.record_event") as mock_record_event:
        mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            type('obj', (object,), {'data': [{"id": "learner-123"}]}),
            type('obj', (object,), {'data': [sample_mission]})
        ]
        response = client.post("/api/v1/missions/m-1/start")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "m-1"
        assert data["status"] == "IN_PROGRESS"
        mock_table.return_value.update.assert_not_called()
        mock_record_event.assert_not_called()

def test_mission_start_from_pending(mock_get_current_user, mock_supabase_admin):
    sample_mission = {
        "id": "m-1",
        "roadmap_id": "rm-1",
        "title": "Build a REST API",
        "description": "API description",
        "mission_type": "LEARNING",
        "subject": "CS",
        "priority": "HIGH",
        "estimated_minutes": 60,
        "week": 1,
        "sequence": 1,
        "status": "PENDING",
        "roadmaps": {"learner_id": "learner-123"}
    }
    updated_mission = dict(sample_mission, status="IN_PROGRESS")
    with patch("app.api.v1.endpoints.missions.supabase_admin.table") as mock_table, \
         patch("app.api.v1.endpoints.missions.event_service.record_event") as mock_record_event:
        mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            type('obj', (object,), {'data': [{"id": "learner-123"}]}),
            type('obj', (object,), {'data': [sample_mission]})
        ]
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = (
            type('obj', (object,), {'data': [updated_mission]})
        )
        response = client.post("/api/v1/missions/m-1/start")
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"
        mock_table.return_value.update.assert_called_once()
        mock_record_event.assert_called_once_with("learner-123", "MISSION_STARTED", "MISSION", "m-1")

def test_mission_start_from_deferred(mock_get_current_user, mock_supabase_admin):
    sample_mission = {
        "id": "m-1",
        "roadmap_id": "rm-1",
        "title": "Build a REST API",
        "description": "API description",
        "mission_type": "LEARNING",
        "subject": "CS",
        "priority": "HIGH",
        "estimated_minutes": 60,
        "week": 1,
        "sequence": 1,
        "status": "DEFERRED",
        "roadmaps": {"learner_id": "learner-123"}
    }
    updated_mission = dict(sample_mission, status="IN_PROGRESS")
    with patch("app.api.v1.endpoints.missions.supabase_admin.table") as mock_table, \
         patch("app.api.v1.endpoints.missions.event_service.record_event") as mock_record_event:
        mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            type('obj', (object,), {'data': [{"id": "learner-123"}]}),
            type('obj', (object,), {'data': [sample_mission]})
        ]
        mock_table.return_value.update.return_value.eq.return_value.execute.return_value = (
            type('obj', (object,), {'data': [updated_mission]})
        )
        response = client.post("/api/v1/missions/m-1/start")
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"
        mock_table.return_value.update.assert_called_once()
        mock_record_event.assert_called_once_with("learner-123", "MISSION_STARTED", "MISSION", "m-1")

def test_mission_start_rejects_completed_and_skipped(mock_get_current_user, mock_supabase_admin):
    for invalid_status in ["COMPLETED", "SKIPPED"]:
        sample_mission = {
            "id": "m-1",
            "roadmap_id": "rm-1",
            "title": "Build a REST API",
            "description": "API description",
            "mission_type": "LEARNING",
            "subject": "CS",
            "priority": "HIGH",
            "estimated_minutes": 60,
            "week": 1,
            "sequence": 1,
            "status": invalid_status,
            "roadmaps": {"learner_id": "learner-123"}
        }
        with patch("app.api.v1.endpoints.missions.supabase_admin.table") as mock_table:
            mock_table.return_value.select.return_value.eq.return_value.execute.side_effect = [
                type('obj', (object,), {'data': [{"id": "learner-123"}]}),
                type('obj', (object,), {'data': [sample_mission]})
            ]
            response = client.post("/api/v1/missions/m-1/start")
            assert response.status_code == 400
            assert response.json()["detail"] == "Mission cannot be started from current state"


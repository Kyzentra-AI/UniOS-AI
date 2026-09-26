import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_get_current_user():
    # Patch across the different routers
    with patch("app.api.v1.endpoints.syllabus.get_current_user") as mock_syl, \
         patch("app.api.v1.endpoints.roadmaps.get_current_user") as mock_rm, \
         patch("app.api.v1.endpoints.missions.get_current_user") as mock_miss:
        user = {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}
        mock_syl.return_value = user
        mock_rm.return_value = user
        mock_miss.return_value = user
        yield

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

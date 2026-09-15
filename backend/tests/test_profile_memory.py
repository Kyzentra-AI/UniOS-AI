import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_current_user

client = TestClient(app)

# Helper mock user dependency
async def mock_get_current_user():
    return {
        "user_id": "test-user-123",
        "email": "student@example.com",
        "role": "user"
    }

@pytest.fixture(autouse=True)
def override_user_dep():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def mock_supabase():
    with patch("app.api.v1.endpoints.profile.supabase_admin") as mock_profile_db, \
         patch("app.api.v1.endpoints.memory.supabase_admin") as mock_memory_db:
        yield mock_profile_db, mock_memory_db


# --- PROFILE ENDPOINT TESTS ---

def test_get_profile_not_found(mock_supabase):
    mock_profile_db, _ = mock_supabase
    
    # Mock no profile found
    mock_execute = MagicMock()
    mock_execute.execute.return_value.data = []
    mock_profile_db.table.return_value.select.return_value.eq.return_value = mock_execute

    response = client.get("/api/v1/profile")
    assert response.status_code == 404
    assert "Student profile not found" in response.json()["detail"]


def test_create_profile_success(mock_supabase):
    mock_profile_db, _ = mock_supabase
    
    # Mock existing profile query (empty = insert new)
    mock_select = MagicMock()
    mock_select.execute.return_value.data = []

    # Mock insert response
    mock_insert = MagicMock()
    mock_insert.execute.return_value.data = [{
        "profile_id": "prof-123",
        "user_id": "test-user-123",
        "degree_program": "B.Tech - Computer Science",
        "academic_year": "3rd Year / Semester 5",
        "primary_language": "Hindi",
        "preferred_modes": ["Visual Diagrams", "Story Mode"],
        "primary_career_goal": "Core CS Concepts",
        "created_at": "2026-09-12T15:00:00Z",
        "updated_at": "2026-09-12T15:00:00Z"
    }]

    # Mock directives query
    mock_directives = MagicMock()
    mock_directives.execute.return_value.data = [{"directive_text": "Always use Python"}]

    def table_router(table_name):
        mock_t = MagicMock()
        if table_name == "student_profiles":
            mock_t.select.return_value.eq.return_value = mock_select
            mock_t.insert.return_value = mock_insert
            mock_t.update.return_value = mock_insert
        elif table_name == "ai_explicit_directives":
            mock_t.delete.return_value.eq.return_value = MagicMock()
            mock_t.insert.return_value = MagicMock()
            mock_t.select.return_value.eq.return_value.eq.return_value = mock_directives
        return mock_t

    mock_profile_db.table.side_effect = table_router

    payload = {
        "degree_program": "B.Tech - Computer Science",
        "academic_year": "3rd Year / Semester 5",
        "primary_language": "Hindi",
        "preferred_modes": ["Visual Diagrams", "Story Mode"],
        "primary_career_goal": "Core CS Concepts",
        "explicit_directives": ["Always use Python"]
    }

    response = client.post("/api/v1/profile", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["primary_language"] == "Hindi"
    assert res_data["explicit_directives"] == ["Always use Python"]


# --- MEMORY ENDPOINTS TESTS ---

def test_log_implicit_memory(mock_supabase):
    _, mock_memory_db = mock_supabase

    # Mock existing check (empty = insert new)
    mock_select = MagicMock()
    mock_select.execute.return_value.data = []

    mock_insert = MagicMock()
    mock_insert.execute.return_value.data = [{
        "memory_id": "mem-101",
        "user_id": "test-user-123",
        "concept": "Recursion",
        "error_frequency": 1,
        "last_observed": "2026-09-12T15:00:00Z",
        "is_archived": False
    }]

    mock_t = MagicMock()
    mock_t.select.return_value.eq.return_value.eq.return_value.eq.return_value = mock_select
    mock_t.insert.return_value = mock_insert
    mock_memory_db.table.return_value = mock_t

    payload = {
        "concept": "Recursion",
        "error_frequency_increment": 1
    }

    response = client.post("/api/v1/memory/logs", json=payload)
    assert response.status_code == 201
    assert response.json()["concept"] == "Recursion"
    assert response.json()["error_frequency"] == 1


def test_context_retrieval(mock_supabase):
    mock_profile_db, mock_memory_db = mock_supabase

    # Mock profile response
    mock_prof_t = MagicMock()
    mock_prof_t.select.return_value.eq.return_value.execute.return_value.data = [{
        "primary_language": "Hindi",
        "preferred_modes": ["Story Mode"]
    }]
    mock_profile_db.table.return_value = mock_prof_t

    # Mock memory logs & directives response
    mock_mem_t = MagicMock()
    
    def memory_router(table_name):
        mock_table = MagicMock()
        if table_name == "ai_implicit_memory_logs":
            mock_logs = MagicMock()
            mock_logs.execute.return_value.data = [
                {"concept": "Recursion", "error_frequency": 3, "last_observed": "2026-09-12T10:00:00Z"},
                {"concept": "Pointers", "error_frequency": 2, "last_observed": "2026-09-11T10:00:00Z"}
            ]
            mock_table.select.return_value.eq.return_value.eq.return_value.order.return_value = mock_logs
        elif table_name == "ai_explicit_directives":
            mock_directives = MagicMock()
            mock_directives.execute.return_value.data = [
                {"directive_text": "Always provide code examples in Python."}
            ]
            mock_table.select.return_value.eq.return_value.eq.return_value = mock_directives
        elif table_name == "student_profiles":
            mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
                "primary_language": "Hindi",
                "preferred_modes": ["Story Mode"]
            }]
        return mock_table

    mock_memory_db.table.side_effect = memory_router

    response = client.get("/api/v1/context/retrieve")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["student_id"] == "test-user-123"
    assert res_data["preferences"]["language"] == "Hindi"
    assert len(res_data["active_friction_points"]) == 2
    assert res_data["active_friction_points"][0]["concept"] == "Recursion"
    assert res_data["explicit_directives"] == ["Always provide code examples in Python."]


def test_memory_reset(mock_supabase):
    _, mock_memory_db = mock_supabase

    mock_t = MagicMock()
    mock_t.update.return_value.eq.return_value.execute.return_value.data = []
    mock_memory_db.table.return_value = mock_t

    payload = {"reset_scope": "implicit_only"}
    response = client.post("/api/v1/memory/reset", json=payload)
    assert response.status_code == 200
    assert "All implicit AI learning memory logs have been successfully reset" in response.json()["message"]

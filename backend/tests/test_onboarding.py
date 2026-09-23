import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.schemas.onboarding import OnboardingCompleteValidator, AcademicStatus, DailyStudyHours, LearningDepth
from app.core.kie_assembler import LearnerContextAssembler

client = TestClient(app)

# --- MOCKS ---

@pytest.fixture
def mock_get_current_user():
    # We patch the dependency in FastAPI
    with patch("app.api.v1.endpoints.onboarding.get_current_user") as mock:
        mock.return_value = {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}
        yield mock

@pytest.fixture
def mock_supabase_admin():
    with patch("app.api.v1.endpoints.onboarding.supabase_admin") as mock:
        yield mock

# --- KIE CONTEXT ASSEMBLER TESTS ---

def test_kie_context_assembler():
    learner = {
        "id": "l-123", "user_id": "user-123", "primary_goal": "Learn AI",
        "target_skills": ["Python"], "skills": ["Java"], "projects": [],
        "research": None, "experience": "1 yr", "onboarding_status": "IN_PROGRESS"
    }
    academic = {
        "academic_status": "BACHELOR", "university": "MIT", "degree_program": "CS",
        "domain": "Tech", "current_year": "Year 2", "graduation_year": None, "subjects": ["Math"]
    }
    prefs = {
        "daily_study_hours": "2_3", "learning_depth": "DEEP"
    }
    
    context = LearnerContextAssembler.assemble(learner, academic, prefs)
    
    assert context["learner_id"] == "l-123"
    assert context["education"]["academic_status"] == "BACHELOR"
    assert context["career"]["target_skills"] == ["Python"]
    assert context["preferences"]["learning_depth"] == "DEEP"

def test_kie_context_assembler_missing_data():
    context = LearnerContextAssembler.assemble({}, {}, {})
    assert context["learner_id"] is None
    assert context["education"] == {}
    assert context["career"]["target_skills"] == []
    assert context["preferences"] == {}

# --- VALIDATION SCHEMAS TESTS ---

def test_onboarding_complete_validator_bachelor_valid():
    data = {
        "primary_goal": "Job",
        "target_skills": [],
        "skills": [],
        "projects": [],
        "academic_status": AcademicStatus.BACHELOR,
        "university": "Stanford",
        "degree_program": "CS",
        "domain": "Tech",
        "current_year": "Senior",
        "graduation_year": None,
        "subjects": [],
        "daily_study_hours": DailyStudyHours.HOURS_2_3,
        "learning_depth": LearningDepth.BALANCED
    }
    v = OnboardingCompleteValidator(**data)
    assert v.academic_status == AcademicStatus.BACHELOR

def test_onboarding_complete_validator_bachelor_invalid():
    data = {
        "primary_goal": "Job",
        "target_skills": [],
        "skills": [],
        "projects": [],
        "academic_status": AcademicStatus.BACHELOR,
        "university": None, # Invalid
        "degree_program": "CS",
        "domain": "Tech",
        "current_year": "Senior",
        "graduation_year": 2024, # Invalid
        "subjects": [],
        "daily_study_hours": DailyStudyHours.HOURS_2_3,
        "learning_depth": LearningDepth.BALANCED
    }
    with pytest.raises(ValueError):
        OnboardingCompleteValidator(**data)

def test_onboarding_complete_validator_recent_grad_valid():
    data = {
        "primary_goal": "Job",
        "target_skills": [],
        "skills": [],
        "projects": [],
        "academic_status": AcademicStatus.RECENT_GRADUATE,
        "university": None,
        "degree_program": "CS",
        "domain": "Tech",
        "current_year": None,
        "graduation_year": 2023,
        "subjects": [],
        "daily_study_hours": DailyStudyHours.HOURS_2_3,
        "learning_depth": LearningDepth.BALANCED
    }
    v = OnboardingCompleteValidator(**data)
    assert v.graduation_year == 2023

# --- API ENDPOINTS TESTS ---
# Note: we need to override the dependency in the app for testing
from app.core.deps import get_current_user

def override_get_current_user():
    return {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_init_onboarding(mock_supabase_admin):
    # Mock that learner does not exist
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
    
    # Mock insert response
    mock_insert_response = MagicMock()
    mock_insert_response.data = [{"id": "l-123"}]
    mock_supabase_admin.table.return_value.insert.return_value.execute.return_value = mock_insert_response
    
    payload = {
        "learner_profile": {"primary_goal": "Goal"},
        "academic_profile": {"academic_status": "BACHELOR"},
        "learning_preferences": {"learning_depth": "QUICK"}
    }
    
    response = client.post("/api/v1/onboarding", json=payload)
    assert response.status_code == 200
    assert mock_supabase_admin.table.return_value.insert.call_count == 3

def test_patch_onboarding(mock_supabase_admin):
    # Mock that learner exists
    mock_learner_res = MagicMock()
    mock_learner_res.data = [{"id": "l-123"}]
    
    # We have to mock the chained calls .table().select().eq().execute()
    # It's tricky to mock all chained calls identically for different tables, so we just check if it runs without 500
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_learner_res
    mock_supabase_admin.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_learner_res
    
    payload = {
        "learner_profile": {"skills": ["Python", "C++"]}
    }
    
    response = client.patch("/api/v1/onboarding", json=payload)
    assert response.status_code == 200
    
def test_complete_onboarding_missing_fields(mock_supabase_admin):
    # Mock learner exists but incomplete
    mock_res = MagicMock()
    mock_res.data = [{
        "id": "l-123",
        "onboarding_status": "IN_PROGRESS"
    }]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_res
    
    response = client.post("/api/v1/onboarding/complete")
    # Should fail due to missing fields in DB mockup
    assert response.status_code == 400


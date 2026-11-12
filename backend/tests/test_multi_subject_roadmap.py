import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.deps import get_current_user
from app.schemas.roadmap import (
    RoadmapRequest,
    RoadmapScope,
    AIMLRoadmapResponse,
    RoadmapMission,
    MissionType,
    SubjectTrack
)
from app.services.roadmap_service import roadmap_service
from app.core.context_v2_assembler import ContextV2Assembler

client = TestClient(app)

@pytest.fixture
def mock_user():
    user = {"user_id": "user-123", "email": "test@test.com", "role": "user", "payload": {}}
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()

# -----------------------------------------------------------------------------
# 1. Test POST /api/v1/roadmaps
# -----------------------------------------------------------------------------
def test_post_roadmap_with_subject(mock_user):
    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table, \
         patch.object(roadmap_service, "generate_roadmap_background", new_callable=AsyncMock) as mock_bg:
        
        # Mock learner
        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-123"}]
        
        # Mock syllabus
        syl_mock = MagicMock()
        syl_mock.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "syl-123",
            "learner_id": "learner-123",
            "status": "CONFIRMED"
        }]
        
        def table_router(table_name):
            if table_name == "learner_profiles":
                return learner_mock
            elif table_name == "syllabus_documents":
                return syl_mock
            return MagicMock()

        mock_table.side_effect = table_router
        
        response = client.post("/api/v1/roadmaps", json={
            "syllabus_id": "syl-123",
            "scope": "ACADEMIC",
            "subject": "Operating Systems"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Roadmap generation started"
        assert data["status"] == "PROCESSING"
        assert data["subject"] == "Operating Systems"
        mock_bg.assert_called_once_with("learner-123", "ACADEMIC", "syl-123", "Operating Systems")


def test_post_roadmap_without_subject(mock_user):
    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table, \
         patch.object(roadmap_service, "generate_roadmap_background", new_callable=AsyncMock) as mock_bg:

        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-123"}]
        
        syl_mock = MagicMock()
        syl_mock.select.return_value.eq.return_value.execute.return_value.data = [{
            "id": "syl-123",
            "learner_id": "learner-123",
            "status": "CONFIRMED"
        }]
        
        def table_router(table_name):
            if table_name == "learner_profiles":
                return learner_mock
            elif table_name == "syllabus_documents":
                return syl_mock
            return MagicMock()

        mock_table.side_effect = table_router
        
        response = client.post("/api/v1/roadmaps", json={
            "syllabus_id": "syl-123",
            "scope": "BOTH"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROCESSING"
        assert data["subject"] == "ALL"
        mock_bg.assert_called_once_with("learner-123", "BOTH", "syl-123", None)

# -----------------------------------------------------------------------------
# 2. Test GET /api/v1/roadmaps/current
# -----------------------------------------------------------------------------
def test_get_current_roadmap_empty(mock_user):
    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table:
        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-123"}]
        
        rm_mock = MagicMock()
        rm_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        
        def table_router(table_name):
            if table_name == "learner_profiles":
                return learner_mock
            return rm_mock

        mock_table.side_effect = table_router
        
        response = client.get("/api/v1/roadmaps/current")
        assert response.status_code == 200
        data = response.json()
        assert data["roadmap"] is None
        assert data["available_subjects"] == []
        assert data["active_subject"] == "ALL"


def test_get_current_roadmap_master_and_tabs(mock_user):
    master_rm = {
        "id": "rm-master",
        "version": 1,
        "scope": "ACADEMIC",
        "subject": None,
        "status": "ACTIVE",
        "plan_data": {"goals": ["Master all subjects"]},
        "created_at": "2026-11-01T00:00:00Z",
        "updated_at": "2026-11-01T00:00:00Z"
    }
    missions = [
        {"id": "m1", "roadmap_id": "rm-master", "title": "OS Mission 1", "subject": "Operating Systems", "status": "COMPLETED", "sequence": 1},
        {"id": "m2", "roadmap_id": "rm-master", "title": "OS Mission 2", "subject": "Operating Systems", "status": "PENDING", "sequence": 2},
        {"id": "m3", "roadmap_id": "rm-master", "title": "DBMS Mission 1", "subject": "DBMS", "status": "IN_PROGRESS", "sequence": 3},
    ]

    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table:
        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-123"}]
        
        rm_mock = MagicMock()
        rm_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [master_rm]
        
        miss_mock = MagicMock()
        miss_mock.select.return_value.eq.return_value.order.return_value.execute.return_value.data = missions

        def table_router(table_name):
            if table_name == "learner_profiles":
                return learner_mock
            elif table_name == "roadmaps":
                return rm_mock
            elif table_name == "missions":
                return miss_mock
            return MagicMock()

        mock_table.side_effect = table_router
        
        response = client.get("/api/v1/roadmaps/current")
        assert response.status_code == 200
        data = response.json()
        assert data["roadmap"]["id"] == "rm-master"
        assert len(data["roadmap"]["missions"]) == 3
        assert data["active_subject"] == "ALL"
        
        # Verify available_subjects contains both OS and DBMS
        subjs = {s["name"]: s for s in data["available_subjects"]}
        assert "Operating Systems" in subjs
        assert subjs["Operating Systems"]["total_missions"] == 2
        assert subjs["Operating Systems"]["completed_missions"] == 1
        assert subjs["Operating Systems"]["progress_percentage"] == 50
        assert "DBMS" in subjs
        assert subjs["DBMS"]["in_progress_missions"] == 1


def test_get_current_roadmap_filter_subject_and_fallback(mock_user):
    master_rm = {
        "id": "rm-master",
        "version": 1,
        "scope": "ACADEMIC",
        "subject": None,
        "status": "ACTIVE",
        "plan_data": {},
        "created_at": "2026-11-01T00:00:00Z",
        "updated_at": "2026-11-01T00:00:00Z"
    }
    missions = [
        {"id": "m1", "roadmap_id": "rm-master", "title": "OS Mission 1", "subject": "Operating Systems", "status": "COMPLETED", "sequence": 1},
        {"id": "m2", "roadmap_id": "rm-master", "title": "DBMS Mission 1", "subject": "DBMS", "status": "PENDING", "sequence": 2},
    ]

    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table:
        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-123"}]
        
        rm_mock = MagicMock()
        rm_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [master_rm]
        
        miss_mock = MagicMock()
        miss_mock.select.return_value.eq.return_value.order.return_value.execute.return_value.data = missions

        def table_router(table_name):
            if table_name == "learner_profiles":
                return learner_mock
            elif table_name == "roadmaps":
                return rm_mock
            elif table_name == "missions":
                return miss_mock
            return MagicMock()

        mock_table.side_effect = table_router
        
        # Filter for Operating Systems (case-insensitive test)
        response = client.get("/api/v1/roadmaps/current?subject=operating%20systems")
        assert response.status_code == 200
        data = response.json()
        assert data["active_subject"] == "operating systems"
        # Only OS mission should be displayed
        assert len(data["roadmap"]["missions"]) == 1
        assert data["roadmap"]["missions"][0]["subject"] == "Operating Systems"


# -----------------------------------------------------------------------------
# 3. Test RoadmapService Background Worker
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_roadmap_service_generate_with_subject():
    kie_response = {
        "scope": "ACADEMIC",
        "target_subject": "Operating Systems",
        "subject_tracks": [
            {
                "subject_name": "Operating Systems",
                "mission_count": 2,
                "estimated_total_minutes": 180,
                "core_topics": ["Process Scheduling", "Virtual Memory"]
            }
        ],
        "goals": ["Master OS"],
        "milestones": ["Week 1: Scheduling"],
        "missions": [
            {
                "title": "Study Schedulers",
                "type": "LEARNING",
                "description": "Understand round robin",
                "priority": "HIGH",
                "estimated_minutes": 90,
                "subject": "Operating Systems",
                "week": 1,
                "sequence": 1
            }
        ]
    }

    with patch("app.services.roadmap_service.ContextV2Assembler.assemble", new_callable=AsyncMock) as mock_assemble, \
         patch("app.services.roadmap_service.kie_service.generate_roadmap", new_callable=AsyncMock) as mock_kie, \
         patch("app.services.roadmap_service.supabase_admin.table") as mock_table, \
         patch("app.services.roadmap_service.event_service.record_event") as mock_record:

        mock_assemble.return_value = {"learner_id": "l-1", "target_subject": "Operating Systems"}
        mock_kie.return_value = kie_response

        # Mock table calls for deactivation, version query, insert roadmap, insert missions
        rm_mock = MagicMock()
        rm_mock.update.return_value.eq.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        rm_mock.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        rm_mock.insert.return_value.execute.return_value.data = [{"id": "rm-new-123"}]

        miss_mock = MagicMock()
        miss_mock.insert.return_value.execute.return_value.data = [{"id": "m-new-1"}]

        def table_router(table_name):
            if table_name == "roadmaps":
                return rm_mock
            elif table_name == "missions":
                return miss_mock
            return MagicMock()

        mock_table.side_effect = table_router

        await roadmap_service.generate_roadmap_background("l-1", "ACADEMIC", "syl-1", target_subject="Operating Systems")

        mock_assemble.assert_called_once_with("l-1", "ACADEMIC", "syl-1", target_subject="Operating Systems")
        mock_kie.assert_called_once()
        mock_record.assert_called_once_with(
            learner_id="l-1",
            event_type="ROADMAP_CREATED",
            entity_type="ROADMAP",
            entity_id="rm-new-123"
        )

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.deps import get_current_user
from app.schemas.learning import ContentReferenceQuery
from app.services.content_reference_service import ContentReferenceService
from app.services.kie_gateway_service import KIEGatewayService
from app.services.learning_session_service import LearningSessionService
from app.services.roadmap_service import RoadmapService


@pytest.fixture
def auth_client():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": "user-bba-1"}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_per_subject_roadmap_orchestration_coverage_and_ordering():
    parsed_syllabus = {
        "subjects": [
            {
                "name": "Principles of Management",
                "topics": ["Nature of Management", "PODC Framework", "Delegation of Authority"],
            },
            {
                "name": "Financial Accounting",
                "topics": ["Double Entry System", "Trial Balance"],
            },
        ]
    }

    async def fake_assemble(learner_id, scope=None, syllabus_id=None, target_subject=None):
        return {
            "learner_id": learner_id,
            "scope": scope,
            "target_subject": target_subject,
            "education": {"degree_program": "BBA", "domain": "Management"},
            "syllabus": parsed_syllabus,
        }

    async def fake_generate_roadmap(ctx):
        subj = ctx.get("target_subject")
        if subj == "Principles of Management":
            return {
                "scope": "ACADEMIC",
                "target_subject": subj,
                "subject_tracks": [{"subject_name": subj, "mission_count": 1, "estimated_total_minutes": 60, "core_topics": ["Nature of Management"]}],
                "missions": [
                    {
                        "title": "Nature of Management",
                        "type": "LEARNING",
                        "description": "Objectives: Understand management.\nCore Concepts: Scope.",
                        "subject": subj,
                        "topic": "Nature of Management",
                        "objectives": "Understand management.",
                        "core_concepts": "Scope and functions.",
                        "deliverables": "Summary notes.",
                        "mastery_criteria": "Explain PODC.",
                        "week": 2,
                        "sequence": 1,
                    }
                ],
            }
        return {
            "scope": "ACADEMIC",
            "target_subject": subj,
            "subject_tracks": [{"subject_name": subj, "mission_count": 1, "estimated_total_minutes": 60, "core_topics": ["Double Entry System"]}],
            "missions": [
                {
                    "title": "Double Entry System",
                    "type": "LEARNING",
                    "description": "Learn debit and credit rules.",
                    "subject": subj,
                    "topic": "Double Entry System",
                    "week": 1,
                    "sequence": 1,
                }
            ],
        }

    inserted_missions = []

    def table_router(name):
        tbl = MagicMock()
        if name == "syllabus_documents":
            tbl.select.return_value.eq.return_value.execute.return_value.data = [{"parsed_content": parsed_syllabus}]
        elif name == "roadmaps":
            tbl.select.return_value.eq.return_value.eq.return_value.is_.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            tbl.insert.return_value.execute.return_value.data = [{"id": "rm-bba-1"}]
        elif name == "missions":
            def capture_insert(rows):
                inserted_missions.extend(rows)
                m = MagicMock()
                m.execute.return_value.data = rows
                return m
            tbl.insert.side_effect = capture_insert
        return tbl

    with patch("app.services.roadmap_service.supabase_admin.table", side_effect=table_router), \
         patch("app.services.roadmap_service.ContextV2Assembler.assemble", side_effect=fake_assemble), \
         patch("app.services.roadmap_service.kie_service.generate_roadmap", side_effect=fake_generate_roadmap), \
         patch("app.services.roadmap_service.event_service.record_event"):
        await RoadmapService.generate_roadmap_background("learner-1", "ACADEMIC", "syl-1", target_subject=None)

    # All 5 syllabus topics across both subjects must be covered (2 returned + 3 added by coverage gate)
    assert len(inserted_missions) == 5
    sequences = [m["sequence"] for m in inserted_missions]
    assert sequences == [1, 2, 3, 4, 5]
    # Structured metadata preserved on KIE-generated mission
    pom_first = next(m for m in inserted_missions if m["title"] == "Nature of Management")
    assert pom_first["objectives"] == "Understand management."
    assert pom_first["core_concepts"] == "Scope and functions."


def test_get_current_roadmap_sorts_by_week_then_sequence(auth_client):
    master_rm = {
        "id": "rm-1",
        "version": 1,
        "scope": "ACADEMIC",
        "subject": None,
        "status": "ACTIVE",
        "plan_data": {},
    }
    unsorted_missions = [
        {"id": "m3", "roadmap_id": "rm-1", "title": "Week 3", "subject": "BBA", "status": "PENDING", "week": 3, "sequence": 1},
        {"id": "m1", "roadmap_id": "rm-1", "title": "Week 1", "subject": "BBA", "status": "PENDING", "week": 1, "sequence": 1},
        {"id": "m2", "roadmap_id": "rm-1", "title": "Week 2", "subject": "BBA", "status": "PENDING", "week": 2, "sequence": 2},
    ]

    with patch("app.api.v1.endpoints.roadmaps.supabase_admin.table") as mock_table:
        learner_mock = MagicMock()
        learner_mock.select.return_value.eq.return_value.execute.return_value.data = [{"id": "learner-1"}]
        rm_mock = MagicMock()
        rm_mock.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [master_rm]
        miss_mock = MagicMock()
        miss_mock.select.return_value.eq.return_value.order.return_value.execute.return_value.data = unsorted_missions

        def router(t):
            return {"learner_profiles": learner_mock, "roadmaps": rm_mock, "missions": miss_mock}.get(t, MagicMock())

        mock_table.side_effect = router
        resp = auth_client.get("/api/v1/roadmaps/current")
        assert resp.status_code == 200
        ids = [m["id"] for m in resp.json()["roadmap"]["missions"]]
        assert ids == ["m1", "m2", "m3"]


def test_content_reference_service_extracts_nested_subjects():
    parsed = {
        "subjects": [
            {
                "name": "Principles of Management",
                "chapters": [{"title": "Unit 1: Planning", "topics": ["Nature of Planning", "MBO"]}],
                "topics": ["PODC Framework"],
            }
        ]
    }
    with patch("app.services.content_reference_service.supabase_admin.table") as mock_table:
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"parsed_content": parsed}]
        res = ContentReferenceService.get_references(
            ContentReferenceQuery(syllabus_id="00000000-0000-0000-0000-000000000001", topic="PODC Framework")
        )
        assert len(res.references) >= 1
        assert "Principles of Management" in res.references[0]["content"]


@pytest.mark.asyncio
async def test_generate_lesson_non_cs_guard_retries_and_preserves_mermaid():
    session_row = {
        "id": "sess-1",
        "learner_id": "learner-1",
        "topic": "PODC Framework",
        "lesson_id": "podc-1",
        "subject": "Principles of Management",
        "syllabus_id": "00000000-0000-0000-0000-000000000001",
        "lesson_data": None,
        "checkpoint_block_id": None,
        "progress_percentage": 0,
    }
    leaked_cs_lesson = {
        "id": "podc-1",
        "title": "PODC",
        "objective": "Learn PODC",
        "blocks": [
            {"id": "b1", "type": "CODE", "title": "Python Class", "code": "class PODC: pass", "language": "python"}
        ],
    }
    clean_bba_lesson = {
        "id": "podc-1",
        "title": "PODC Framework",
        "objective": "Master Planning, Organizing, Directing, and Controlling",
        "blocks": [
            {
                "id": "b1",
                "type": "TEXT",
                "title": "Visual Framework & Mental Model",
                "content": "```mermaid\nflowchart TD\n  P[Planning] --> O[Organizing]\n```",
            }
        ],
    }

    call_payloads = []

    async def fake_request(client, url, payload, max_retries=3):
        call_payloads.append((url, payload))
        if url.endswith("/interpret"):
            return {"strategy": "case_study"}
        if len([p for u, p in call_payloads if u.endswith("/lesson/generate")]) == 1:
            return leaked_cs_lesson
        return clean_bba_lesson

    with patch("app.services.kie_gateway_service.learning_session_service.get_session", return_value=session_row), \
         patch("app.services.kie_gateway_service.ContextV2Assembler.assemble", new=AsyncMock(return_value={
             "education": {"degree_program": "BBA", "domain": "Business Management"},
             "syllabus": {},
         })), \
         patch("app.services.kie_gateway_service.content_reference_service.get_references") as mock_refs, \
         patch("app.services.kie_gateway_service.KIEGatewayService._request_with_retry", side_effect=fake_request), \
         patch("app.services.kie_gateway_service.learning_session_service.update_checkpoint") as mock_ckpt:
        mock_refs.return_value.references = [{"subject": "Principles of Management", "content": "PODC"}]
        lesson = await KIEGatewayService.generate_lesson("learner-1", "sess-1", "req-1", {})

    gen_calls = [p for u, p in call_payloads if u.endswith("/lesson/generate")]
    assert len(gen_calls) == 2
    assert gen_calls[0]["subject"] == "Principles of Management"
    assert gen_calls[0]["degree_program"] == "BBA"
    assert gen_calls[1]["strict_domain_constraints"] is True
    assert "```mermaid\nflowchart TD\n" in lesson.blocks[0].content
    mock_ckpt.assert_called_once()


def test_complete_session_returns_assessment_handoff():
    existing_session = {
        "id": "00000000-0000-0000-0000-000000000010",
        "learner_id": "00000000-0000-0000-0000-000000000001",
        "mission_id": "00000000-0000-0000-0000-000000000020",
        "topic": "PODC Framework",
        "lesson_id": "podc-1",
        "subject": None,
        "status": "IN_PROGRESS",
        "progress_percentage": 80,
        "lesson_data": {"id": "podc-1", "title": "PODC", "objective": "Obj", "blocks": [{"id": "b1", "type": "TEXT", "content": "5 sections only"}]},
        "created_at": "2026-11-25T10:00:00Z",
        "updated_at": "2026-11-25T10:00:00Z",
    }

    with patch("app.services.learning_session_service.supabase_admin.table") as mock_table, \
         patch("app.services.learning_session_service.event_service.record_event"):
        ls_tbl = MagicMock()
        ls_tbl.select.return_value.eq.return_value.execute.return_value.data = [existing_session]
        ls_tbl.update.return_value.eq.return_value.execute.return_value.data = [
            {**existing_session, "status": "COMPLETED", "progress_percentage": 100}
        ]
        m_tbl = MagicMock()
        m_tbl.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
            {"subject": "Principles of Management"}
        ]
        mock_table.side_effect = lambda name: ls_tbl if name == "learning_sessions" else m_tbl

        completed = LearningSessionService.complete_session(existing_session["id"], existing_session["learner_id"])
        assert completed["status"] == "COMPLETED"
        assert completed["progress_percentage"] == 100
        assert completed["next_step"] == "ASSESSMENT"
        assert completed["assessment_context"] == {
            "session_id": existing_session["id"],
            "topic": "PODC Framework",
            "subject": "Principles of Management",
        }


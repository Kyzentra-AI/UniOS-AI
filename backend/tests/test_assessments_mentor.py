"""
Unit and Integration Tests for Assessments Generation, Attempts, and Mentor Chat.
Verifies:
- POST /api/v1/assessments/generate returns unwrapped Assessment object with stable IDs.
- Secret answer keys are never leaked to client.
- POST /api/v1/assessments/attempts evaluates answers and records attempt.
- POST /api/v1/mentor/chat handles conversation creation, continuation, and persona modes.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.deps import get_current_user
from app.main import app

client = TestClient(app)

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_LEARNER_ID = "00000000-0000-0000-0000-000000000002"
TEST_SESSION_ID = "00000000-0000-0000-0000-000000000010"


@pytest.fixture
def mock_get_current_user():
    prev = app.dependency_overrides.get(get_current_user)
    user = {
        "user_id": TEST_USER_ID,
        "email": "student@unios.ai",
        "role": "learner",
        "payload": {},
    }
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    if prev is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = prev


# ==============================================================================
# 1. Assessment Generation Tests
# ==============================================================================

def test_generate_assessment_unwrapped_structure(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        # 1. Mock learning session found
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID, "topic": "DBMS Fundamentals"}]
        )

        # 2. Mock no existing assessment found
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )

        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

        payload = {
            "session_id": TEST_SESSION_ID,
            "topic": "DBMS Fundamentals",
        }

        response = client.post("/api/v1/assessments/generate", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Must be unwrapped Assessment object
        assert "id" in data
        assert "title" in data
        assert "type" in data
        assert "questions" in data
        assert "data" not in data  # Assert not wrapped in data or result object
        assert "result" not in data

        # Check questions format
        questions = data["questions"]
        assert len(questions) > 0
        q1 = questions[0]
        assert "id" in q1
        assert "type" in q1
        assert "question" in q1
        assert "options" in q1
        assert len(q1["options"]) > 0

        # Verify correct_option_id / answer_keys is NEVER leaked to the client
        assert "correct_option_id" not in q1
        assert "answer_keys" not in data
        assert "correctOptionId" not in q1


def test_generate_assessment_stable_persistence(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        # Existing persisted assessment in DB
        persisted_asmt = {
            "id": "assessment-stable-123",
            "session_id": TEST_SESSION_ID,
            "learner_id": TEST_LEARNER_ID,
            "topic": "DBMS Fundamentals",
            "title": "DBMS Fundamentals Assessment",
            "type": "mcq",
            "instructions": "Answer all questions.",
            "questions": [
                {
                    "id": "question-1",
                    "type": "mcq",
                    "question": "Which component manages a database?",
                    "options": [
                        {"id": "option-1", "text": "DBMS"},
                        {"id": "option-2", "text": "Compiler"},
                    ],
                    "correct_option_id": "option-1",
                }
            ],
            "answer_keys": {"question-1": "option-1"},
        }

        def table_router(table_name):
            t = MagicMock()
            if table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            elif table_name == "assessments":
                t.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[persisted_asmt]
                )
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "topic": "DBMS Fundamentals",
        }

        response = client.post("/api/v1/assessments/generate", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "assessment-stable-123"
        assert data["title"] == "DBMS Fundamentals Assessment"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["id"] == "question-1"
        assert "correct_option_id" not in data["questions"][0]


# ==============================================================================
# 2. Assessment Attempt Submission Tests
# ==============================================================================

def test_submit_assessment_attempt(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        # Mock assessment lookup with answer key
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "assessment-123",
                "session_id": TEST_SESSION_ID,
                "topic": "DBMS Fundamentals",
                "questions": [{"id": "question-1", "type": "mcq"}],
                "answer_keys": {"question-1": "option-1"},
            }]
        )

        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "attempt-123",
                "session_id": TEST_SESSION_ID,
                "learner_id": TEST_LEARNER_ID,
                "assessment_id": "assessment-123",
                "topic": "DBMS Fundamentals",
                "answers": [{"question_id": "question-1", "answer": "option-1", "hints_used": 0, "time_spent_seconds": 25}],
                "score": 1.0,
                "total_time_spent_seconds": 25,
                "hints_used_count": 0,
                "is_completed": True,
                "mastery_updates": {},
                "feedback": "Good work.",
                "created_at": "2026-10-26T05:00:00Z",
            }]
        )
        mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[{}])

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [
                {
                    "question_id": "question-1",
                    "answer": "option-1",
                    "hints_used": 0,
                    "time_spent_seconds": 25,
                }
            ],
            "total_time_spent_seconds": 25,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "attempt-123"
        assert data["score"] == 1.0
        assert data["is_completed"] is True
        assert data["hints_used_count"] == 0
        assert "feedback" in data


# ==============================================================================
# 3. Mentor Chat Tests
# ==============================================================================

def test_mentor_chat_new_conversation(mock_get_current_user):
    with patch("app.api.v1.endpoints.mentor._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.mentor.mentor_service.supabase_admin") as mock_db, \
         patch("app.services.mentor.mentor_service.billing_service.get_or_create_usage") as mock_usage:

        # Mock usage quota
        mock_usage.return_value.quotas = {
            "aiTutorRequests": MagicMock(remaining=10)
        }

        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"ai_tutor_requests": 2}]
        )
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])

        payload = {
            "mode": "tutor",
            "message": "Explain DBMS in simple words",
            "context": {
                "topic": "DBMS Fundamentals",
                "lessonId": "lesson-123",
                "roadmapId": "roadmap-123",
                "missionId": "mission-123",
            },
            "history": [
                {"role": "user", "content": "What is a database?"},
                {"role": "mentor", "content": "A database is an organized collection of data."},
            ],
            "conversationId": None,
        }

        response = client.post("/api/v1/mentor/chat", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 0
        assert "conversationId" in data
        assert data["conversationId"].startswith("conversation_")
        assert "createdAt" in data


def test_mentor_chat_continue_conversation(mock_get_current_user):
    with patch("app.api.v1.endpoints.mentor._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.mentor.mentor_service.supabase_admin") as mock_db:

        existing_conv_id = "conversation-123"

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": existing_conv_id, "learner_id": TEST_LEARNER_ID}]
        )
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])
        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{}])

        payload = {
            "mode": "study-coach",
            "message": "How should I structure my revision?",
            "context": {"topic": "DBMS Fundamentals"},
            "history": [],
            "conversationId": existing_conv_id,
        }

        response = client.post("/api/v1/mentor/chat", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversationId"] == existing_conv_id
        assert "reply" in data


# ==============================================================================
# 4. Assessment Robustness & Edge Cases Tests
# ==============================================================================

def test_generate_assessment_persistence_failure_raises_500(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID, "topic": "DBMS Fundamentals"}]
        )
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        mock_db.table.return_value.insert.return_value.execute.side_effect = Exception("DB Connection Timeout")

        payload = {
            "session_id": TEST_SESSION_ID,
            "topic": "DBMS Fundamentals",
        }

        response = client.post("/api/v1/assessments/generate", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to persist assessment" in response.json()["detail"]


def test_submit_assessment_attempt_duplicate_question_ids(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [
                {"question_id": "question-1", "answer": "option-1"},
                {"question_id": "question-1", "answer": "option-2"},
            ],
            "total_time_spent_seconds": 30,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Duplicate question IDs" in response.json()["detail"]


def test_submit_assessment_attempt_invalid_question_id(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-123",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [{"id": "question-1", "type": "mcq"}],
                        "answer_keys": {"question-1": "option-1"},
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [
                {"question_id": "non-existent-question", "answer": "option-1"}
            ],
            "total_time_spent_seconds": 30,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid question ID" in response.json()["detail"]


def test_submit_assessment_attempt_invalid_mcq_option(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-123",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [{
                            "id": "question-1",
                            "type": "mcq",
                            "options": [
                                {"id": "option-1", "text": "DBMS"},
                                {"id": "option-2", "text": "Compiler"},
                            ]
                        }],
                        "answer_keys": {"question-1": "option-1"},
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [
                {"question_id": "question-1", "answer": "option-invalid-999"}
            ],
            "total_time_spent_seconds": 30,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid option" in response.json()["detail"]


def test_submit_assessment_attempt_foreign_assessment_ownership(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{
                "id": "assessment-123",
                "learner_id": "different-learner-uuid",
                "session_id": TEST_SESSION_ID,
                "topic": "DBMS Fundamentals",
                "questions": [{"id": "question-1", "type": "mcq"}],
            }]
        )

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [{"question_id": "question-1", "answer": "option-1"}],
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Assessment does not belong to the authenticated learner" in response.json()["detail"]


def test_submit_assessment_attempt_foreign_session_ownership(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-123",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [{"id": "question-1", "type": "mcq"}],
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": "different-learner-uuid"}]
                )
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [{"question_id": "question-1", "answer": "option-1"}],
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Learning session does not belong to the authenticated learner" in response.json()["detail"]


def test_submit_assessment_attempt_persistence_failure_raises_500(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db:

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-123",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [{"id": "question-1", "type": "mcq"}],
                        "answer_keys": {"question-1": "option-1"},
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            elif table_name == "assessment_attempts":
                t.insert.return_value.execute.side_effect = Exception("DB Disk Full")
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "answers": [{"question_id": "question-1", "answer": "option-1"}],
            "total_time_spent_seconds": 25,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to persist assessment attempt" in response.json()["detail"]


def test_submit_assessment_attempt_kie_zero_score_not_converted_to_one(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db, \
         patch("app.services.assessment_service.AssessmentService._evaluate_with_kie") as mock_kie:

        mock_kie.return_value = (0.0, {"Computer Science": {"DBMS": {"score": 0.0, "status": "NOVICE"}}}, "Needs improvement.", True)

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-subj-1",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [{"id": "q-subj-1", "type": "subjective"}],
                        "answer_keys": {},
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            elif table_name == "assessment_attempts":
                t.insert.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "attempt-zero-1",
                        "learner_id": TEST_LEARNER_ID,
                        "score": 0.0,
                        "is_completed": True,
                    }]
                )
            elif table_name == "learner_mastery":
                t.upsert.return_value.execute.return_value = MagicMock(data=[{}])
            return t

        mock_db.table.side_effect = table_router

        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-subj-1",
            "topic": "DBMS Fundamentals",
            "answers": [{"question_id": "q-subj-1", "answer": "completely incorrect answer"}],
            "total_time_spent_seconds": 40,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == 0.0  # Must NOT be 1.0!


def test_submit_assessment_attempt_incomplete_scoring_denominator(mock_get_current_user):
    with patch("app.api.v1.endpoints.assessments._get_learner_id", return_value=TEST_LEARNER_ID), \
         patch("app.services.assessment_service.supabase_admin") as mock_db, \
         patch("app.services.assessment_service.AssessmentService._evaluate_with_kie") as mock_kie:

        mock_kie.return_value = (None, {}, None, False)

        def table_router(table_name):
            t = MagicMock()
            if table_name == "assessments":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "assessment-multi-q",
                        "learner_id": TEST_LEARNER_ID,
                        "session_id": TEST_SESSION_ID,
                        "topic": "DBMS Fundamentals",
                        "questions": [
                            {"id": "q1", "type": "mcq"},
                            {"id": "q2", "type": "mcq"},
                        ],
                        "answer_keys": {"q1": "option-1", "q2": "option-2"},
                    }]
                )
            elif table_name == "learning_sessions":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": TEST_SESSION_ID, "learner_id": TEST_LEARNER_ID}]
                )
            elif table_name == "assessment_attempts":
                t.insert.return_value.execute.return_value = MagicMock(
                    data=[{
                        "id": "attempt-half-1",
                        "learner_id": TEST_LEARNER_ID,
                        "score": 0.5,
                        "is_completed": True,
                    }]
                )
            return t

        mock_db.table.side_effect = table_router

        # Learner submits only 1 correct answer out of 2 total questions
        payload = {
            "session_id": TEST_SESSION_ID,
            "assessment_id": "assessment-multi-q",
            "topic": "DBMS Fundamentals",
            "answers": [{"question_id": "q1", "answer": "option-1"}],
            "total_time_spent_seconds": 15,
            "is_completed": True,
        }

        response = client.post("/api/v1/assessments/attempts", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == 0.5  # 1 out of 2, not 1.0!


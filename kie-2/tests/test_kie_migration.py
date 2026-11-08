import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.context_v2 import ContextQuestion
from app.schemas.syllabus import SyllabusExtractResponse
from app.schemas.roadmap import AIMLRoadmapResponse


class TestKIEMigrationContracts(unittest.TestCase):
    """
    Authoritative test suite verifying all 8 unified KIE endpoints
    required by Backend Migration Guide.
    """

    def setUp(self):
        self.client = TestClient(app)

    # ------------------------------------------------------------------------
    # Endpoint 1: POST /api/v1/kie/context/analyze
    # ------------------------------------------------------------------------
    @patch("app.api.v1.endpoints.context.get_context_service")
    def test_endpoint_1_context_analyze_fire_and_forget(self, mock_get_svc):
        mock_svc = MagicMock()
        mock_get_svc.return_value = mock_svc
        mock_svc.generate_questions.return_value = [
            ContextQuestion(
                question_id="q_001",
                text="What are your primary programming languages?",
                type="multi_select",
                options=["Python", "Java", "Go"],
            )
        ]

        payload = {
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "user_id": "user-auth-uuid-123",
            "learner": {
                "primary_goal": "Get a job in AI",
                "target_skills": ["Python", "ML"],
                "skills": ["Java"],
                "experience": "1 year internship",
            },
            "education": {
                "academic_status": "BACHELOR",
                "university": "MIT",
                "degree_program": "Computer Science",
                "domain": "Technology",
            },
            "preferences": {
                "daily_study_hours": "2_3",
                "learning_depth": "DEEP",
            },
            "syllabus": {},
            "roadmap": {},
            "recent_history": [],
            "memory_summary": {},
            "scope": None,
        }

        resp = self.client.post("/api/v1/kie/context/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "processing")
        self.assertIn("questions", data)

        # Verify background task was executed
        self.assertTrue(mock_svc.generate_questions.called)
        self.assertTrue(mock_svc.post_questions_webhook.called)
        call_user_id = mock_svc.post_questions_webhook.call_args[1].get("user_id") or mock_svc.post_questions_webhook.call_args[0][0]
        self.assertIn(call_user_id, ["user-auth-uuid-123", "00000000-0000-0000-0000-000000000001"])

    # ------------------------------------------------------------------------
    # Endpoint 2: POST /api/v1/kie/context/resolve
    # ------------------------------------------------------------------------
    @patch("app.api.v1.endpoints.context.get_context_service")
    def test_endpoint_2_context_resolve_fire_and_forget(self, mock_get_svc):
        mock_svc = MagicMock()
        mock_get_svc.return_value = mock_svc
        mock_svc.resolve_answers.return_value = {
            "primary_languages": ["Python", "Go"],
            "experience_level": "intermediate",
            "career_readiness": "moderate",
        }

        payload = {
            "user_id": "user-auth-uuid-123",
            "answers": [
                {"question_id": "q_001", "answer": ["Python", "Go"]},
                {"question_id": "q_002", "answer": "1-2 years"},
            ],
        }

        resp = self.client.post("/api/v1/kie/context/resolve", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")

        # Verify background task resolved answers and called webhook
        self.assertTrue(mock_svc.resolve_answers.called)
        self.assertTrue(mock_svc.post_resolved_webhook.called)

    # ------------------------------------------------------------------------
    # Endpoint 3: POST /api/v1/kie/syllabus/extract
    # ------------------------------------------------------------------------
    def test_endpoint_3_syllabus_extract_synchronous(self):
        payload = {
            "syllabus_id": "syl-uuid-123",
            "text": (
                "Course: Computer Science 101\n"
                "Module 1: Data Structures\n"
                "- Arrays and Linked Lists\n"
                "- Stacks and Queues\n"
                "Module 2: Algorithms\n"
                "- Sorting and Searching\n"
                "- Dynamic Programming\n"
            ),
        }

        resp = self.client.post("/api/v1/kie/syllabus/extract", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Backend ParsedContent validation
        validated = SyllabusExtractResponse.model_validate(data)
        self.assertGreaterEqual(len(validated.subjects), 1)
        for s in validated.subjects:
            self.assertTrue(len(s.name) > 0)
            self.assertGreaterEqual(len(s.topics), 1)

    # ------------------------------------------------------------------------
    # Endpoint 4: POST /api/v1/kie/roadmap/generate
    # ------------------------------------------------------------------------
    def test_endpoint_4_roadmap_generate_synchronous(self):
        payload = {
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "learner": {
                "primary_goal": "Get a job in AI",
                "skills": ["Python", "Java"],
            },
            "education": {
                "academic_status": "BACHELOR",
                "university": "Apex Institute",
                "degree_program": "Computer Science",
            },
            "syllabus": {
                "subjects": [
                    {
                        "name": "Data Structures",
                        "topics": ["Binary Trees", "Graphs", "Hash Tables"],
                    }
                ]
            },
            "scope": "ACADEMIC",
        }

        resp = self.client.post("/api/v1/kie/roadmap/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Backend AIMLRoadmapResponse validation
        validated = AIMLRoadmapResponse.model_validate(data)
        self.assertEqual(validated.scope, "ACADEMIC")
        self.assertGreaterEqual(len(validated.missions), 3)

        # Check mission field constraints
        for m in validated.missions:
            self.assertTrue(len(m.title) > 0)
            self.assertIn(m.type.value, ["LEARNING", "REVISION", "ASSIGNMENT", "PRACTICAL", "ARTIFACT", "CAREER"])
            self.assertIn(m.priority, ["HIGH", "MEDIUM", "LOW"])
            self.assertGreater(m.estimated_minutes, 0)
            self.assertGreater(m.week, 0)
            self.assertGreater(m.sequence, 0)

    # ------------------------------------------------------------------------
    # Endpoint 5: POST /api/v1/kie/memory/summary
    # ------------------------------------------------------------------------
    def test_endpoint_5_memory_summary_synchronous(self):
        payload = {
            "events": [
                {
                    "id": "ev-1",
                    "learner_id": "l-101",
                    "event_type": "MISSION_COMPLETED",
                    "entity_type": "MISSION",
                    "entity_id": "m-1",
                    "payload": {"topic": "Binary Search Trees"},
                    "created_at": "2026-10-30T10:00:00Z",
                },
                {
                    "id": "ev-2",
                    "learner_id": "l-101",
                    "event_type": "MISSION_SKIPPED",
                    "entity_type": "MISSION",
                    "entity_id": "m-2",
                    "payload": {"topic": "Dynamic Programming"},
                    "created_at": "2026-10-29T10:00:00Z",
                },
            ]
        }

        resp = self.client.post("/api/v1/kie/memory/summary", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, dict)
        self.assertIn("mastered_concepts", data)
        self.assertIn("struggling_concepts", data)
        self.assertIn("recommended_pacing", data)

    # ------------------------------------------------------------------------
    # Endpoint 6: POST /api/v1/kie/learn/interpret
    # ------------------------------------------------------------------------
    def test_endpoint_6_learn_interpret(self):
        payload = {
            "request_id": "req-001",
            "learner_id": "l-001",
            "topic": "Binary Search Trees",
            "user_intent": "Explain tree traversals with visual analogies",
            "references": [],
            "context": {},
        }
        resp = self.client.post("/api/v1/kie/learn/interpret", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("intent_category", data)
        self.assertIn("pedagogical_strategy", data)
        self.assertIn("knowledge_gaps_identified", data)

    # ------------------------------------------------------------------------
    # Endpoint 7: POST /api/v1/kie/lesson/generate
    # ------------------------------------------------------------------------
    def test_endpoint_7_lesson_generate(self):
        payload = {
            "request_id": "req-002",
            "learner_id": "l-001",
            "topic": "Binary Search Trees",
            "lesson_id": "lesson-bst-01",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "ANALOGY_THEN_CODE",
                "knowledge_gaps_identified": ["recursion"],
            },
            "references": [],
            "context": {},
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], "lesson-bst-01")
        self.assertIn("blocks", data)
        self.assertGreaterEqual(len(data["blocks"]), 3)
        self.assertTrue(len(data["blocks"][-1]["id"]) > 0)

    # ------------------------------------------------------------------------
    # Endpoint 8: POST /api/v1/kie/mastery/evaluate
    # ------------------------------------------------------------------------
    def test_endpoint_8_mastery_evaluate(self):
        payload = {
            "learner_id": "00000000-0000-0000-0000-000000000001",
            "assessment_id": "quiz-01",
            "topic": "Binary Search Trees",
            "total_time_spent_seconds": 120,
            "answers": [
                {"question_id": "q1", "answer": "C) O(N)", "hints_used": 0, "time_spent_seconds": 30},
                {"question_id": "q2", "answer": ["opt1", "opt2"], "hints_used": 1, "time_spent_seconds": 90},
            ],
        }
        resp = self.client.post("/api/v1/kie/mastery/evaluate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("score", data)
        self.assertGreaterEqual(data["score"], 0.0)
        self.assertLessEqual(data["score"], 1.0)
        self.assertIn("feedback", data)
        self.assertIn("mastery_updates", data)


if __name__ == "__main__":
    unittest.main()


import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas.memory_context import RoadmapStatus, RoadmapRecommendedAction
from app.schemas.memory_events import MemoryEventType, EvidenceSource
from app.services import get_memory_repository


class TestSprint3EndToEndLifecycle(unittest.TestCase):
    """End-to-End integration test suite for the complete Sprint 3 learner lifecycle.
    
    Validates the cross-subsystem pipeline:
    Onboarding -> Memory Initialization -> Context Retrieval -> Lesson Planning ->
    Failing Assessment (Friction Escalation) -> Roadmap Adaptation (Remediation) ->
    Remediation Assessment (Friction Resolution) -> Final Roadmap Adaptation ->
    Full Memory State Retrieval.
    """

    @classmethod
    def setUpClass(cls):
        # Enforce deterministic mock LLM provider to avoid rate limits or external dependencies
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        # Isolate memory repository before each test execution
        self.repo = get_memory_repository()
        self.repo.clear()
        self.client = TestClient(app)

    def test_01_complete_sprint3_learner_lifecycle(self):
        """Execute the primary 9-step Sprint 3 learner lifecycle for test_student_001:
        
        STEP 1 — Onboarding validation & intelligence analysis
        STEP 2 — Memory initialization via public events API
        STEP 3 — Relevant context retrieval for upcoming lesson
        STEP 4 — Pedagogical lesson planning and block generation
        STEP 5 — Ingest failing assessment (score 0.40 < 0.50) & escalate friction
        STEP 6 — Roadmap adaptation triggers needs_remediation
        STEP 7 — Ingest remediation assessment (score 0.88 > 0.85) & resolve friction
        STEP 8 — Final roadmap adaptation verifies remediation cleared
        STEP 9 — Retrieve full memory container and verify multi-step persistence
        """
        learner_id = "test_student_001"

        # -------------------------------------------------------------------------
        # STEP 1 — Onboarding
        # -------------------------------------------------------------------------
        onboarding_profile = {
            "learner_id": learner_id,
            "stage": "bachelor",
            "academic_program": "B.Tech Computer Science",
            "current_semester": 2,
            "target_role": "AI/ML Engineer",
            "declared_skills": [
                {
                    "skill_name": "Python",
                    "self_rating": 3,
                    "category": "programming",
                },
                {
                    "skill_name": "Linear Algebra",
                    "self_rating": 2,
                    "category": "theory",
                },
            ],
            "interests": ["Machine Learning", "Neural Networks"],
            "preferences": {
                "preferred_medium": "interactive",
                "pace": "standard",
                "weekly_hours": 15,
                "practical_vs_theory_ratio": 0.8,
            },
            "motivation_statement": "I want to master AI/ML engineering and build production deep learning applications.",
        }

        # 1a. Preflight validation
        resp_validate = self.client.post(
            "/api/v1/onboarding/validate-profile",
            json=onboarding_profile,
        )
        self.assertEqual(resp_validate.status_code, 200)
        val_data = resp_validate.json()
        self.assertTrue(val_data["is_valid"])
        self.assertEqual(val_data["learner_id"], learner_id)

        # 1b. Deep multi-dimensional intelligence analysis
        resp_analyze = self.client.post(
            "/api/v1/onboarding/analyze",
            json=onboarding_profile,
        )
        self.assertEqual(resp_analyze.status_code, 200)
        intel_data = resp_analyze.json()
        self.assertEqual(intel_data["learner_id"], learner_id)
        self.assertEqual(intel_data["target_role"], "AI/ML Engineer")
        # Assert structured intelligence dimensions returned
        self.assertIn("skill_analysis", intel_data)
        self.assertIn("knowledge_analysis", intel_data)
        self.assertIn("learning_style", intel_data)
        self.assertIn("career_goals", intel_data)
        self.assertIn("motivation", intel_data)
        self.assertIn("readiness", intel_data)

        # -------------------------------------------------------------------------
        # STEP 2 — Memory Initialization
        # (Using existing public memory event API as onboarding->memory bridge is not yet built)
        # -------------------------------------------------------------------------
        # 2a. Target Career Goal
        resp_goal = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.GOAL_CREATED.value,
                "evidence_source": EvidenceSource.EXPLICIT.value,
                "confidence_score": 1.0,
                "payload": {
                    "primary_target_role": "AI/ML Engineer",
                    "target_timeline_months": 6,
                    "milestones": [
                        "Python Foundations",
                        "Linear Algebra & Calculus",
                        "PyTorch Deep Learning",
                    ],
                },
            },
        )
        self.assertEqual(resp_goal.status_code, 200)
        goal_res = resp_goal.json()
        self.assertTrue(goal_res["success"])
        self.assertIn("goals", goal_res["updated_facets"])

        # 2b. Learning Preferences
        resp_pref = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.PREFERENCE_OBSERVED.value,
                "evidence_source": EvidenceSource.EXPLICIT.value,
                "confidence_score": 1.0,
                "payload": {
                    "dominant_modality": "interactive",
                    "pacing": "standard",
                    "practical_vs_theory_ratio": 0.8,
                },
            },
        )
        self.assertEqual(resp_pref.status_code, 200)
        pref_res = resp_pref.json()
        self.assertTrue(pref_res["success"])
        self.assertIn("preferences", pref_res["updated_facets"])

        # 2c. Baseline Weak Topic / Struggle Signal
        resp_fric_1 = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.TOPIC_STRUGGLED.value,
                "evidence_source": EvidenceSource.OBSERVED.value,
                "confidence_score": 0.9,
                "payload": {
                    "topic": "Python Functions",
                    "struggle_type": "conceptual_gap",
                    "details": "Difficulty understanding parameter passing and scoping rules",
                },
            },
        )
        self.assertEqual(resp_fric_1.status_code, 200)
        self.assertTrue(resp_fric_1.json()["success"])

        resp_fric_2 = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.REPEATED_MISTAKE.value,
                "evidence_source": EvidenceSource.OBSERVED.value,
                "confidence_score": 0.9,
                "payload": {
                    "topic": "Python Functions",
                    "details": "Repeated NameError on local variable scope in nested functions",
                },
            },
        )
        self.assertEqual(resp_fric_2.status_code, 200)
        self.assertTrue(resp_fric_2.json()["success"])

        # -------------------------------------------------------------------------
        # STEP 3 — Relevant Context Retrieval
        # -------------------------------------------------------------------------
        resp_context = self.client.post(
            "/api/v1/memory/relevant-context",
            json={
                "learner_id": learner_id,
                "topic": "Python Functions",
                "objective": "Master Python function parameters",
            },
        )
        self.assertEqual(resp_context.status_code, 200)
        ctx_data = resp_context.json()
        self.assertEqual(ctx_data["learner_id"], learner_id)
        self.assertEqual(ctx_data["topic"], "Python Functions")
        self.assertEqual(
            ctx_data["relevant_preferences"]["dominant_modality"], "interactive"
        )
        self.assertEqual(
            ctx_data["active_goal"]["primary_target_role"], "AI/ML Engineer"
        )
        # Verify scoped friction was retrieved for Python Functions
        self.assertTrue(len(ctx_data["relevant_friction"]) >= 1)
        self.assertTrue(
            any(f["topic"] == "Python Functions" for f in ctx_data["relevant_friction"])
        )
        self.assertIsNotNone(ctx_data.get("recommended_pedagogical_mode"))
        self.assertTrue(len(ctx_data.get("rationale", "")) > 0)

        # -------------------------------------------------------------------------
        # STEP 4 — Lesson Generation
        # -------------------------------------------------------------------------
        lesson_payload = {
            "context_id": "ctx_lifecycle_001",
            "topic": "Python Functions",
            "objective": "Master Python function parameters",
            "learner_state": {
                "learner_id": learner_id,
                "stage": "bachelor",
                "confidence": "medium",
                "weak_topics": ["Python Functions"],
                "career_goal": "AI/ML Engineer",
                "learning_preference": "interactive",
            },
            "time_budget_minutes": 15,
        }

        resp_lesson = self.client.post(
            "/api/v1/learning/plan-lesson",
            json=lesson_payload,
        )
        self.assertEqual(resp_lesson.status_code, 200)
        lesson_data = resp_lesson.json()
        self.assertEqual(lesson_data["context_id"], "ctx_lifecycle_001")
        self.assertEqual(lesson_data["topic"], "Python Functions")
        self.assertIn("pedagogy_decision", lesson_data)
        self.assertIn("strategy", lesson_data["pedagogy_decision"])
        self.assertIn("presentation_mode", lesson_data["pedagogy_decision"])
        self.assertIn("blocks", lesson_data)
        self.assertIsInstance(lesson_data["blocks"], list)
        self.assertTrue(len(lesson_data["blocks"]) > 0)

        # -------------------------------------------------------------------------
        # STEP 5 — Failing Assessment Ingestion (< 0.50)
        # -------------------------------------------------------------------------
        resp_fail = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.ASSESSMENT_RESULT.value,
                "evidence_source": EvidenceSource.OBSERVED.value,
                "confidence_score": 0.95,
                "payload": {
                    "topic": "Python Functions",
                    "score": 0.40,
                },
            },
        )
        self.assertEqual(resp_fail.status_code, 200)
        fail_data = resp_fail.json()
        self.assertTrue(fail_data["success"])
        self.assertTrue(fail_data["friction_level_updated"])
        self.assertIn("friction", fail_data["updated_facets"])
        self.assertIn("learning_history", fail_data["updated_facets"])

        # -------------------------------------------------------------------------
        # STEP 6 — Roadmap Adaptation After Failure
        # -------------------------------------------------------------------------
        resp_rm_fail = self.client.post(
            "/api/v1/memory/roadmap-context",
            json={
                "learner_id": learner_id,
                "current_topic": "Python Functions",
            },
        )
        self.assertEqual(resp_rm_fail.status_code, 200)
        rm_fail_data = resp_rm_fail.json()
        self.assertEqual(
            rm_fail_data["status"], RoadmapStatus.NEEDS_REMEDIATION.value
        )
        self.assertEqual(
            rm_fail_data["recommended_action"],
            RoadmapRecommendedAction.INSERT_REMEDIATION.value,
        )
        self.assertIn("Python Functions", rm_fail_data["remediation_topics"])

        # -------------------------------------------------------------------------
        # STEP 7 — Remediation Assessment Ingestion (> 0.85)
        # -------------------------------------------------------------------------
        resp_remed = self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.ASSESSMENT_RESULT.value,
                "evidence_source": EvidenceSource.OBSERVED.value,
                "confidence_score": 0.95,
                "payload": {
                    "topic": "Python Functions",
                    "score": 0.88,
                },
            },
        )
        self.assertEqual(resp_remed.status_code, 200)
        remed_data = resp_remed.json()
        self.assertTrue(remed_data["success"])
        self.assertTrue(remed_data["friction_level_updated"])
        self.assertIn("learning_history", remed_data["updated_facets"])

        # -------------------------------------------------------------------------
        # STEP 8 — Final Roadmap Adaptation
        # -------------------------------------------------------------------------
        resp_rm_final = self.client.post(
            "/api/v1/memory/roadmap-context",
            json={
                "learner_id": learner_id,
                "current_topic": "Python Functions",
            },
        )
        self.assertEqual(resp_rm_final.status_code, 200)
        rm_final_data = resp_rm_final.json()
        # Verify status is NO LONGER needs_remediation
        self.assertNotEqual(
            rm_final_data["status"], RoadmapStatus.NEEDS_REMEDIATION.value
        )
        self.assertIn(
            rm_final_data["status"],
            [
                RoadmapStatus.ON_TRACK.value,
                RoadmapStatus.READY_FOR_ADVANCEMENT.value,
                RoadmapStatus.GOAL_SHIFTED.value,
            ],
        )
        # Python Functions must no longer be in active remediation
        self.assertNotIn("Python Functions", rm_final_data.get("remediation_topics", []))

        # -------------------------------------------------------------------------
        # STEP 9 — Final Memory Container Retrieval & Verification
        # -------------------------------------------------------------------------
        resp_retrieve = self.client.post(
            "/api/v1/memory/retrieve",
            json={"learner_id": learner_id},
        )
        self.assertEqual(resp_retrieve.status_code, 200)
        mem = resp_retrieve.json()

        self.assertEqual(mem["learner_id"], learner_id)
        # Both failing (0.40) and remediation (0.88) assessments are preserved
        self.assertGreaterEqual(len(mem["learning_history"]), 2)
        scores = [h["assessment_score"] for h in mem["learning_history"] if h["assessment_score"] is not None]
        self.assertIn(0.40, scores)
        self.assertIn(0.88, scores)

        # Friction on Python Functions was marked as resolved by score 0.88
        fric_funcs = [f for f in mem["friction"] if f["topic"] == "Python Functions"]
        self.assertTrue(len(fric_funcs) > 0)
        self.assertFalse(
            fric_funcs[0]["unresolved"],
            "Score 0.88 (> 0.85) must resolve friction on Python Functions",
        )

        # Verify preferences and goals preserved
        self.assertEqual(mem["preferences"]["dominant_modality"], "interactive")
        self.assertEqual(mem["goals"]["primary_target_role"], "AI/ML Engineer")

    def test_02_remediation_transition_to_on_track_progression(self):
        """Verify that when a learner with standard curriculum goals remediates a topic,
        the roadmap status transitions strictly to ON_TRACK (proceed_next_topic).
        """
        learner_id = "test_ontrack_student"

        # Baseline goal aligned to default Software Engineer role (no goal shift)
        self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.GOAL_CREATED.value,
                "payload": {"primary_target_role": "Software Engineer"},
            },
        )

        # Establish high-severity struggle on Recursion
        self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.TOPIC_STRUGGLED.value,
                "payload": {"topic": "Recursion"},
            },
        )
        self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.REPEATED_MISTAKE.value,
                "payload": {"topic": "Recursion"},
            },
        )
        self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.ASSESSMENT_RESULT.value,
                "payload": {"topic": "Recursion", "score": 0.45},
            },
        )

        # Confirm needs_remediation
        r_fail = self.client.post(
            "/api/v1/memory/roadmap-context",
            json={"learner_id": learner_id, "current_topic": "Recursion"},
        )
        self.assertEqual(r_fail.json()["status"], RoadmapStatus.NEEDS_REMEDIATION.value)

        # Pass remediation with score 0.88 (> 0.85)
        self.client.post(
            "/api/v1/memory/events",
            json={
                "learner_id": learner_id,
                "event_type": MemoryEventType.ASSESSMENT_RESULT.value,
                "payload": {"topic": "Recursion", "score": 0.88},
            },
        )

        # Confirm strict transition to ON_TRACK
        r_pass = self.client.post(
            "/api/v1/memory/roadmap-context",
            json={"learner_id": learner_id, "current_topic": "Recursion"},
        )
        self.assertEqual(r_pass.json()["status"], RoadmapStatus.ON_TRACK.value)
        self.assertEqual(
            r_pass.json()["recommended_action"],
            RoadmapRecommendedAction.PROCEED_NEXT_TOPIC.value,
        )
        self.assertEqual(len(r_pass.json()["remediation_topics"]), 0)


if __name__ == "__main__":
    unittest.main()

import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    MasteryTier,
    AssessmentAttemptType,
    AssessmentEvidence,
)
from app.services import get_mastery_engine, get_memory_engine


class TestSprint4MasteryEngine(unittest.TestCase):
    """Test suite for Task A2-S4-03 Mastery & Weakness Intelligence Engine."""

    def setUp(self):
        self.mastery_engine = get_mastery_engine()
        self.memory_engine = get_memory_engine()
        self.client = TestClient(app)

    # 1. Canonical BRD Tiers: Weak (< 50%), Developing (50-79%), Proficient (80-100%)
    def test_01_canonical_brd_mastery_tiers_and_thresholds(self):
        """Verify strict classification into Weak, Developing, and Proficient tiers (Section 6.4)."""
        learner_id = "tier_test_student"

        # Diagnostic attempt: 0.40 -> Weak
        evidence_weak = AssessmentEvidence(
            learner_id=learner_id,
            topic="Dynamic Programming",
            score=0.40,
            attempt_type=AssessmentAttemptType.DIAGNOSTIC,
        )
        res_weak = self.mastery_engine.evaluate_assessment(evidence_weak)
        self.assertEqual(res_weak.mastery_tier, MasteryTier.WEAK)
        self.assertFalse(res_weak.is_proficient)
        self.assertTrue(res_weak.remediation_signal.remediation_required)

        # Reassessment attempt: 0.65 -> Developing
        evidence_dev = AssessmentEvidence(
            learner_id=learner_id,
            topic="Dynamic Programming",
            score=0.65,
            attempt_type=AssessmentAttemptType.FORMATIVE,
        )
        res_dev = self.mastery_engine.evaluate_assessment(evidence_dev)
        self.assertEqual(res_dev.mastery_tier, MasteryTier.DEVELOPING)
        self.assertFalse(res_dev.is_proficient)
        self.assertFalse(res_dev.remediation_signal.remediation_required)

        # High score: 0.90 -> Proficient
        evidence_prof = AssessmentEvidence(
            learner_id=learner_id,
            topic="Dynamic Programming",
            score=0.90,
            attempt_type=AssessmentAttemptType.REASSESSMENT,
        )
        res_prof = self.mastery_engine.evaluate_assessment(evidence_prof)
        self.assertEqual(res_prof.mastery_tier, MasteryTier.PROFICIENT)
        self.assertTrue(res_prof.is_proficient)
        self.assertFalse(res_prof.remediation_signal.remediation_required)
        self.assertEqual(res_prof.remediation_signal.recommended_strategy, "advancement")

    # 2. Measurable Remediation Signal Generation
    def test_02_measurable_remediation_signal_on_struggle(self):
        """Verify poor performance emits concrete, measurable remediation signals."""
        learner_id = "remediation_sig_student"
        evidence = AssessmentEvidence(
            learner_id=learner_id,
            topic="Pointers & Memory Allocation",
            subtopic="Heap Fragmentation",
            score=0.30,
            attempt_type=AssessmentAttemptType.FORMATIVE,
            questions_total=10,
            questions_correct=3,
        )
        result = self.mastery_engine.evaluate_assessment(evidence)

        sig = result.remediation_signal
        self.assertTrue(sig.remediation_required)
        self.assertEqual(sig.severity, "high")
        self.assertEqual(sig.recommended_strategy, "remediation")
        self.assertIn("Pointers & Memory Allocation", sig.weak_concepts)
        self.assertIn("Heap Fragmentation", sig.weak_concepts)
        self.assertIn("remediation loop", sig.recommended_action.lower())
        self.assertIn(evidence.topic, result.weak_areas)

    # 3. Memory Synchronization
    def test_03_assessment_evaluation_synchronizes_with_memory(self):
        """Verify that evaluating an assessment updates learner history in MemoryEngine."""
        learner_id = "sync_memory_student"
        evidence = AssessmentEvidence(
            learner_id=learner_id,
            topic="SQL Indexing",
            score=0.92,
            attempt_type=AssessmentAttemptType.FORMATIVE,
        )
        self.mastery_engine.evaluate_assessment(evidence)

        mem = self.memory_engine.get_or_create_memory(learner_id)
        # Check that learning_history contains the assessment
        sql_history = [h for h in mem.learning_history if h.topic == "SQL Indexing"]
        self.assertGreaterEqual(len(sql_history), 1)
        self.assertEqual(sql_history[-1].assessment_score, 0.92)


    # 4. HTTP Assessment Evaluation API
    def test_04_http_evaluate_assessment_api(self):
        """Verify POST /api/v1/learning/evaluate-assessment endpoint."""
        payload = {
            "learner_id": "api_assess_user",
            "topic": "Tax Accounting",
            "score": "45%",  # Test defensive percentage parsing
            "attempt_type": "formative",
            "questions_total": 10,
            "questions_correct": 4,
        }
        res = self.client.post("/api/v1/learning/evaluate-assessment", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["learner_id"], "api_assess_user")
        self.assertEqual(data["topic"], "Tax Accounting")
        self.assertEqual(data["mastery_tier"], "weak")
        self.assertTrue(data["remediation_signal"]["remediation_required"])


if __name__ == "__main__":
    unittest.main()

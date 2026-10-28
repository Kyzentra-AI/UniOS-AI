import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import MasteryTier
from app.services import get_remediation_service


class TestSprint4RemediationLoop(unittest.TestCase):
    """Test suite for Task A2-S4-04 Remediation Closed Loop."""

    def setUp(self):
        self.remediation_service = get_remediation_service()
        self.client = TestClient(app)

    # 1. Closed Loop: Struggle -> Remediation -> Reassessment Success -> Proficiency
    def test_01_closed_loop_struggle_to_proficiency(self):
        """Verify the complete cycle: initial failure -> remediation -> reassessment recovery -> progression."""
        result = self.remediation_service.run_remediation_cycle(
            learner_id="remediation_hero_01",
            topic="Asynchronous Concurrency",
            initial_score=0.35,        # Initial failure (< 0.50)
            reassessment_score=0.88,   # Reassessment recovery (>= 0.80)
            academic_domain="engineering",
        )

        self.assertEqual(result.topic, "Asynchronous Concurrency")
        self.assertEqual(result.initial_tier, MasteryTier.WEAK)
        self.assertTrue(result.remediation_applied)
        self.assertEqual(result.remediation_strategy, "remediation")
        self.assertEqual(result.final_tier, MasteryTier.PROFICIENT)
        self.assertEqual(result.progression_status, "remediated_proficient")
        self.assertIn("Promote learner to next", result.next_recommended_action)
        self.assertGreaterEqual(len(result.steps), 3)

    # 2. Closed Loop: Continued Struggle -> Escalation
    def test_02_closed_loop_continued_struggle_triggers_escalation(self):
        """Verify that poor reassessment score keeps the learner in remediation and escalates."""
        result = self.remediation_service.run_remediation_cycle(
            learner_id="escalation_student_01",
            topic="Compiler Optimization",
            initial_score=0.25,        # Initial failure
            reassessment_score=0.38,   # Continued failure (< 0.50)
            academic_domain="engineering",
        )

        self.assertEqual(result.initial_tier, MasteryTier.WEAK)
        self.assertTrue(result.remediation_applied)
        self.assertEqual(result.final_tier, MasteryTier.WEAK)
        self.assertEqual(result.progression_status, "escalated")
        self.assertIn("Escalate struggle", result.next_recommended_action)

    # 3. Next Recommended Action Changes Based on Learner Evidence
    def test_03_next_action_changes_dynamically_with_evidence(self):
        """Verify that different learner evidence alters the next pedagogical recommendation."""
        # Struggle case
        result_struggle = self.remediation_service.run_remediation_cycle(
            learner_id="dynamic_user_a",
            topic="Microeconomics",
            initial_score=0.40,
        )
        self.assertTrue(result_struggle.remediation_applied)
        self.assertIn("remediation loop", result_struggle.next_recommended_action.lower())

        # High achievement case
        result_success = self.remediation_service.run_remediation_cycle(
            learner_id="dynamic_user_b",
            topic="Microeconomics",
            initial_score=0.92,
        )
        self.assertFalse(result_success.remediation_applied)
        self.assertIn("Advance learner", result_success.next_recommended_action)

    # 4. HTTP Remediation Loop API Endpoint
    def test_04_http_remediation_loop_api(self):
        """Verify POST /api/v1/learning/remediation-loop endpoint."""
        payload = {
            "learner_id": "http_loop_user",
            "topic": "Constitutional Law Due Process",
            "initial_score": 0.32,
            "reassessment_score": 0.85,
            "academic_domain": "law",
            "learner_stage": "bachelor",
        }
        res = self.client.post("/api/v1/learning/remediation-loop", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["progression_status"], "remediated_proficient")
        self.assertEqual(data["final_tier"], "proficient")
        self.assertTrue(data["remediation_applied"])


if __name__ == "__main__":
    unittest.main()

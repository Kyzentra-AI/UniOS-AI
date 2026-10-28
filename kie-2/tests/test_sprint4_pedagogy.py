import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    NormalizedLearningContext,
    LearnerState,
    LearnerStage,
    ConfidenceLevel,
    TeachingStrategy,
    DifficultyLevel,
    PresentationMode,
    PracticeLevel,
)
from app.services import get_pedagogy_engine


class TestSprint4PedagogyEngine(unittest.TestCase):
    """Test suite for Task A2-S4-01 Pedagogy Engine and the Universal 5-Learner Test."""

    def setUp(self):
        self.engine = get_pedagogy_engine()
        self.client = TestClient(app)

    # 1. Evidence-Driven Pedagogy: High Mastery vs Active Friction
    def test_01_same_topic_different_learner_evidence_produces_different_pedagogy(self):
        """Verify that the same topic produces materially different pedagogy based on learner evidence."""
        topic = "Recursion"

        # Learner A: High mastery (0.90), high confidence, wants advancement
        state_advanced = LearnerState(
            learner_id="advanced_learner_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.HIGH,
            concept_mastery={topic: 0.90},
            weak_topics=[],
            academic_domain="engineering",
        )
        ctx_advanced = NormalizedLearningContext(
            context_id="ctx_adv_01",
            request_id="req_adv_01",
            topic=topic,
            objective="Analyze tail recursion optimization and call stack limits",
            learner_state=state_advanced,
            academic_domain="engineering",
        )
        decision_adv = self.engine.determine_pedagogy(ctx_advanced)

        self.assertEqual(decision_adv.strategy, TeachingStrategy.ADVANCEMENT)
        self.assertEqual(decision_adv.difficulty, DifficultyLevel.ADVANCED)
        self.assertEqual(decision_adv.practice_level, PracticeLevel.CHALLENGE_BASED)
        self.assertFalse(decision_adv.remediation)
        self.assertIn("concept_synthesis", decision_adv.sequence)

        # Learner B: Low mastery (0.25), active weakness, low confidence
        state_remedial = LearnerState(
            learner_id="struggling_learner_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.LOW,
            concept_mastery={topic: 0.25},
            weak_topics=[topic],
            academic_domain="engineering",
        )
        ctx_remedial = NormalizedLearningContext(
            context_id="ctx_rem_01",
            request_id="req_rem_01",
            topic=topic,
            objective="Understand base cases and prevent infinite recursion",
            learner_state=state_remedial,
            academic_domain="engineering",
        )
        decision_rem = self.engine.determine_pedagogy(ctx_remedial)

        self.assertEqual(decision_rem.strategy, TeachingStrategy.REMEDIATION)
        self.assertEqual(decision_rem.difficulty, DifficultyLevel.BEGINNER)
        self.assertEqual(decision_rem.practice_level, PracticeLevel.REMEDIAL)
        self.assertTrue(decision_rem.remediation)
        self.assertIn("prerequisite_review", decision_rem.sequence)

        # Confirm strategies and sequences are materially different
        self.assertNotEqual(decision_adv.strategy, decision_rem.strategy)
        self.assertNotEqual(decision_adv.difficulty, decision_rem.difficulty)
        self.assertNotEqual(decision_adv.practice_level, decision_rem.practice_level)

    # 2. Universal Five-Learner Architecture Test (Section 18 / 2.5)
    def test_02_universal_five_learner_architecture_fixtures(self):
        """Verify distinct, domain-appropriate pedagogy decisions for the five required learner fixtures:
        1. B.Tech CSE (Engineering)
        2. B.Com (Commerce / Finance)
        3. BA Humanities (Arts / Psychology)
        4. MSc Science (Life Sciences / Biotech)
        5. Recent MBA Graduate (Management / Business)
        """
        # Fixture 1: B.Tech CSE
        btech_state = LearnerState(
            learner_id="btech_student_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.MEDIUM,
            academic_program="B.Tech Computer Science",
            academic_domain="engineering",
        )
        btech_ctx = NormalizedLearningContext(
            topic="Deadlock Prevention",
            objective="Analyze resource allocation graphs",
            learner_state=btech_state,
            academic_domain="engineering",
        )
        btech_decision = self.engine.determine_pedagogy(btech_ctx)
        self.assertEqual(btech_decision.presentation_mode, PresentationMode.VISUAL)

        # Fixture 2: B.Com (Commerce / Finance)
        bcom_state = LearnerState(
            learner_id="bcom_student_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.MEDIUM,
            academic_program="Bachelor of Commerce",
            academic_domain="commerce",
        )
        bcom_ctx = NormalizedLearningContext(
            topic="Depreciation Methods",
            objective="Evaluate straight-line vs declining balance impact on balance sheet",
            learner_state=bcom_state,
            academic_domain="commerce",
        )
        bcom_decision = self.engine.determine_pedagogy(bcom_ctx)
        self.assertEqual(bcom_decision.presentation_mode, PresentationMode.CASE_STUDY)

        # Fixture 3: BA Humanities (Psychology)
        ba_state = LearnerState(
            learner_id="ba_student_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.MEDIUM,
            academic_program="BA Psychology",
            academic_domain="humanities",
        )
        ba_ctx = NormalizedLearningContext(
            topic="Cognitive Dissonance Theory",
            objective="Critique Festinger's experimental paradigm",
            learner_state=ba_state,
            academic_domain="humanities",
        )
        ba_decision = self.engine.determine_pedagogy(ba_ctx)
        self.assertEqual(ba_decision.presentation_mode, PresentationMode.ANALYTICAL)

        # Fixture 4: MSc Science (Biotechnology)
        msc_state = LearnerState(
            learner_id="msc_student_01",
            stage=LearnerStage.MASTER,
            confidence=ConfidenceLevel.MEDIUM,
            academic_program="MSc Biotechnology",
            academic_domain="science",
        )
        msc_ctx = NormalizedLearningContext(
            topic="CRISPR-Cas9 Gene Editing",
            objective="Model off-target guide RNA cleavage kinetics",
            learner_state=msc_state,
            academic_domain="science",
        )
        msc_decision = self.engine.determine_pedagogy(msc_ctx)
        self.assertEqual(msc_decision.presentation_mode, PresentationMode.SIMULATION)
        self.assertEqual(msc_decision.explanation_depth, "deep-dive")

        # Fixture 5: Recent MBA Graduate (Management)
        mba_state = LearnerState(
            learner_id="mba_grad_01",
            stage=LearnerStage.GRADUATE,
            confidence=ConfidenceLevel.HIGH,
            academic_program="Master of Business Administration",
            academic_domain="management",
            concept_mastery={"Mergers & Acquisitions": 0.85},
        )
        mba_ctx = NormalizedLearningContext(
            topic="Mergers & Acquisitions",
            objective="Assess synergy valuation and post-merger integration risks",
            learner_state=mba_state,
            academic_domain="management",
        )
        mba_decision = self.engine.determine_pedagogy(mba_ctx)
        self.assertEqual(mba_decision.presentation_mode, PresentationMode.CASE_STUDY)
        self.assertEqual(mba_decision.strategy, TeachingStrategy.ADVANCEMENT)

    # 3. Missing Context Resilience
    def test_03_missing_optional_context_safe_fallbacks(self):
        """Verify that minimal contexts without memory or domain defaults cleanly."""
        state = LearnerState(learner_id="minimal_user")
        ctx = NormalizedLearningContext(
            topic="General Problem Solving",
            objective="Breakdown complex problems",
            learner_state=state,
        )
        decision = self.engine.determine_pedagogy(ctx)
        self.assertIsNotNone(decision.strategy)
        self.assertIsNotNone(decision.difficulty)
        self.assertIsNotNone(decision.sequence)
        self.assertGreaterEqual(len(decision.sequence), 3)

    # 4. HTTP API Endpoint Verification
    def test_04_http_pedagogy_decision_endpoint(self):
        """Verify POST /api/v1/learning/pedagogy-decision endpoint."""
        payload = {
            "context_id": "ctx_http_ped_01",
            "request_id": "req_http_ped_01",
            "topic": "Microeconomics Elasticity",
            "objective": "Calculate price elasticity of demand",
            "academic_domain": "commerce",
            "learner_state": {
                "learner_id": "http_ped_user",
                "stage": "bachelor",
                "confidence": "medium",
                "concept_mastery": {"Microeconomics Elasticity": 0.65},
            },
        }
        res = self.client.post("/api/v1/learning/pedagogy-decision", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["strategy"], "reinforcement")
        self.assertEqual(data["presentation_mode"], "case_study")
        self.assertIn("sequence", data)
        self.assertIn("practice_level", data)


if __name__ == "__main__":
    unittest.main()

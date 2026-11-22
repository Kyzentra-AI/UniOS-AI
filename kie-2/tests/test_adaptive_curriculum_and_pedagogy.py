import unittest
from app.data.canonical_curricula import DAA_CANONICAL_CURRICULUM, get_canonical_curriculum
from app.schemas.context_v2 import AnalyzeContextRequest
from app.schemas.pedagogy import TeachingStrategy, DifficultyLevel, PresentationMode
from app.schemas import NormalizedLearningContext, LearnerStage, ConfidenceLevel
from app.services.pedagogy_engine import get_pedagogy_engine
from app.services.roadmap_service import get_roadmap_service
from app.services.syllabus_extract_service import get_syllabus_extract_service
from app.services.prompt_builder import get_strategy_delivery_guidelines, build_lesson_prompt


class TestAdaptiveCurriculumAndPedagogy(unittest.TestCase):
    def setUp(self):
        self.pedagogy_engine = get_pedagogy_engine()
        self.roadmap_service = get_roadmap_service()
        self.syllabus_service = get_syllabus_extract_service()

    def test_canonical_daa_curriculum_structure(self):
        """Verify DAA has 7 chapters, outcomes, and comprehensive topics."""
        curriculum = get_canonical_curriculum("Design and Analysis of Algorithms")
        self.assertIsNotNone(curriculum)
        self.assertEqual(len(curriculum["chapters"]), 7)

        expected_chapters = [
            "Introduction to Algorithms",
            "Divide and Conquer",
            "Greedy Algorithms",
            "Dynamic Programming",
            "Backtracking",
            "Branch and Bound",
            "Graph Algorithms and Complexity Theory",
        ]
        actual_chapters = [c["title"] for c in curriculum["chapters"]]
        self.assertEqual(actual_chapters, expected_chapters)

        # Verify Chapter 1 topics (from PDF page 3 & 4)
        ch1 = curriculum["chapters"][0]
        self.assertEqual(len(ch1["topics"]), 7)
        self.assertIn("Characteristics of Algorithms", [t["title"] for t in ch1["topics"]])
        self.assertIn("Time Complexity", [t["title"] for t in ch1["topics"]])
        self.assertIn("Space Complexity", [t["title"] for t in ch1["topics"]])
        self.assertIn("Asymptotic Notations: Big-O, Big-Omega and Big-Theta", [t["title"] for t in ch1["topics"]])

    def test_pedagogy_engine_adaptive_strategies(self):
        """Verify PedagogyEngine dynamically selects Irfan's 5 strategies based on evidence."""
        # 1. Remediation / low confidence -> foundational_support
        ctx_remed = NormalizedLearningContext(
            topic="Dynamic Programming",
            objective="Understand memoization",
            learner_state={
                "learner_id": "u1",
                "stage": "bachelor",
                "confidence": "low",
                "weak_topics": ["Dynamic Programming"],
            },
        )
        dec_remed = self.pedagogy_engine.determine_pedagogy(ctx_remed)
        self.assertEqual(dec_remed.adaptive_strategy, TeachingStrategy.FOUNDATIONAL_SUPPORT.value)

        # 2. Visual presentation mode -> visual_support
        ctx_visual = NormalizedLearningContext(
            topic="Divide and Conquer",
            objective="Understand recursion trees",
            learner_state={
                "learner_id": "u2",
                "stage": "bachelor",
                "confidence": "medium",
                "learning_preference": "visual",
            },
        )
        dec_visual = self.pedagogy_engine.determine_pedagogy(ctx_visual)
        self.assertEqual(dec_visual.adaptive_strategy, TeachingStrategy.VISUAL_SUPPORT.value)

        # 3. High mastery -> advanced_extension
        ctx_adv = NormalizedLearningContext(
            topic="Asymptotic Notations",
            objective="Prove formal bounds",
            learner_state={
                "learner_id": "u3",
                "stage": "master",
                "confidence": "high",
                "concept_mastery": {"Asymptotic Notations": 0.95},
            },
        )
        dec_adv = self.pedagogy_engine.determine_pedagogy(ctx_adv)
        self.assertEqual(dec_adv.adaptive_strategy, TeachingStrategy.ADVANCED_EXTENSION.value)

    def test_strategy_delivery_guidelines(self):
        """Verify delivery instructions for each strategy."""
        g_found = get_strategy_delivery_guidelines(TeachingStrategy.FOUNDATIONAL_SUPPORT)
        self.assertIn("Foundational Support", g_found)
        self.assertIn("plain language", g_found)

        g_vis = get_strategy_delivery_guidelines(TeachingStrategy.VISUAL_SUPPORT)
        self.assertIn("Visual Support", g_vis)
        self.assertIn("flowcharts", g_vis)

        g_log = get_strategy_delivery_guidelines(TeachingStrategy.LOGICAL_ANALYTICAL)
        self.assertIn("Logical / Analytical Support", g_log)
        self.assertIn("mathematical recurrence", g_log)

        g_prac = get_strategy_delivery_guidelines(TeachingStrategy.PRACTICAL_APPLIED)
        self.assertIn("Practical / Applied Support", g_prac)
        self.assertIn("executable code", g_prac)

        g_adv = get_strategy_delivery_guidelines(TeachingStrategy.ADVANCED_EXTENSION)
        self.assertIn("Advanced / Extension", g_adv)
        self.assertIn("edge-case optimization", g_adv)

    def test_single_subject_daa_roadmap_grounding(self):
        """Verify targeted DAA roadmap generates missions matching all 7 canonical chapters."""
        req = AnalyzeContextRequest(
            learner_id="00000000-0000-0000-0000-000000000001",
            user_id="u_auth_123",
            target_subject="Design and Analysis of Algorithms",
            scope="ACADEMIC",
        )
        resp = self.roadmap_service._generate_single_subject_deterministic(
            req, "ACADEMIC", "Design and Analysis of Algorithms"
        )
        self.assertEqual(resp.target_subject, "Design and Analysis of Algorithms")
        self.assertGreaterEqual(len(resp.missions), 7)

        # Verify missions cover canonical chapters
        mission_chapters = {m.chapter for m in resp.missions if m.chapter}
        self.assertIn("Introduction to Algorithms", mission_chapters)
        self.assertIn("Divide and Conquer", mission_chapters)
        self.assertIn("Greedy Algorithms", mission_chapters)
        self.assertIn("Dynamic Programming", mission_chapters)

        # Subject tracks must include canonical chapters
        self.assertTrue(len(resp.subject_tracks) >= 1)
        st = resp.subject_tracks[0]
        self.assertEqual(len(st.chapters), 7)

    def test_syllabus_extract_daa_canonical(self):
        """Verify syllabus fallback extracts DAA canonical chapters."""
        text = "Course syllabus: Design and Analysis of Algorithms (DAA), divide and conquer, dynamic programming"
        res = self.syllabus_service._build_fallback("syl_test", text)
        self.assertTrue(any(s.name == "Design and Analysis of Algorithms" for s in res.subjects))


if __name__ == "__main__":
    unittest.main()

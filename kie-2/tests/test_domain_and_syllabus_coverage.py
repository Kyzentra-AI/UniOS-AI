import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.context_v2 import AnalyzeContextRequest
from app.services.roadmap_service import get_roadmap_service


class TestDomainAndSyllabusCoverage(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.roadmap_service = get_roadmap_service()

    def test_daa_lesson_generates_algorithm_code_not_sql(self):
        """Issue 2: Ensure DAA generates algorithmic merge_sort / asymptotic analysis, not SQL table."""
        payload = {
            "topic": "Design and Analysis of Algorithms",
            "objective": "Understand asymptotic complexity and divide-and-conquer",
            "learner_state": {"learner_id": "u1", "stage": "bachelor", "confidence": "medium"},
            "lesson_id": "les-daa",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "VISUAL_THEN_THEORY",
                "knowledge_gaps_identified": ["asymptotic complexity"],
            },
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]

        content_all = " ".join((b.get("content") or "") for b in blocks)
        self.assertNotIn("CREATE TABLE", content_all)
        self.assertNotIn("Enterprise Alpha", content_all)
        self.assertIn("merge_sort", content_all)
        self.assertIn("log", content_all.lower())

    def test_toc_lesson_generates_automata_not_sql(self):
        """Issue 2: Ensure Theory of Computation generates DFA / state machine, not SQL table."""
        payload = {
            "topic": "Theory of Computation",
            "objective": "Understand formal languages and state machines",
            "learner_state": {"learner_id": "u1", "stage": "bachelor", "confidence": "medium"},
            "lesson_id": "les-toc",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "VISUAL_THEN_THEORY",
                "knowledge_gaps_identified": ["dfa"],
            },
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]

        content_all = " ".join((b.get("content") or "") for b in blocks)
        self.assertNotIn("CREATE TABLE", content_all)
        self.assertNotIn("Enterprise Alpha", content_all)
        self.assertTrue(
            "DeterministicFiniteAutomaton" in content_all or "DFA" in content_all,
            f"Expected DFA or DeterministicFiniteAutomaton in content, got: {content_all[:300]}",
        )

    def test_neural_networks_lesson_generates_pytorch_and_neuron_math(self):
        """Verify Neural Networks demonstration topic follows the Section 5 Teaching Blueprint."""
        payload = {
            "topic": "Artificial Neural Networks",
            "objective": "Explain neuron mechanics, calculate weighted sum, and implement PyTorch classifier",
            "learner_state": {"learner_id": "u1", "stage": "bachelor", "confidence": "medium"},
            "lesson_id": "les-nn",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "ANALOGY_THEN_CODE",
                "knowledge_gaps_identified": ["artificial neuron", "backpropagation"],
            },
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]

        content_all = " ".join((b.get("content") or "") for b in blocks)
        self.assertNotIn("CREATE TABLE", content_all)
        self.assertNotIn("Tata Group", content_all)
        self.assertNotIn("Principles & Theories of Management", content_all)
        self.assertIn("torch", content_all.lower())
        self.assertIn("linear", content_all.lower())
        self.assertIn("sigmoid", content_all.lower())

        # Also verify offline blueprint contains exact Section 5 reference calculations and remediation
        from app.services.llm_provider import MockLLMProvider
        mock_lesson = MockLLMProvider().generate_lesson(prompt="", context_id="mock-nn", topic="Artificial Neural Networks")
        mock_content = " ".join((b.content or "") for b in mock_lesson.blocks)
        self.assertIn("0.973", mock_content)
        self.assertIn("784", mock_content)
        self.assertIn("Misconception", mock_content)

    def test_multisubject_full_syllabus_coverage(self):
        """Issue 1: Ensure 8 subjects each receive at least 2 progressive missions covering full syllabus."""
        subjects = [
            {"name": "Design and Analysis of Algorithms", "topics": ["Asymptotic Analysis", "Divide and Conquer", "Dynamic Programming", "Greedy Algorithms"]},
            {"name": "Theory of Computation", "topics": ["Finite Automata", "Context-Free Grammars", "Turing Machines"]},
            {"name": "Artificial Intelligence", "topics": ["Search Agents", "Heuristics", "Adversarial Search"]},
            {"name": "Enterprise Programming using Java", "topics": ["JDBC", "Spring Boot", "REST APIs"]},
            {"name": "Quantitative Aptitude and Reasoning", "topics": ["Number Systems", "Percentages", "Permutations"]},
            {"name": "Design and Analysis of Algorithms Laboratory", "topics": ["Sorting Lab", "Graph Traversal Lab"]},
            {"name": "Professionalism & Corporate Ethics", "topics": ["Ethical Theories", "Corporate Governance"]},
        ]

        req = AnalyzeContextRequest(
            learner_id="00000000-0000-0000-0000-000000000001",
            user_id="user-auth-uuid-123",
            syllabus={"subjects": subjects},
            scope="ACADEMIC",
        )

        res = self.roadmap_service._generate_multi_subject_deterministic(req, "ACADEMIC")

        # Every subject must have missions
        for subj in subjects:
            s_name = subj["name"]
            matching = [m for m in res.missions if m.subject.strip().lower() == s_name.strip().lower()]
            self.assertGreaterEqual(
                len(matching),
                2,
                f"Subject '{s_name}' must have at least 2 progressive missions for full syllabus coverage, found {len(matching)}",
            )

        # Subject tracks must be present for all subjects
        track_names = {t.subject_name.lower() for t in res.subject_tracks}
        for subj in subjects:
            self.assertIn(subj["name"].lower(), track_names)

    def test_zoology_lesson_has_zero_software_leakage(self):
        """Verify Medical/Zoology topic generates zero CS strings, zero code, and is classified as GENERAL_HUMANITIES_SCIENCE."""
        payload = {
            "topic": "Foundations of Life and Zoological Scope",
            "objective": "Understand biological diversity, animal kingdom taxonomy, and ecological scope",
            "academic_domain": "Life Sciences",
            "learner_state": {
                "learner_id": "u_med_01",
                "stage": "bachelor",
                "confidence": "medium",
                "academic_program": "B.Sc Zoology",
                "career_goal": "Zoological Researcher",
            },
            "lesson_id": "les-zoology-01",
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]
        self.assertEqual(len(blocks), 5)

        for b in blocks:
            self.assertIsNone(b.get("code"), f"Code block found in Zoology topic: {b.get('title')}")
            content = (b.get("content") or "").lower()
            for bad_str in ["modular, maintainable", "type-safe", "separation of concerns", "software architecture", "persistence layers", "api contract"]:
                self.assertNotIn(bad_str, content, f"Found leaked CS string '{bad_str}' in Zoology block '{b.get('title')}'")

    def test_physics_kinematics_math_sanitization(self):
        """Verify Physics Kinematics lesson does not contain raw unrendered \\text{} macros in math."""
        from app.services.content_sanitizer import sanitize_math_and_latex

        raw_math = """
• $u = 20 , \\text{m/s}$
• $a = -5 , \\text{m/s}^2$
• $v = 0 , \\text{m/s}$ (because it stops)
• $t = ?$
• $s = ?$
$$v = u + at$$
"""
        cleaned = sanitize_math_and_latex(raw_math)
        self.assertNotIn(r"\text{", cleaned)
        self.assertIn("20 m/s", cleaned)
        self.assertIn("-5 m/s²", cleaned)
        self.assertIn("v = 0 m/s", cleaned)
        self.assertIn("t = ?", cleaned)
        self.assertIn("$$v = u + at$$", cleaned)

    def test_medical_context_questions_have_no_programming(self):
        """Verify ContextService does not ask programming questions to medical/life sciences learners."""
        from app.services.context_service import ContextService
        cs = ContextService()
        med_ctx = {
            "learner": {"learner_id": "student_med_01"},
            "education": {"degree_program": "B.Sc Zoology", "domain": "Life Sciences", "academic_status": "BACHELOR"},
        }
        questions = cs._generate_questions_deterministic(med_ctx)
        self.assertEqual(len(questions), 4)
        for q in questions:
            self.assertNotIn("programming", q.text.lower())
            for opt in q.options:
                self.assertNotIn("python", opt.lower())
                self.assertNotIn("javascript", opt.lower())

    def test_medical_roadmap_has_no_software_engineer_goal(self):
        """Verify roadmap generation for medical/zoology syllabus does not default to Software Engineer."""
        subjects = [
            {"name": "Animal Diversity & Systematics", "topics": ["Invertebrates", "Vertebrates", "Comparative Anatomy"]},
            {"name": "Cell Biology & Genetics", "topics": ["Cell Structure", "Mendelian Genetics", "DNA Replication"]},
        ]
        req = AnalyzeContextRequest(
            learner_id="00000000-0000-0000-0000-000000000002",
            user_id="user-auth-uuid-456",
            syllabus={"subjects": subjects},
            education={"degree_program": "B.Sc Zoology", "domain": "Life Sciences"},
            scope="BOTH",
        )
        res = self.roadmap_service._generate_multi_subject_deterministic(req, "BOTH")
        self.assertIsNotNone(res.career)
        career_goals_str = " ".join(res.career.goals).lower()
        self.assertNotIn("software engineer", career_goals_str)
        self.assertNotIn("production architecture", career_goals_str)
        for m in res.missions:
            desc = m.description.lower()
            self.assertNotIn("production-grade implementation with comprehensive unit and boundary test", desc)


if __name__ == "__main__":
    unittest.main()

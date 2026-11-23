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


if __name__ == "__main__":
    unittest.main()

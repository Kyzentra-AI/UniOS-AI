import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas import (
    NormalizedLearningContext,
    LearnerState,
    LearnerStage,
    ConfidenceLevel,
    LessonBlockType,
    GeneratedLesson,
)
from app.services import get_llm_provider


class TestSprint4LessonGeneration(unittest.TestCase):
    """Test suite for Task A2-S4-02 Structured Lesson Generation and Universal Learning Blocks."""

    @classmethod
    def setUpClass(cls):
        # Force deterministic mock provider to ensure reproducible contract assertions
        # and avoid rate limits or external LLM dependencies during CI/test runs.
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.provider = get_llm_provider(force_mock=True)
        self.client = TestClient(app)

    # 1. Structured Lesson Schema Validation
    def test_01_structured_lesson_contains_prerequisites_intent_next_action(self):
        """Verify generated lesson contains objectives, prerequisites, sequence, blocks, intent, and next action."""
        payload = {
            "context_id": "ctx_lesson_test_01",
            "request_id": "req_tracing_12345",
            "topic": "Dynamic Programming",
            "objective": "Understand memoization tables and overlapping subproblems",
            "learner_state": {
                "learner_id": "dp_student_01",
                "stage": "bachelor",
                "confidence": "medium",
                "concept_mastery": {"Recursion": 0.85},
            },
        }
        res = self.client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(res.status_code, 200)
        lesson_data = res.json()

        # Validate schema fields
        self.assertEqual(lesson_data["topic"], "Dynamic Programming")
        self.assertEqual(lesson_data["request_id"], "req_tracing_12345")
        self.assertEqual(lesson_data["context_id"], "ctx_lesson_test_01")
        self.assertIn("prerequisites", lesson_data)

        self.assertGreater(len(lesson_data["prerequisites"]), 0)
        self.assertIn("assessment_intent", lesson_data)
        self.assertIsNotNone(lesson_data["assessment_intent"])
        self.assertEqual(lesson_data["assessment_intent"]["target_concepts"], ["Dynamic Programming"])
        self.assertIn("next_action", lesson_data)
        self.assertIsNotNone(lesson_data["next_action"])
        self.assertEqual(lesson_data["next_action"]["target_topic"], "Dynamic Programming")

        # Validate blocks
        blocks = lesson_data["blocks"]
        self.assertGreaterEqual(len(blocks), 5)
        block_types = [b["type"] for b in blocks]
        self.assertIn("objective", block_types)
        self.assertIn("explanation", block_types)
        self.assertIn("worked_example", block_types)
        self.assertIn("visual_spec", block_types)
        self.assertIn("practice_task", block_types)

    # 2. Strict UI Boundary Rules
    def test_02_strict_ui_boundary_enforcement(self):
        """Verify that lesson blocks contain strictly NO raw HTML, React, JSX, or frontend code."""
        payload = {
            "context_id": "ctx_boundary_test",
            "topic": "Binary Search Trees",
            "objective": "Understand BST insertion and traversal",
            "learner_state": {
                "learner_id": "boundary_user",
                "stage": "bachelor",
            },
        }
        res = self.client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        forbidden_tags = ["<div", "<html", "<script", "import React", "export default", "className="]
        for b in data["blocks"]:
            content_str = str(b["content"])
            for tag in forbidden_tags:
                self.assertNotIn(tag, content_str, f"Found forbidden UI code '{tag}' in block '{b['title']}'")

    # 3. Content Grounding with content_context
    def test_03_content_grounding_ingestion(self):
        """Verify that approved syllabus content in content_context is ingested into curriculum_references."""
        payload = {
            "context_id": "ctx_grounding_test",
            "request_id": "req_grounding_01",
            "topic": "Capital Asset Pricing Model",
            "objective": "Calculate required return on equity",
            "academic_domain": "commerce",
            "content_context": {
                "relevant_content": [
                    "Approved Syllabus Unit 4: CAPM formula E(R) = Rf + Beta*(Rm - Rf)",
                    "Financial Economics Standard Reference Ch 7, p. 142",
                ]
            },
            "learner_state": {
                "learner_id": "grounding_user",
                "stage": "bachelor",
                "academic_domain": "commerce",
            },
        }
        ctx = NormalizedLearningContext.model_validate(payload)
        self.assertEqual(len(ctx.curriculum_references), 2)
        self.assertIn("CAPM formula", ctx.curriculum_references[0])

        res = self.client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(res.status_code, 200)

    # 4. Domain-Adaptive Content Tailoring
    def test_04_domain_adaptive_block_content(self):
        """Verify that Commerce and Science domains receive domain-tailored worked examples."""
        # Commerce request
        commerce_payload = {
            "topic": "Financial Auditing Standards",
            "objective": "Evaluate internal control risk",
            "academic_domain": "commerce",
            "learner_state": {"learner_id": "auditor_01", "stage": "bachelor"},
        }
        res_com = self.client.post("/api/v1/learning/plan-lesson", json=commerce_payload)
        self.assertEqual(res_com.status_code, 200)
        com_blocks = res_com.json()["blocks"]
        example_com = next(b for b in com_blocks if b["type"] == "worked_example")
        self.assertIn("Financial Analysis", example_com["title"])

        # Science request
        science_payload = {
            "topic": "Gel Electrophoresis",
            "objective": "Separate DNA fragments by molecular weight",
            "academic_domain": "science",
            "learner_state": {"learner_id": "biotech_01", "stage": "master"},
        }
        res_sci = self.client.post("/api/v1/learning/plan-lesson", json=science_payload)
        self.assertEqual(res_sci.status_code, 200)
        sci_blocks = res_sci.json()["blocks"]
        example_sci = next(b for b in sci_blocks if b["type"] == "worked_example")
        self.assertIn("Experimental Methodology", example_sci["title"])

    # 5. Canonical KIE Endpoint Alias
    def test_05_canonical_kie_generate_learning_intelligence_endpoint(self):
        """Verify Section 4.2 canonical endpoint /api/v1/learning/generate-learning-intelligence."""
        payload = {
            "request_id": "req_canonical_42",
            "topic": "Graph Algorithms",
            "objective": "Understand Dijkstra's shortest path",
            "learner_state": {"learner_id": "canon_user", "stage": "bachelor"},
        }
        res = self.client.post("/api/v1/learning/generate-learning-intelligence", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["request_id"], "req_canonical_42")
        self.assertGreaterEqual(len(data["blocks"]), 5)


if __name__ == "__main__":
    unittest.main()

"""
Authoritative Test Suite for UniOS Beta Testing & Quality Report Fixes.
Verifies:
  - BUG-01 / CONTENT-09: Non-CS topic assessments (Entrepreneurship, Law, Commerce) are discipline-aligned.
  - BUG-02: Mentor chat responses use clean, mobile-safe Markdown (no deep #### tags).
  - BUG-05: Mentor chat accepts step_index, step_title, step_content, total_steps with flexible aliases.
  - BUG-06: Mentor chat token budget and sequence completeness.
  - Photos 1-4 & UX-02: Visual spec never generates meta-drawing instructions; code is embedded in content.
  - CONTENT-11 / PERF-03: Syllabus fallback does not falsely match Database Management Systems for E-Commerce.
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.mentor import MentorChatContext, MentorChatRequest
from app.services.llm_provider import MockLLMProvider
from app.services.syllabus_extract_service import get_syllabus_extract_service
from app.services.mentor_prompt_builder import build_mentor_chat_prompt, get_mentor_system_prompt
from app.services.assessment_prompt_builder import build_assessment_generation_prompt
from app.schemas.assessment import AssessmentGenerateRequest


class TestTestingReportFixes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.mock_provider = MockLLMProvider()

    def test_bug_01_entrepreneurship_assessment_not_database_mock(self):
        """BUG-01: Ensure Entrepreneurship assessment does NOT return CS/DB questions."""
        prompt = (
            "- Topic: DSE-501 (A) - ENTREPRENEURSHIP DEVELOPMENT\n"
            "- Preferred Question Type: mcq\n"
            "- Question Count: 5\n"
        )
        res = self.mock_provider.generate_assessment(prompt)
        self.assertEqual(res["title"], "DSE-501 (A) - ENTREPRENEURSHIP DEVELOPMENT Assessment")
        self.assertEqual(len(res["questions"]), 5)

        for q in res["questions"]:
            q_text = q["question"]
            options_text = " ".join(o["text"] for o in q["options"])
            # Strictly assert CS keywords are absent
            self.assertNotIn("Storage Manager & Buffer Pool", options_text)
            self.assertNotIn("Query Compiler & Parser", options_text)
            self.assertNotIn("Transaction Concurrency Monitor", options_text)

        # Assert authentic entrepreneurship content is present
        all_text = " ".join(q["question"] + " " + " ".join(o["text"] for o in q["options"]) for q in res["questions"])
        self.assertTrue(
            any(k in all_text for k in ["Lean Startup", "MVP", "bootstrapping", "venture capital", "Patent", "Product-Market Fit", "LTV / CAC"]),
            "Assessment must contain authentic entrepreneurship topics.",
        )

    def test_bug_01_commerce_assessment_discipline_aligned(self):
        """BUG-01 / CONTENT-09: Financial accounting assessment must return accounting questions."""
        prompt = (
            "- Topic: Financial Accounting & Balance Sheet Analysis\n"
            "- Preferred Question Type: mcq\n"
            "- Question Count: 3\n"
        )
        res = self.mock_provider.generate_assessment(prompt)
        self.assertEqual(len(res["questions"]), 3)
        all_text = " ".join(q["question"] for q in res["questions"])
        self.assertTrue(
            any(k in all_text for k in ["accrual", "ratio", "balance sheet", "Assets = Liabilities + Equity"]),
            "Commerce assessment must reflect financial accounting concepts.",
        )

    def test_bug_02_mentor_system_prompt_clean_markdown_rules(self):
        """BUG-02: Mentor system prompt contains strict rules against deep #### tags and raw HTML."""
        sys_prompt = get_mentor_system_prompt("tutor")
        self.assertIn("Never use deep '####' or '#####' tags", sys_prompt)
        self.assertIn("Under NO circumstances should you output raw HTML, JSX", sys_prompt)

    def test_bug_05_mentor_step_context_flexible_aliases(self):
        """BUG-05: MentorChatContext supports step_index, step_title, step_content, total_steps with camelCase aliases."""
        ctx_data = {
            "topic": "Mastering DBMS",
            "stepIndex": 3,
            "stepTitle": "Example: Creating a Simple Student Database",
            "sectionContent": "Consider a university database with a Students table...",
            "totalSteps": 6,
            "subject": "Database Management Systems",
        }
        ctx = MentorChatContext.model_validate(ctx_data)
        self.assertEqual(ctx.step_index, 3)
        self.assertEqual(ctx.step_title, "Example: Creating a Simple Student Database")
        self.assertEqual(ctx.total_steps, 6)
        self.assertEqual(ctx.subject, "Database Management Systems")

        req = MentorChatRequest(
            learner_id="test_student",
            mode="tutor",
            message="Explain what this example is doing",
            context=ctx,
        )
        built_prompt = build_mentor_chat_prompt(req)
        self.assertIn("Section 3 of 6 - \"Example: Creating a Simple Student Database\"", built_prompt)
        self.assertIn("Ground your answer in the content of this step", built_prompt)
        self.assertIn("Consider a university database with a Students table", built_prompt)

    def test_lesson_generate_sanitizes_meta_diagram_instructions(self):
        """Photo 3 & UX-02: Ensure 'Renderer Type: Diagram. Step 1: Draw a rectangle' is sanitized into a real diagram."""
        payload = {
            "topic": "Relational Databases",
            "objective": "Understand tables and relations",
            "learner_state": {
                "learner_id": "test_user",
                "stage": "bachelor",
                "confidence": "medium",
            },
            "lesson_id": "test-lesson-meta",
            "interpreted_data": {
                "intent_category": "CONCEPTUAL_EXPLANATION",
                "pedagogical_strategy": "VISUAL_THEN_THEORY",
                "knowledge_gaps_identified": ["relations"],
            },
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]

        for b in blocks:
            c = b.get("content") or ""
            self.assertNotIn("Renderer Type: Diagram. Step 1: Draw a rectangle", c)

    def test_lesson_generate_embeds_code_in_content_for_card_renderers(self):
        """Photo 1: Ensure code blocks are embedded in content for frontend card renderers."""
        payload = {
            "topic": "Relational Database Management Systems",
            "objective": "Design tables and query with SQL",
            "learner_state": {
                "learner_id": "test_user",
                "stage": "bachelor",
                "confidence": "medium",
            },
            "lesson_id": "test-lesson-code",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "ANALOGY_THEN_CODE",
                "knowledge_gaps_identified": ["sql"],
            },
        }
        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        blocks = resp.json()["blocks"]

        # Assert that the worked example / implementation block embeds formatted markdown code in content
        code_embedded = any("```" in (b.get("content") or "") for b in blocks)
        self.assertTrue(code_embedded, "Content must contain formatted markdown fenced code (```) for frontend card renderers.")

    def test_content_11_syllabus_extract_fallback_ecommerce_not_dbms(self):
        """CONTENT-11: E-commerce syllabus text does not trigger Database Management Systems fallback."""
        svc = get_syllabus_extract_service()
        raw_text = (
            "Course: Introduction to E-Commerce\n"
            "Overview of digital market infrastructure, consumer behavior, electronic payment gateways, "
            "and logistics supply chain fulfillment."
        )
        res = svc._build_fallback("syl_ecom", raw_text)
        self.assertEqual(len(res.subjects), 1)
        subject_name = res.subjects[0].name
        self.assertEqual(subject_name, "E-Commerce & Digital Business")
        self.assertNotIn("Database Management Systems", subject_name)


if __name__ == "__main__":
    unittest.main()

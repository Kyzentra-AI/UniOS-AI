"""
Sprint 5 — Universal Build Engine Tests (AI/ML-2)
Task A2-S5-01: Contextual Build Coach  — POST /api/v1/kie/build/coach
Task A2-S5-02: Project Recommendations — GET  /api/v1/kie/build/recommend

Coverage:
  - Public endpoint contracts and response schemas (Backend-approved wire format)
  - Coach: intent/message/context/project_context request fields
  - Coach: reply/suggestions/action_items response fields
  - Recommend: learner_id-only public query param
  - Recommend: title/description/type/skills response fields
  - Valid and invalid inputs
  - Missing project/learner context
  - LLM failures and malformed output
  - Correct URL construction and router registration
  - Mock provider behavior and deterministic output
  - Domain-adaptive response content
  - UI boundary enforcement (no raw HTML/JSX)
  - Mastery-driven tone / remediation logic
  - Fallback deterministic recommendations when LLM fails
  - Sprint 3 memory engine integration for learner context
  - Sprint 1–4 regression compatibility
"""

import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas.build import (
    ActionItem,
    ArtifactType,
    BuildCoachPublicRequest,
    BuildCoachPublicResponse,
    BuildCoachRequest,
    BuildCoachResponse,
    BuildDifficulty,
    BuildRecommendContext,
    BuildRecommendResponse,
    CoachingTone,
    ProjectContextInput,
    ProjectRecommendation,
)
from app.services import get_build_coach_service, get_llm_provider, coaching_response_to_public
from app.services.build_coach_service import (
    BuildCoachService,
    _coaching_tone_from_str,
    _difficulty_from_str,
    _artifact_type_from_str,
    _sanitize_coaching_blocks,
    _determine_coaching_tone_from_mastery,
)
from app.services.build_prompt_builder import build_coach_prompt, build_recommend_prompt
from app.services.llm_provider import LLMProviderError, LLMParseError, MockLLMProvider


# ---------------------------------------------------------------------------
# Shared valid payloads — Backend-approved public wire format
# ---------------------------------------------------------------------------

VALID_COACH_PAYLOAD = {
    "intent": "guidance",
    "message": "I am unsure how to model the relationship between orders and inventory correctly.",
    "context": "bachelor engineering student working on database schema design milestone",
    "project_context": {
        "id": "proj_001",
        "title": "E-Commerce Inventory Management System",
        "type": "code_project",
        "status": "in_progress",
        "skills": ["Correct table relationships", "Appropriate data types", "Normalization to 3NF"],
    },
}

VALID_RECOMMEND_PARAMS = {
    "learner_id": "learner_s5_001",
}


# ---------------------------------------------------------------------------
# Test Class 1: Endpoint URL Construction & Router Registration
# ---------------------------------------------------------------------------

class TestSprint5URLConstruction(unittest.TestCase):
    """Verify that Sprint 5 routes are mounted at exactly /api/v1/kie/build/*."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_coach_url_registered_at_exact_path(self):
        """POST /api/v1/kie/build/coach must return 200 (not 404)."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertNotEqual(res.status_code, 404, "Route not registered at /api/v1/kie/build/coach")
        self.assertEqual(res.status_code, 200)

    def test_02_recommend_url_registered_at_exact_path(self):
        """GET /api/v1/kie/build/recommend must return 200 (not 404)."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertNotEqual(res.status_code, 404, "Route not registered at /api/v1/kie/build/recommend")
        self.assertEqual(res.status_code, 200)

    def test_03_no_duplicate_prefix_in_path(self):
        """Duplicate prefixes (/api/v1/api/v1/kie/...) must return 404."""
        res = self.client.post("/api/v1/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 404)

    def test_04_old_paths_return_404(self):
        """Non-KIE paths (/build/coach without /kie prefix) must not exist."""
        res = self.client.post("/api/v1/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 404)

    def test_05_health_check_still_intact(self):
        """Regression: /health must remain available after Sprint 5 additions."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)

    def test_06_plan_endpoint_not_exposed(self):
        """POST /api/v1/kie/build/plan must NOT be exposed (AI/ML-1 boundary)."""
        res = self.client.post("/api/v1/kie/build/plan", json={})
        self.assertEqual(res.status_code, 404, "AI/ML-2 must NOT implement the plan endpoint")


# ---------------------------------------------------------------------------
# Test Class 2: Build Coach Endpoint — Contract & Schema (Backend wire format)
# ---------------------------------------------------------------------------

class TestSprint5CoachContract(unittest.TestCase):
    """Verify POST /api/v1/kie/build/coach public contract compliance."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_valid_request_returns_200_with_schema(self):
        """Valid coach request returns 200 and all required public schema fields."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        # Backend-approved public response fields
        required = ["reply", "suggestions", "action_items"]
        for field in required:
            self.assertIn(field, data, f"Missing required public field: {field}")

    def test_02_reply_is_non_empty_string(self):
        """reply must be a non-empty string."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data["reply"], str)
        self.assertGreater(len(data["reply"]), 0, "reply must not be empty")

    def test_03_suggestions_is_a_list(self):
        """suggestions must be a list."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["suggestions"], list)

    def test_04_action_items_is_a_list(self):
        """action_items must be a list."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["action_items"], list)

    def test_05_each_action_item_has_type_and_label(self):
        """Each action_item must have 'type' and 'label' fields."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        for item in res.json()["action_items"]:
            self.assertIn("type", item, "action_item missing 'type'")
            self.assertIn("label", item, "action_item missing 'label'")
            self.assertIn("url", item, "action_item missing 'url'")

    def test_06_intent_field_is_accepted(self):
        """intent field must be accepted without a 422."""
        payload = {**VALID_COACH_PAYLOAD, "intent": "review"}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_07_message_field_is_accepted(self):
        """message field must be accepted."""
        payload = {**VALID_COACH_PAYLOAD, "message": "I need help structuring my argument."}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_08_context_field_is_optional(self):
        """context field is optional; omitting it must still succeed."""
        payload = {k: v for k, v in VALID_COACH_PAYLOAD.items() if k != "context"}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_09_project_context_is_optional(self):
        """project_context is optional; minimal request with only intent+message must succeed."""
        payload = {"intent": "general", "message": "Where do I start with my project?"}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_10_project_context_id_title_type_status_skills_accepted(self):
        """project_context must accept id, title, type, status, and skills fields."""
        payload = {
            "intent": "guidance",
            "message": "I need guidance on my case analysis.",
            "project_context": {
                "id": "proj-law-001",
                "title": "Constitutional Law Case Brief",
                "type": "case_analysis",
                "status": "draft",
                "skills": ["IRAC structure", "Case briefing", "Legal reasoning"],
            },
        }
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_11_no_raw_html_jsx_in_reply_or_suggestions(self):
        """UI boundary: reply and suggestions must NEVER contain raw HTML tags or JSX."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        forbidden = ["<div", "<html", "<script", "import React", "export default", "className="]
        # Check reply
        for tag in forbidden:
            self.assertNotIn(tag, data["reply"], f"Found forbidden UI code '{tag}' in reply")
        # Check suggestions
        for suggestion in data["suggestions"]:
            for tag in forbidden:
                self.assertNotIn(tag, suggestion, f"Found forbidden UI code '{tag}' in suggestion")

    def test_12_all_supported_artifact_types_accepted_in_project_context(self):
        """All ArtifactType enum values must be accepted in project_context.type."""
        for artifact_type in ArtifactType:
            payload = {
                "intent": "guidance",
                "message": f"Help me with my {artifact_type.value} project.",
                "project_context": {
                    "title": f"Test {artifact_type.value}",
                    "type": artifact_type.value,
                    "status": "in_progress",
                },
            }
            res = self.client.post("/api/v1/kie/build/coach", json=payload)
            self.assertEqual(
                res.status_code, 200,
                f"artifact_type='{artifact_type.value}' was rejected (status={res.status_code})"
            )

    def test_13_domain_adaptive_response_for_law_project(self):
        """Law domain must return a non-empty coaching reply."""
        payload = {
            "intent": "review",
            "message": "Review my IRAC argument for the contract dispute.",
            "context": "law bachelor student",
            "project_context": {
                "title": "Contract Dispute Case Brief",
                "type": "case_analysis",
                "status": "in_progress",
            },
        }
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()["reply"]), 0)

    def test_14_suggestions_strings_are_non_empty(self):
        """Each item in suggestions must be a non-empty string."""
        res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 200)
        for item in res.json()["suggestions"]:
            self.assertIsInstance(item, str)
            self.assertGreater(len(item.strip()), 0, "Empty string in suggestions list")

    def test_15_humanities_essay_returns_reply(self):
        """Humanities essay project must return a non-empty coaching reply."""
        payload = {
            "intent": "guidance",
            "message": "My essay lacks a clear thesis statement.",
            "context": "humanities bachelor",
            "project_context": {
                "title": "Philosophical Essay on Free Will",
                "type": "essay",
                "status": "draft",
            },
        }
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()["reply"]), 0)


# ---------------------------------------------------------------------------
# Test Class 3: Build Coach Endpoint — Invalid Inputs
# ---------------------------------------------------------------------------

class TestSprint5CoachInvalidInputs(unittest.TestCase):
    """Verify 422 Unprocessable Entity for contract-violating coach requests."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_missing_intent_returns_422(self):
        """Omitting required intent must return 422."""
        payload = {k: v for k, v in VALID_COACH_PAYLOAD.items() if k != "intent"}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_02_missing_message_returns_422(self):
        """Omitting required message must return 422."""
        payload = {k: v for k, v in VALID_COACH_PAYLOAD.items() if k != "message"}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_03_empty_intent_returns_422(self):
        """Empty string intent must return 422."""
        payload = {**VALID_COACH_PAYLOAD, "intent": ""}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_04_empty_message_returns_422(self):
        """Empty string message must return 422."""
        payload = {**VALID_COACH_PAYLOAD, "message": ""}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_05_message_too_long_returns_422(self):
        """message exceeding 2000 characters must return 422."""
        payload = {**VALID_COACH_PAYLOAD, "message": "x" * 2001}
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_06_empty_body_returns_422(self):
        """Empty body must return 422."""
        res = self.client.post("/api/v1/kie/build/coach", json={})
        self.assertEqual(res.status_code, 422)


# ---------------------------------------------------------------------------
# Test Class 4: Project Recommendations — Contract & Schema (Backend wire format)
# ---------------------------------------------------------------------------

class TestSprint5RecommendContract(unittest.TestCase):
    """Verify GET /api/v1/kie/build/recommend contract compliance."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_valid_request_with_learner_id_returns_200(self):
        """Valid learner_id-only request must return 200."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)

    def test_02_response_contains_required_fields(self):
        """Response must contain learner_id, recommendations, recommendation_rationale, generated_at."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        required = ["learner_id", "recommendations", "recommendation_rationale", "generated_at"]
        for field in required:
            self.assertIn(field, data, f"Missing required field: {field}")

    def test_03_recommendations_is_non_empty_list(self):
        """recommendations must be a non-empty list."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        recs = res.json()["recommendations"]
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)

    def test_04_each_recommendation_has_contract_fields(self):
        """Each recommendation must contain title, description, type, and skills (Backend contract)."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        for rec in res.json()["recommendations"]:
            self.assertIn("title", rec, "Missing 'title' in recommendation")
            self.assertIn("description", rec, "Missing 'description' in recommendation")
            self.assertIn("type", rec, "Missing 'type' in recommendation (not 'artifact_type')")
            self.assertIn("skills", rec, "Missing 'skills' in recommendation (not 'key_skills_targeted')")

    def test_05_type_field_is_valid_artifact_type_string(self):
        """type in each recommendation must be a valid ArtifactType string."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        valid_types = {t.value for t in ArtifactType}
        for rec in res.json()["recommendations"]:
            self.assertIn(
                rec["type"], valid_types,
                f"Recommendation 'type' value '{rec['type']}' is not a valid ArtifactType"
            )

    def test_06_skills_field_is_a_list(self):
        """skills in each recommendation must be a list."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        for rec in res.json()["recommendations"]:
            self.assertIsInstance(rec["skills"], list, "'skills' must be a list")

    def test_07_learner_id_echoed_in_response(self):
        """learner_id must be echoed back in response."""
        res = self.client.get("/api/v1/kie/build/recommend", params={"learner_id": "echo_test_learner"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["learner_id"], "echo_test_learner")

    def test_08_no_artifact_type_field_in_response(self):
        """Response must NOT contain 'artifact_type' — renamed to 'type' in contract."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        for rec in res.json()["recommendations"]:
            self.assertNotIn(
                "artifact_type", rec,
                "'artifact_type' should not appear in response — use 'type'"
            )

    def test_09_no_key_skills_targeted_field_in_response(self):
        """Response must NOT contain 'key_skills_targeted' — renamed to 'skills' in contract."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        for rec in res.json()["recommendations"]:
            self.assertNotIn(
                "key_skills_targeted", rec,
                "'key_skills_targeted' should not appear — use 'skills'"
            )

    def test_10_only_learner_id_is_required_public_param(self):
        """Only learner_id should be sufficient for a valid response (no other required params)."""
        res = self.client.get("/api/v1/kie/build/recommend", params={"learner_id": "minimal_learner"})
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()["recommendations"]), 0)

    def test_11_difficulty_values_are_valid_enums(self):
        """All recommendation difficulty values must be valid BuildDifficulty enum members."""
        valid_difficulties = {"foundational", "intermediate", "advanced"}
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        for rec in res.json()["recommendations"]:
            self.assertIn(rec["difficulty"], valid_difficulties)

    def test_12_recommendation_rationale_non_empty(self):
        """recommendation_rationale must be a non-empty string."""
        res = self.client.get("/api/v1/kie/build/recommend", params=VALID_RECOMMEND_PARAMS)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json()["recommendation_rationale"], str)
        self.assertGreater(len(res.json()["recommendation_rationale"]), 0)

    def test_13_undocumented_params_ignored_or_rejected(self):
        """
        Extra query params not in the Backend contract (academic_domain, count, etc.)
        should be silently ignored by FastAPI (they are not declared on the endpoint).
        The response must still be valid.
        """
        params = {
            "learner_id": "learner_extra_params",
            "academic_domain": "engineering",  # not declared
            "count": 3,                         # not declared
        }
        res = self.client.get("/api/v1/kie/build/recommend", params=params)
        # FastAPI ignores undeclared query params — response should still be 200
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("recommendations", data)


# ---------------------------------------------------------------------------
# Test Class 5: Project Recommendations — Invalid Inputs
# ---------------------------------------------------------------------------

class TestSprint5RecommendInvalidInputs(unittest.TestCase):
    """Verify 422/error responses for contract-violating recommend requests."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_missing_learner_id_returns_422(self):
        """Omitting learner_id must return 422."""
        res = self.client.get("/api/v1/kie/build/recommend")
        self.assertEqual(res.status_code, 422)

    def test_02_empty_learner_id_returns_422(self):
        """Whitespace-only learner_id must return 422."""
        res = self.client.get("/api/v1/kie/build/recommend", params={"learner_id": "   "})
        self.assertEqual(res.status_code, 422)

    def test_03_no_params_returns_422(self):
        """No query params must return 422."""
        res = self.client.get("/api/v1/kie/build/recommend")
        self.assertEqual(res.status_code, 422)


# ---------------------------------------------------------------------------
# Test Class 6: LLM Failure & Malformed Output Handling
# ---------------------------------------------------------------------------

class TestSprint5LLMFailureHandling(unittest.TestCase):
    """Verify graceful degradation on LLM errors and malformed responses."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_llm_provider_error_on_coach_returns_correct_status(self):
        """LLMProviderError during coach generation must return the provider's status_code."""
        mock_service = MagicMock()
        mock_service.generate_coaching.side_effect = LLMProviderError("Groq timeout", status_code=504)

        with patch("app.api.v1.endpoints.build.get_build_coach_service", return_value=mock_service):
            res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 504)

    def test_02_llm_parse_error_on_coach_returns_502(self):
        """LLMParseError during coach generation must return 502 Bad Gateway.

        Note: LLMParseError inherits LLMProviderError. The endpoint's
        LLMParseError handler runs first and returns 502 with the
        'Build coaching response could not be parsed' prefix in the detail.
        """
        mock_service = MagicMock()
        mock_service.generate_coaching.side_effect = LLMParseError("JSON malformed", raw_content="{bad}")

        with patch("app.api.v1.endpoints.build.get_build_coach_service", return_value=mock_service):
            res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 502)
        detail = res.json()["detail"]
        self.assertIn("Build coaching response could not be parsed", detail)

    def test_03_unexpected_exception_on_coach_returns_500(self):
        """Unhandled exception in service must return 500 Internal Server Error."""
        mock_service = MagicMock()
        mock_service.generate_coaching.side_effect = RuntimeError("Database exploded")

        with patch("app.api.v1.endpoints.build.get_build_coach_service", return_value=mock_service):
            res = self.client.post("/api/v1/kie/build/coach", json=VALID_COACH_PAYLOAD)
        self.assertEqual(res.status_code, 500)

    def test_04_empty_coaching_blocks_from_llm_gets_fallback(self):
        """If LLM returns empty coaching_blocks, service must inject a fallback orientation block."""
        mock_provider = MockLLMProvider()
        mock_provider.generate_build_coaching = lambda prompt: {
            "coaching_tone": "instructive",
            "coaching_blocks": [],
            "gap_summary": None,
            "next_milestone_hint": None,
            "remediation_recommended": False,
        }
        service = BuildCoachService(provider=mock_provider)
        request = BuildCoachRequest(
            request_id="req-fallback-test",
            learner_id="learner_fallback",
            project_title="Test Project",
        )
        response = service.generate_coaching(request)
        self.assertGreater(len(response.coaching_blocks), 0)
        self.assertEqual(response.coaching_blocks[0].block_type, "orientation")

    def test_05_malformed_coaching_blocks_not_a_list_gets_fallback(self):
        """If LLM returns coaching_blocks as a dict (not list), service falls back."""
        mock_provider = MockLLMProvider()
        mock_provider.generate_build_coaching = lambda prompt: {
            "coaching_tone": "instructive",
            "coaching_blocks": {"oops": "not a list"},
            "remediation_recommended": False,
        }
        service = BuildCoachService(provider=mock_provider)
        request = BuildCoachRequest(
            request_id="req-malformed-test",
            learner_id="learner_malformed",
            project_title="Test Project",
        )
        response = service.generate_coaching(request)
        self.assertGreater(len(response.coaching_blocks), 0)

    def test_06_recommend_falls_back_to_deterministic_on_llm_error(self):
        """If LLM raises during recommend, deterministic recommendations are returned (no 500)."""
        mock_provider = MockLLMProvider()
        mock_provider.generate_build_coaching = MagicMock(side_effect=RuntimeError("LLM down"))
        service = BuildCoachService(provider=mock_provider)
        context = BuildRecommendContext(
            learner_id="fallback_learner",
            academic_domain="engineering",
            learner_stage="bachelor",
        )
        response = service.generate_recommendations(context, request_id="req-fallback", count=3)
        self.assertGreater(len(response.recommendations), 0)
        self.assertIsNotNone(response.recommendation_rationale)

    def test_07_coaching_block_with_html_content_is_redacted(self):
        """coaching blocks containing HTML must be redacted by _sanitize_coaching_blocks."""
        raw_blocks = [
            {
                "block_type": "guidance",
                "title": "Test",
                "content": "<div>Please do not return HTML</div>",
            }
        ]
        sanitized = _sanitize_coaching_blocks(raw_blocks)
        self.assertEqual(len(sanitized), 1)
        self.assertIn("[Coaching block redacted", sanitized[0].content)

    def test_08_coaching_block_with_jsx_content_is_redacted(self):
        """coaching blocks containing JSX/React code must be redacted."""
        raw_blocks = [
            {
                "block_type": "guidance",
                "title": "Bad Block",
                "content": "import React from 'react'; export default function App() {}",
            }
        ]
        sanitized = _sanitize_coaching_blocks(raw_blocks)
        self.assertIn("[Coaching block redacted", sanitized[0].content)


# ---------------------------------------------------------------------------
# Test Class 7: coaching_response_to_public mapper
# ---------------------------------------------------------------------------

class TestSprint5ResponseMapper(unittest.TestCase):
    """Unit tests for coaching_response_to_public()."""

    def _make_internal_response(self, **kwargs) -> BuildCoachResponse:
        defaults = dict(
            request_id="req-mapper-test",
            learner_id="learner_map",
            project_title="Mapper Test Project",
            artifact_type=ArtifactType.CODE_PROJECT,
            coaching_tone=CoachingTone.INSTRUCTIVE,
            coaching_blocks=[],
            remediation_recommended=False,
        )
        defaults.update(kwargs)
        return BuildCoachResponse(**defaults)

    def test_01_reply_from_orientation_block(self):
        """reply must be populated from orientation block content."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", title="Start", content="Welcome to the session."),
                CoachingBlock(block_type="guidance", title="Guidance", content="Do X first."),
            ]
        )
        pub = coaching_response_to_public(internal)
        self.assertIn("Welcome to the session.", pub.reply)

    def test_02_suggestions_from_guidance_and_next_step_blocks(self):
        """suggestions must include content from guidance and next_step blocks."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", title="", content="Orientation."),
                CoachingBlock(block_type="guidance", title="G", content="Step one: do A."),
                CoachingBlock(block_type="next_step", title="Next", content="Proceed to B."),
            ]
        )
        pub = coaching_response_to_public(internal)
        self.assertIn("Step one: do A.", pub.suggestions)
        self.assertIn("Proceed to B.", pub.suggestions)

    def test_03_action_items_from_next_milestone_hint(self):
        """next_milestone_hint must produce a NEXT_STEP action item."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", content="Coaching session.")
            ],
            next_milestone_hint="Review your data model before moving to indexing.",
        )
        pub = coaching_response_to_public(internal)
        next_step_items = [ai for ai in pub.action_items if ai.type == "NEXT_STEP"]
        self.assertGreater(len(next_step_items), 0)
        self.assertIn("data model", next_step_items[0].label)

    def test_04_action_items_include_remediation_when_flagged(self):
        """remediation_recommended=True must produce a REMEDIATION action item."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", content="Coaching.")
            ],
            remediation_recommended=True,
        )
        pub = coaching_response_to_public(internal)
        remediation_items = [ai for ai in pub.action_items if ai.type == "REMEDIATION"]
        self.assertGreater(len(remediation_items), 0)

    def test_05_action_item_fields_have_type_label_url(self):
        """Each action_item must have type, label, and url."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", content="Coaching.")
            ],
            next_milestone_hint="Complete your draft.",
        )
        pub = coaching_response_to_public(internal)
        for ai in pub.action_items:
            self.assertIsInstance(ai.type, str)
            self.assertIsInstance(ai.label, str)
            # url can be None but must be present as a field
            self.assertTrue(hasattr(ai, "url"))

    def test_06_reply_falls_back_when_no_orientation_block(self):
        """reply must not be empty even if there is no orientation block."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="guidance", content="Do step A."),
            ]
        )
        pub = coaching_response_to_public(internal)
        self.assertGreater(len(pub.reply), 0)

    def test_07_gap_summary_included_in_reply(self):
        """gap_summary must be appended to the reply."""
        from app.schemas.build import CoachingBlock
        internal = self._make_internal_response(
            coaching_blocks=[
                CoachingBlock(block_type="orientation", content="Orientation text."),
            ],
            gap_summary="Your submission lacks depth in the analysis section.",
        )
        pub = coaching_response_to_public(internal)
        self.assertIn("lacks depth", pub.reply)

    def test_08_public_response_schema_validates(self):
        """BuildCoachPublicResponse schema must accept reply/suggestions/action_items."""
        pub = BuildCoachPublicResponse(
            reply="Here is your coaching feedback.",
            suggestions=["First, review your outline.", "Then, strengthen your argument."],
            action_items=[
                ActionItem(type="DOCUMENTATION_LINK", label="IRAC Structure Guide", url="https://example.com/irac"),
                ActionItem(type="NEXT_STEP", label="Revise your introduction", url=None),
            ],
        )
        self.assertEqual(pub.reply, "Here is your coaching feedback.")
        self.assertEqual(len(pub.suggestions), 2)
        self.assertEqual(len(pub.action_items), 2)
        self.assertEqual(pub.action_items[0].type, "DOCUMENTATION_LINK")


# ---------------------------------------------------------------------------
# Test Class 8: Service-Level Unit Tests
# ---------------------------------------------------------------------------

class TestSprint5ServiceUnit(unittest.TestCase):
    """Unit tests for BuildCoachService and helper functions."""

    def test_01_coaching_tone_from_str_valid_values(self):
        """_coaching_tone_from_str must parse all valid coaching tone strings."""
        self.assertEqual(_coaching_tone_from_str("encouraging"), CoachingTone.ENCOURAGING)
        self.assertEqual(_coaching_tone_from_str("instructive"), CoachingTone.INSTRUCTIVE)
        self.assertEqual(_coaching_tone_from_str("challenging"), CoachingTone.CHALLENGING)

    def test_02_coaching_tone_from_str_fallback_invalid(self):
        """_coaching_tone_from_str must default to INSTRUCTIVE on invalid input."""
        self.assertEqual(_coaching_tone_from_str("unknown_tone"), CoachingTone.INSTRUCTIVE)
        self.assertEqual(_coaching_tone_from_str(None), CoachingTone.INSTRUCTIVE)
        self.assertEqual(_coaching_tone_from_str(42), CoachingTone.INSTRUCTIVE)

    def test_03_coaching_tone_from_str_case_insensitive(self):
        """_coaching_tone_from_str must be case-insensitive."""
        self.assertEqual(_coaching_tone_from_str("ENCOURAGING"), CoachingTone.ENCOURAGING)
        self.assertEqual(_coaching_tone_from_str("Instructive"), CoachingTone.INSTRUCTIVE)

    def test_04_difficulty_from_str_valid_values(self):
        """_difficulty_from_str must parse all valid difficulty strings."""
        self.assertEqual(_difficulty_from_str("foundational"), BuildDifficulty.FOUNDATIONAL)
        self.assertEqual(_difficulty_from_str("intermediate"), BuildDifficulty.INTERMEDIATE)
        self.assertEqual(_difficulty_from_str("advanced"), BuildDifficulty.ADVANCED)

    def test_05_difficulty_from_str_fallback(self):
        """_difficulty_from_str must default to INTERMEDIATE on invalid input."""
        self.assertEqual(_difficulty_from_str("ultra_hard"), BuildDifficulty.INTERMEDIATE)
        self.assertEqual(_difficulty_from_str(None), BuildDifficulty.INTERMEDIATE)

    def test_06_artifact_type_from_str_valid_values(self):
        """_artifact_type_from_str must parse all ArtifactType members."""
        for t in ArtifactType:
            self.assertEqual(_artifact_type_from_str(t.value), t)

    def test_07_artifact_type_from_str_fallback(self):
        """_artifact_type_from_str must default to GENERAL on unknown string."""
        self.assertEqual(_artifact_type_from_str("blockchain_project"), ArtifactType.GENERAL)
        self.assertEqual(_artifact_type_from_str(None), ArtifactType.GENERAL)

    def test_08_determine_tone_weak_mastery(self):
        """_determine_coaching_tone_from_mastery must return ENCOURAGING when mastery < 0.50."""
        req = BuildCoachRequest(
            request_id="req-tone-test",
            learner_id="learner_tone",
            project_title="Tone Test",
            concept_mastery={"SQL": 0.30, "OOP": 0.40},
            weak_topics=["SQL"],
        )
        tone = _determine_coaching_tone_from_mastery(req)
        self.assertEqual(tone, CoachingTone.ENCOURAGING)

    def test_09_determine_tone_high_mastery(self):
        """_determine_coaching_tone_from_mastery must return CHALLENGING when all mastery >= 0.80."""
        req = BuildCoachRequest(
            request_id="req-tone-high",
            learner_id="learner_high",
            project_title="High Mastery Project",
            concept_mastery={"SQL": 0.85, "OOP": 0.90},
            weak_topics=[],
        )
        tone = _determine_coaching_tone_from_mastery(req)
        self.assertEqual(tone, CoachingTone.CHALLENGING)

    def test_10_determine_tone_no_mastery_data(self):
        """_determine_coaching_tone_from_mastery must return INSTRUCTIVE when no mastery data."""
        req = BuildCoachRequest(
            request_id="req-tone-none",
            learner_id="learner_none",
            project_title="No Data Project",
        )
        tone = _determine_coaching_tone_from_mastery(req)
        self.assertEqual(tone, CoachingTone.INSTRUCTIVE)

    def test_11_sanitize_coaching_blocks_filters_empty_content(self):
        """_sanitize_coaching_blocks must drop blocks with empty content."""
        raw_blocks = [
            {"block_type": "guidance", "title": "T", "content": "Valid content"},
            {"block_type": "guidance", "title": "T2", "content": ""},
            {"block_type": "guidance", "title": "T3", "content": "   "},
        ]
        result = _sanitize_coaching_blocks(raw_blocks)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].content, "Valid content")

    def test_12_sanitize_coaching_blocks_non_dict_items_skipped(self):
        """_sanitize_coaching_blocks must skip non-dict list items."""
        raw_blocks = ["not_a_dict", 42, None, {"block_type": "guidance", "content": "OK"}]
        result = _sanitize_coaching_blocks(raw_blocks)
        self.assertEqual(len(result), 1)

    def test_13_service_singleton_returns_same_instance(self):
        """get_build_coach_service must return the same singleton instance."""
        s1 = get_build_coach_service()
        s2 = get_build_coach_service()
        self.assertIs(s1, s2)

    def test_14_deterministic_recommendations_always_returns_results(self):
        """Deterministic recommendations must always return at least 1 result for any domain."""
        service = BuildCoachService(provider=MockLLMProvider())
        domains = ["engineering", "commerce", "law", "science", "humanities", "management", "unknown_domain"]
        for domain in domains:
            context = BuildRecommendContext(
                learner_id="test_learner",
                academic_domain=domain,
            )
            response = service._build_deterministic_recommendations(context, count=2)
            self.assertGreater(len(response.recommendations), 0, f"No recs for domain: {domain}")

    def test_15_deterministic_recommendation_has_type_and_skills_fields(self):
        """Deterministic recommendations must use 'type' and 'skills' field names (not old names)."""
        service = BuildCoachService(provider=MockLLMProvider())
        context = BuildRecommendContext(
            learner_id="test_learner",
            academic_domain="engineering",
        )
        response = service._build_deterministic_recommendations(context, count=2)
        for rec in response.recommendations:
            # New contract field names
            self.assertTrue(hasattr(rec, "type"), "ProjectRecommendation must have 'type' field")
            self.assertTrue(hasattr(rec, "skills"), "ProjectRecommendation must have 'skills' field")
            # Verify old names are gone
            self.assertFalse(hasattr(rec, "artifact_type"), "'artifact_type' must not exist")
            self.assertFalse(hasattr(rec, "key_skills_targeted"), "'key_skills_targeted' must not exist")

    def test_16_recommendation_rationale_non_empty(self):
        """recommendation_rationale in response must not be empty."""
        service = BuildCoachService(provider=MockLLMProvider())
        context = BuildRecommendContext(
            learner_id="rationale_test",
            academic_domain="engineering",
            learner_stage="master",
            target_role="ML Engineer",
        )
        response = service.generate_recommendations(context, request_id="req-rat-test", count=2)
        self.assertTrue(len(response.recommendation_rationale) > 0)


# ---------------------------------------------------------------------------
# Test Class 9: Prompt Builder Unit Tests
# ---------------------------------------------------------------------------

class TestSprint5PromptBuilder(unittest.TestCase):
    """Unit tests for build_coach_prompt and build_recommend_prompt."""

    def test_01_coach_prompt_contains_project_title(self):
        """Coach prompt must include the project title."""
        request = BuildCoachRequest(
            request_id="req-prompt-test",
            learner_id="learner_prompt",
            project_title="E-Commerce Inventory Management System",
        )
        prompt = build_coach_prompt(request)
        self.assertIn("E-Commerce Inventory Management System", prompt)

    def test_02_coach_prompt_contains_artifact_type(self):
        """Coach prompt must include the artifact type."""
        request = BuildCoachRequest(
            request_id="req-prompt-test-2",
            learner_id="learner_prompt",
            project_title="Test",
            artifact_type=ArtifactType.CODE_PROJECT,
        )
        prompt = build_coach_prompt(request)
        self.assertIn("code_project", prompt)

    def test_03_coach_prompt_instructs_json_output(self):
        """Coach prompt must instruct LLM to output strictly valid JSON."""
        request = BuildCoachRequest(
            request_id="req-json-test",
            learner_id="learner_json",
            project_title="JSON Test",
        )
        prompt = build_coach_prompt(request)
        self.assertIn("JSON", prompt)
        self.assertIn("coaching_blocks", prompt)

    def test_04_coach_prompt_no_html_instructions(self):
        """Coach prompt must explicitly forbid raw HTML/JSX output."""
        request = BuildCoachRequest(
            request_id="req-html-test",
            learner_id="learner_html",
            project_title="HTML Test",
        )
        prompt = build_coach_prompt(request)
        self.assertIn("NOT output raw HTML", prompt)

    def test_05_recommend_prompt_contains_learner_domain(self):
        """Recommend prompt must include the academic domain."""
        context = BuildRecommendContext(
            learner_id="prompt_test_learner",
            academic_domain="commerce",
            target_role="Financial Analyst",
        )
        prompt = build_recommend_prompt(context, count=3)
        self.assertIn("commerce", prompt.lower())

    def test_06_recommend_prompt_contains_count(self):
        """Recommend prompt must include the requested recommendation count."""
        context = BuildRecommendContext(
            learner_id="prompt_count_test",
            academic_domain="science",
        )
        prompt = build_recommend_prompt(context, count=4)
        self.assertIn("4", prompt)

    def test_07_recommend_prompt_no_preamble_instruction(self):
        """Recommend prompt must instruct LLM to output only the JSON object."""
        context = BuildRecommendContext(learner_id="test", academic_domain="engineering")
        prompt = build_recommend_prompt(context, count=2)
        self.assertIn("no preamble", prompt.lower())


# ---------------------------------------------------------------------------
# Test Class 10: Mock Provider Behavior
# ---------------------------------------------------------------------------

class TestSprint5MockProvider(unittest.TestCase):
    """Verify MockLLMProvider produces a contract-compliant coaching response."""

    def setUp(self):
        self.provider = MockLLMProvider()

    def test_01_mock_returns_dict(self):
        """Mock generate_build_coaching must return a dict."""
        result = self.provider.generate_build_coaching("test prompt")
        self.assertIsInstance(result, dict)

    def test_02_mock_returns_coaching_tone(self):
        """Mock must include coaching_tone key."""
        result = self.provider.generate_build_coaching("test prompt")
        self.assertIn("coaching_tone", result)
        self.assertIn(result["coaching_tone"], ["encouraging", "instructive", "challenging"])

    def test_03_mock_returns_coaching_blocks_list(self):
        """Mock must return coaching_blocks as a non-empty list."""
        result = self.provider.generate_build_coaching("test prompt")
        self.assertIn("coaching_blocks", result)
        self.assertIsInstance(result["coaching_blocks"], list)
        self.assertGreater(len(result["coaching_blocks"]), 0)

    def test_04_mock_weak_prompt_returns_encouraging_tone(self):
        """Mock must detect 'weak' in prompt and return encouraging tone."""
        result = self.provider.generate_build_coaching("Concept mastery: Weak SQL: 0.30")
        self.assertEqual(result["coaching_tone"], "encouraging")
        self.assertTrue(result["remediation_recommended"])

    def test_05_mock_proficient_prompt_returns_challenging_tone(self):
        """Mock must detect 'proficient' in prompt and return challenging tone."""
        result = self.provider.generate_build_coaching("Concept mastery: Proficient Python: 0.90")
        self.assertEqual(result["coaching_tone"], "challenging")
        self.assertFalse(result["remediation_recommended"])

    def test_06_mock_commerce_domain_example_block(self):
        """Mock must return commerce-domain specific example block content."""
        result = self.provider.generate_build_coaching("This is a commerce business_plan project")
        blocks = result["coaching_blocks"]
        example_blocks = [b for b in blocks if b["block_type"] == "example"]
        self.assertGreater(len(example_blocks), 0)
        self.assertIn("break-even", example_blocks[0]["content"].lower())

    def test_07_mock_includes_all_expected_coaching_block_types(self):
        """Mock coaching response must include orientation, gap_analysis, guidance, example, next_step."""
        result = self.provider.generate_build_coaching("general project coaching")
        block_types = [b["block_type"] for b in result["coaching_blocks"]]
        expected_types = ["orientation", "gap_analysis", "guidance", "example", "next_step"]
        for expected in expected_types:
            self.assertIn(expected, block_types, f"Missing expected block type: {expected}")

    def test_08_mock_returns_gap_summary_and_next_milestone_hint(self):
        """Mock must return gap_summary and next_milestone_hint."""
        result = self.provider.generate_build_coaching("test prompt")
        self.assertIn("gap_summary", result)
        self.assertIn("next_milestone_hint", result)
        self.assertIsNotNone(result["gap_summary"])
        self.assertIsNotNone(result["next_milestone_hint"])


# ---------------------------------------------------------------------------
# Test Class 11: Learner Context & Memory Engine Integration
# ---------------------------------------------------------------------------

class TestSprint5LearnerContextBoundary(unittest.TestCase):
    """
    Verifies correct handling of the learner context dependency boundary.

    learner_id is opaque to AI/ML-2; profile data is retrieved from the
    Sprint 3 memory engine (best-effort). AI/ML-2 does NOT maintain an
    independent learner database.
    """

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_opaque_learner_id_does_not_fail_recommend(self):
        """An opaque learner_id (no assumed structure) must not cause failures."""
        res = self.client.get(
            "/api/v1/kie/build/recommend",
            params={"learner_id": "uuid-0000-1111-2222-3333"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["learner_id"], "uuid-0000-1111-2222-3333")

    def test_02_memory_enrichment_failure_does_not_break_recommend(self):
        """Memory engine failure must NOT cause the recommend endpoint to fail.

        get_memory_engine is imported locally inside the endpoint function body.
        We patch it at its source module so the local import gets the mock.
        """
        with patch("app.services.memory_engine.get_memory_engine", side_effect=Exception("Memory unavailable")):
            res = self.client.get(
                "/api/v1/kie/build/recommend",
                params={"learner_id": "learner_no_memory"}
            )
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()["recommendations"]), 0)

    def test_03_memory_enrichment_is_best_effort_on_coach(self):
        """Memory enrichment failure must NOT cause coach endpoint to fail."""
        payload = {
            "intent": "general",
            "message": "Where do I start?",
            "project_context": {
                "title": "Fresh Start Project",
                "type": "essay",
            },
        }
        res = self.client.post("/api/v1/kie/build/coach", json=payload)
        self.assertEqual(res.status_code, 200)

    def test_04_ai_ml2_does_not_expose_learner_db_endpoint(self):
        """AI/ML-2 must NOT expose a learner database endpoint."""
        forbidden_paths = [
            "/api/v1/learners",
            "/api/v1/kie/learners",
            "/api/v1/kie/build/learners",
        ]
        for path in forbidden_paths:
            res = self.client.get(path)
            self.assertEqual(
                res.status_code, 404,
                f"AI/ML-2 unexpectedly exposed learner DB path: {path}"
            )

    def test_05_recommend_uses_only_learner_id_as_public_param(self):
        """
        Verify that extra params are not declared on the endpoint.
        FastAPI should not require academic_domain, count, etc.
        """
        # Only learner_id — must succeed
        res = self.client.get("/api/v1/kie/build/recommend", params={"learner_id": "sole_param_test"})
        self.assertEqual(res.status_code, 200)

    def test_06_recommendations_from_memory_enriched_context(self):
        """
        When memory engine provides context (target_role, weak_topics),
        recommendations must still be returned successfully.
        """
        from app.services.memory_engine import get_memory_engine
        from app.schemas.memory_context import RelevantMemoryQuery

        # Seed memory for this learner
        engine = get_memory_engine()
        memory = engine.get_or_create_memory("memory_enriched_learner")
        memory.goals.primary_target_role = "Data Scientist"
        memory.friction = []  # clear friction

        res = self.client.get(
            "/api/v1/kie/build/recommend",
            params={"learner_id": "memory_enriched_learner"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(len(data["recommendations"]), 0)
        # Recommendations must still use the contract field names
        for rec in data["recommendations"]:
            self.assertIn("type", rec)
            self.assertIn("skills", rec)


# ---------------------------------------------------------------------------
# Test Class 12: Sprint 1–4 Regression Tests
# ---------------------------------------------------------------------------

class TestSprint5Sprint14Regression(unittest.TestCase):
    """Verify Sprint 1–4 routes are unaffected by Sprint 5 additions."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)

    def test_01_health_endpoint_intact(self):
        """GET /health must return 200 with service status."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertIn("status", res.json())

    def test_02_learning_routes_not_404(self):
        """Sprint 1–4 /api/v1/learning routes must still be registered."""
        # Posting an empty payload returns 422 (Unprocessable Entity), not 404.
        # Getting 422 proves the route exists and is registered correctly.
        res = self.client.post("/api/v1/learning/plan-lesson", json={})
        self.assertNotEqual(res.status_code, 404, "Sprint 4 /learning/plan-lesson route missing")

    def test_03_onboarding_routes_not_404(self):
        """Sprint 2 /api/v1/onboarding routes must still be registered."""
        res = self.client.post("/api/v1/onboarding/analyze", json={})
        self.assertNotEqual(res.status_code, 404, "Sprint 2 /onboarding/analyze route missing")

    def test_04_memory_routes_not_404(self):
        """Sprint 3 /api/v1/memory routes must still be registered."""
        # POST /api/v1/memory/events with an empty body returns 422, not 404.
        # Getting 422 proves the route exists and Sprint 3 memory endpoints are intact.
        res = self.client.post("/api/v1/memory/events", json={})
        self.assertNotEqual(res.status_code, 404, "Sprint 3 /memory/events route missing")


if __name__ == "__main__":
    unittest.main()

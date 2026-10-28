"""
Sprint 7 — Career API Routes & Integration Tests (AI/ML-2 KIE)
Phase 4: API Routes & Integration

Coverage:
  - Exact documented path registration:
      POST /api/v1/kie/career/resume/generate
      POST /api/v1/kie/career/ats/analyze
  - Valid resume generation response envelope (200 OK)
  - Valid ATS analysis response envelope (200 OK)
  - Missing or invalid required fields return HTTP 422
  - Provider failure status code mappings:
      HTTP 429: LLM provider rate limit exceeded
      HTTP 502: LLM provider unavailable or malformed response
      HTTP 504: LLM provider connection timeout
      HTTP 500: Unexpected internal exception
  - Deterministic score boundary and original finding IDs preserved
  - Anti-hallucination contact protection and entry ID preservation
  - FastAPI dependency injection override capability
  - Zero live LLM calls or external network access
  - Sprint 1–5 regression route integrity
"""

import copy
import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.schemas.career import (
    ATSAnalyzeResponse,
    ResumeDraft,
    ResumeGenerateResponse,
)
from app.services.career_service import get_career_service
from app.services.llm_provider import LLMParseError, LLMProviderError


# ---------------------------------------------------------------------------
# Canonical Test Payloads (from launch_aiml_integration_guide.md)
# ---------------------------------------------------------------------------

CANONICAL_RESUME_REQUEST_PAYLOAD = {
    "request_id": "1c9a9189-3cb4-4b25-a053-467c1c0777d1",
    "learner_id": "00000000-0000-0000-0000-000000000002",
    "title": "Senior Cloud Backend Engineer",
    "source": "profile",
    "preferences": {
        "targetRole": "Backend Systems Architect",
        "tone": "professional",
    },
    "content": {
        "contact": {
            "fullName": "Jordan Lee",
            "email": "jordan.lee@example.com",
            "phone": "+1-415-555-0199",
            "location": "San Francisco, CA",
            "linkedInUrl": "https://linkedin.com/in/jordanlee",
            "githubUrl": "https://github.com/jordanlee",
            "portfolioUrl": "https://jordanlee.dev",
        },
        "headline": "Software Engineer",
        "summary": "Software engineer with backend experience.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "education": [
            {
                "id": "e8a93144-88ab-448c-9c98-cfba0c6fa4d2",
                "institution": "University of California, Berkeley",
                "degree": "B.S. in Computer Science",
                "fieldOfStudy": "Distributed Systems",
                "startDate": "2020",
                "endDate": "2024",
                "grade": "3.85 GPA",
            }
        ],
        "experience": [
            {
                "id": "3e9b1d07-2a4e-4f05-87cc-98836171f201",
                "company": "Acme Cloud Corp",
                "role": "Software Engineering Intern",
                "location": "San Francisco, CA",
                "startDate": "2023-06",
                "endDate": "2023-09",
                "isCurrent": False,
                "description": "Worked on backend APIs. Handled database queries and optimized performance.",
            }
        ],
        "projects": [
            {
                "id": "d61b34e5-9c8a-4d22-9cb7-789a456123ef",
                "name": "Distributed Task Scheduler",
                "description": "Background task worker queue with priority routing.",
                "technologies": ["Python", "Redis", "Docker"],
                "projectUrl": "https://github.com/jordanlee/scheduler",
                "startDate": "2024-01",
                "endDate": "2024-04",
            }
        ],
        "achievements": [
            {
                "id": "f51c78a9-4b2e-49cd-90ef-123456789abc",
                "title": "AWS Certified Solutions Architect",
                "description": "Validated expertise in distributed cloud systems.",
                "date": "2024-05",
            }
        ],
    },
    "career_context": {
        "learner_id": "00000000-0000-0000-0000-000000000002",
        "learner": {
            "primary_goal": "Become a Principal Cloud Architect",
            "skills": ["Python", "FastAPI", "Go", "Docker", "PostgreSQL"],
            "experience": "Worked on backend APIs. Handled database queries and optimized performance.",
        },
        "education": {
            "university": "University of California, Berkeley",
            "degree_program": "B.S. in Computer Science",
            "domain": "Distributed Systems",
            "academic_status": "Graduated",
        },
        "career_readiness": {
            "projects": [
                {
                    "id": "b0a1c2d3-0001-4000-8000-000000000001",
                    "title": "High-Throughput Microservice",
                    "description": "Built resilient async event pipeline handling 100k msg/sec.",
                    "skills": ["Python", "Redis", "FastAPI"],
                    "status": "COMPLETED",
                }
            ],
            "evidence": [
                {
                    "id": "ev-001",
                    "title": "Query Latency Reduction",
                    "description": "Decreased p99 database query response latency by 42%.",
                    "skills": ["PostgreSQL", "Database Indexing"],
                }
            ],
            "mastery": [
                {
                    "subject": "Computer Science",
                    "topic": "Distributed Consensus & Raft",
                    "mastery_score": 0.88,
                    "status": "MASTERED",
                }
            ],
        },
    },
}

CANONICAL_ATS_REQUEST_PAYLOAD = {
    "request_id": "2d8f99a0-1b2c-4e3d-9f0a-112233445566",
    "learner_id": "00000000-0000-0000-0000-000000000002",
    "document": {
        "fileName": "Jordan_Lee_Resume.pdf",
        "fileType": "pdf",
        "pageCount": 1,
        "extractedCharacterCount": 2150,
    },
    "extracted_text": "Jordan Lee\njordan.lee@example.com | San Francisco, CA\n\nSUMMARY\nSoftware Engineer with experience in Python and databases.\n\nEXPERIENCE\nAcme Cloud Corp - Intern\nWorked on backend APIs and helped with database.\n\nPROJECTS\nDistributed Task Scheduler\nBuilt an async task worker queue.\n\nEDUCATION\nUC Berkeley - B.S. in Computer Science\nGraduated 2024",
    "rule_score": {
        "value": 72.0,
        "maxValue": 100.0,
        "methodology": "defined-rule-based-checks",
        "methodologyVersion": "1.0",
    },
    "rule_findings": [
        {
            "id": "f1-contact",
            "category": "contact_information",
            "severity": "warning",
            "title": "Missing Phone Number",
            "description": "No reachable phone number was found.",
            "recommendation": "Add a standardized phone number with area/country code so recruiters can contact you.",
        },
        {
            "id": "f2-metrics",
            "category": "missing_information",
            "severity": "warning",
            "title": "Few Quantifiable Impact Metrics",
            "description": "Found only 0 quantifiable data points or percentage improvements.",
            "recommendation": "Include specific numbers, scale indicators, and metrics.",
        },
        {
            "id": "f3-verbs",
            "category": "content",
            "severity": "warning",
            "title": "Low Action Verb Density",
            "description": "Detected only 2 distinct strong action verbs in your resume.",
            "recommendation": "Start bullet points with high-impact action verbs.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Test Suites
# ---------------------------------------------------------------------------

class TestSprint7CareerRoutes(unittest.TestCase):
    """Integration test suite for Sprint 7 Career API routes."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.client = TestClient(app)
        app.dependency_overrides.clear()

    def tearDown(self):
        app.dependency_overrides.clear()

    # -----------------------------------------------------------------------
    # Route Registration & Happy Path
    # -----------------------------------------------------------------------

    def test_01_resume_generate_route_registered_at_exact_path(self):
        """POST /api/v1/kie/career/resume/generate must return HTTP 200 (not 404)."""
        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=CANONICAL_RESUME_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("content", data)
        self.assertIn("headline", data["content"])
        self.assertIn("summary", data["content"])
        self.assertIn("skills", data["content"])

    def test_02_ats_analyze_route_registered_at_exact_path(self):
        """POST /api/v1/kie/career/ats/analyze must return HTTP 200 (not 404)."""
        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=CANONICAL_ATS_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertIn("findings", data)
        self.assertTrue(len(data["findings"]) > 0)

    # -----------------------------------------------------------------------
    # Envelope & Contract Validation
    # -----------------------------------------------------------------------

    def test_03_resume_response_envelope_matches_documented_contract(self):
        """Resume response must match Section 3.4 of launch_aiml_integration_guide.md."""
        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=CANONICAL_RESUME_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        parsed = ResumeGenerateResponse.model_validate(response.json())
        self.assertIsInstance(parsed.content, ResumeDraft)
        self.assertEqual(parsed.content.contact.full_name, "Jordan Lee")
        self.assertTrue(len(parsed.content.skills) > 0)

    def test_04_ats_response_envelope_matches_documented_contract(self):
        """ATS response must match Section 4.4 of launch_aiml_integration_guide.md."""
        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=CANONICAL_ATS_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        parsed = ATSAnalyzeResponse.model_validate(response.json())
        self.assertTrue(len(parsed.summary) > 10)
        # Verify original finding IDs are strictly preserved
        finding_ids = [f.id for f in parsed.findings]
        self.assertIn("f1-contact", finding_ids)
        self.assertIn("f2-metrics", finding_ids)
        self.assertIn("f3-verbs", finding_ids)

    # -----------------------------------------------------------------------
    # Input Validation (HTTP 422)
    # -----------------------------------------------------------------------

    def test_05_resume_missing_required_fields_returns_422(self):
        """Missing request_id, learner_id, or content must return HTTP 422."""
        invalid_payload = copy.deepcopy(CANONICAL_RESUME_REQUEST_PAYLOAD)
        invalid_payload.pop("request_id")

        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=invalid_payload,
        )
        self.assertEqual(response.status_code, 422)

    def test_06_ats_missing_required_fields_returns_422(self):
        """Missing extracted_text or rule_score must return HTTP 422."""
        invalid_payload = copy.deepcopy(CANONICAL_ATS_REQUEST_PAYLOAD)
        invalid_payload.pop("extracted_text")

        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=invalid_payload,
        )
        self.assertEqual(response.status_code, 422)

    def test_07_ats_invalid_rule_score_boundary_returns_422(self):
        """Rule score > 100 must fail schema validation and return HTTP 422."""
        invalid_payload = copy.deepcopy(CANONICAL_ATS_REQUEST_PAYLOAD)
        invalid_payload["rule_score"]["value"] = 150.0

        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=invalid_payload,
        )
        self.assertEqual(response.status_code, 422)

    # -----------------------------------------------------------------------
    # Error Mappings (HTTP 429, 502, 504, 500)
    # -----------------------------------------------------------------------

    def test_08_provider_rate_limit_maps_to_429(self):
        """Provider rate limit error must map to HTTP 429."""
        mock_service = MagicMock()
        mock_service.generate_resume.side_effect = LLMProviderError(
            "Groq API rate limit exceeded (HTTP 429).", status_code=429
        )

        app.dependency_overrides[get_career_service] = lambda: mock_service

        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=CANONICAL_RESUME_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 429)

    def test_09_provider_timeout_maps_to_504(self):
        """Provider timeout error must map to HTTP 504."""
        mock_service = MagicMock()
        mock_service.analyze_ats.side_effect = LLMProviderError(
            "Groq API connection timeout failure.", status_code=504
        )

        app.dependency_overrides[get_career_service] = lambda: mock_service

        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=CANONICAL_ATS_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 504)

    def test_10_malformed_llm_output_maps_to_502(self):
        """Malformed LLM output must map to HTTP 502 Bad Gateway."""
        mock_service = MagicMock()
        mock_service.generate_resume.side_effect = LLMParseError(
            "Failed to parse LLM response as JSON.", status_code=502
        )

        app.dependency_overrides[get_career_service] = lambda: mock_service

        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=CANONICAL_RESUME_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 502)
        self.assertIn("Resume generation response could not be parsed", response.json()["detail"])

    def test_11_unexpected_service_exception_maps_to_500(self):
        """Unhandled exceptions must map to HTTP 500 Internal Server Error."""
        mock_service = MagicMock()
        mock_service.analyze_ats.side_effect = RuntimeError("Catastrophic runtime crash")

        app.dependency_overrides[get_career_service] = lambda: mock_service

        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=CANONICAL_ATS_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Unexpected internal error", response.json()["detail"])

    # -----------------------------------------------------------------------
    # Invariant Protection Across Endpoints
    # -----------------------------------------------------------------------

    def test_12_resume_missing_contact_details_preserved_as_null(self):
        """Missing phone/urls in request must remain null in API response."""
        payload = copy.deepcopy(CANONICAL_RESUME_REQUEST_PAYLOAD)
        payload["content"]["contact"]["phone"] = None
        payload["content"]["contact"]["portfolioUrl"] = None

        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=payload,
        )
        self.assertEqual(response.status_code, 200)
        contact = response.json()["content"]["contact"]
        self.assertIsNone(contact.get("portfolioUrl", contact.get("portfolio_url")))

    def test_13_resume_entry_ids_preserved_in_api_response(self):
        """Original entry IDs in education/experience must be preserved in API response."""
        response = self.client.post(
            "/api/v1/kie/career/resume/generate",
            json=CANONICAL_RESUME_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        content = response.json()["content"]
        if content.get("education"):
            self.assertEqual(content["education"][0]["id"], "e8a93144-88ab-448c-9c98-cfba0c6fa4d2")
        if content.get("experience"):
            self.assertEqual(content["experience"][0]["id"], "3e9b1d07-2a4e-4f05-87cc-98836171f201")

    def test_14_ats_score_and_finding_count_preserved(self):
        """ATS analysis preserves original finding count and does not expose altered score."""
        response = self.client.post(
            "/api/v1/kie/career/ats/analyze",
            json=CANONICAL_ATS_REQUEST_PAYLOAD,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["findings"]), 3)
        # Score is not in response schema
        self.assertNotIn("rule_score", data)

    # -----------------------------------------------------------------------
    # Regression Check for Existing Routes
    # -----------------------------------------------------------------------

    def test_15_health_check_endpoint_intact(self):
        """GET /health must remain functional."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_16_build_coach_route_intact(self):
        """POST /api/v1/kie/build/coach must remain functional and not 404."""
        build_payload = {
            "intent": "guidance",
            "message": "I am working on microservice architecture.",
            "context": "engineering student",
            "project_context": {
                "id": "proj_1",
                "title": "Cloud Ledger",
                "type": "code_project",
                "status": "in_progress",
                "skills": ["Architecture"],
            },
        }
        response = self.client.post("/api/v1/kie/build/coach", json=build_payload)
        self.assertEqual(response.status_code, 200)

    def test_17_learning_routes_intact(self):
        """POST /api/v1/learning/plan-lesson must remain registered and not 404."""
        response = self.client.post("/api/v1/learning/plan-lesson", json={})
        self.assertNotEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

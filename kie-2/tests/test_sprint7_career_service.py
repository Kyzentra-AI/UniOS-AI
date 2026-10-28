"""
Sprint 7 — Career Service Layer Tests (AI/ML-2 KIE)
Phase 3: Career Service Layer Implementation

Coverage:
  Resume Generation:
    - Successful generation with a valid structured response (dict, str, bytes).
    - Target-role and tone preferences reaching prompt builder.
    - Missing contact details remain null/missing rather than fabricated.
    - Malformed JSON handled safely (LLMParseError 502).
    - Invalid generated schema handled safely (LLMParseError 502).
    - Empty provider output handled safely (LLMParseError 502).
    - Provider exceptions follow existing error conventions (LLMProviderError).
    - API keys and sensitive credentials redacted from error messages.
    - Existing entry IDs and source data preserved.
    - Empty experience/education preserved (no fabricated credentials).

  ATS Analysis:
    - Successful generation of qualitative feedback.
    - Deterministic rule score and methodology remain unchanged.
    - Original finding IDs remain present.
    - Finding count and identity are preserved.
    - Malformed JSON and invalid schema handled safely.
    - Empty provider output and provider exceptions handled.
    - No live LLM calls occur during tests.
    - Service singleton consistency and method aliases.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from app.schemas.career import (
    ATSAnalyzeRequest,
    ATSAnalyzeResponse,
    ATSFindingSeverity,
    CareerContext,
    CareerContextEducation,
    CareerContextLearner,
    CareerReadiness,
    CareerReadinessProject,
    DocumentFileType,
    DocumentMetadata,
    ResumeAchievement,
    ResumeContact,
    ResumeDraft,
    ResumeEducation,
    ResumeExperience,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
    ResumePreferences,
    ResumeProject,
    ResumeSource,
    ResumeTone,
    RuleFinding,
    RuleScore,
)
from app.services.career_service import (
    CareerService,
    _sanitize_error_message,
    get_career_service,
)
from app.services.llm_provider import (
    LLMParseError,
    LLMProviderError,
    MockLLMProvider,
)


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

def create_valid_resume_request(
    target_role: str = "Senior Cloud Architect",
    tone: ResumeTone = ResumeTone.PROFESSIONAL,
    with_contact_details: bool = True,
    with_entries: bool = True,
) -> ResumeGenerateRequest:
    contact = ResumeContact(
        full_name="Alex Mercer",
        email="alex.mercer@example.com" if with_contact_details else None,
        phone="+1-555-0199" if with_contact_details else None,
        location="Austin, TX" if with_contact_details else None,
        linkedin_url="https://linkedin.com/in/alexmercer" if with_contact_details else None,
        github_url="https://github.com/alexmercer" if with_contact_details else None,
        portfolio_url="https://alexmercer.dev" if with_contact_details else None,
    )

    education = [
        ResumeEducation(
            id="edu-rec-001",
            institution="Georgia Tech",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            start_date="2018",
            end_date="2022",
            grade="3.9 GPA",
        )
    ] if with_entries else []

    experience = [
        ResumeExperience(
            id="exp-rec-001",
            company="Stripe",
            role="Backend Engineer",
            location="Remote",
            start_date="2022-01",
            end_date="2024-01",
            is_current=False,
            description="Engineered high-throughput payments microservices processing 20M events daily.",
        )
    ] if with_entries else []

    projects = [
        ResumeProject(
            id="proj-rec-001",
            name="Distributed Cache Cluster",
            description="Built custom distributed in-memory cache using Raft consensus.",
            technologies=["Go", "Raft", "gRPC"],
            project_url="https://github.com/alexmercer/cache-cluster",
        )
    ] if with_entries else []

    achievements = [
        ResumeAchievement(
            id="ach-rec-001",
            title="AWS Certified Solutions Architect - Professional",
            description="Achieved professional certification in high-availability cloud architecture.",
            date="2023-05",
        )
    ] if with_entries else []

    return ResumeGenerateRequest(
        request_id="11111111-1111-1111-1111-111111111111",
        learner_id="22222222-2222-2222-2222-222222222222",
        title="Senior Cloud Resume",
        source=ResumeSource.PROFILE,
        preferences=ResumePreferences(target_role=target_role, tone=tone),
        content=ResumeDraft(
            contact=contact,
            headline="Cloud Software Engineer",
            summary="Passionate software engineer experienced with distributed systems.",
            skills=["Python", "Go", "AWS", "Kubernetes", "PostgreSQL"],
            education=education,
            experience=experience,
            projects=projects,
            achievements=achievements,
        ),
        career_context=CareerContext(
            learner_id="22222222-2222-2222-2222-222222222222",
            learner=CareerContextLearner(
                primary_goal="Senior Cloud Architect",
                skills=["Cloud Architecture", "Distributed Systems"],
            ),
            education=CareerContextEducation(
                university="Georgia Tech",
                degree_program="B.S. in Computer Science",
            ),
            career_readiness=CareerReadiness(
                projects=[
                    CareerReadinessProject(
                        id="cr-proj-1",
                        title="Distributed Cache Cluster",
                        skills=["Go", "Raft"],
                    )
                ]
            ),
        ),
    )


def create_valid_ats_request(findings_count: int = 3) -> ATSAnalyzeRequest:
    findings = []
    for i in range(1, findings_count + 1):
        findings.append(
            RuleFinding(
                id=f"f{i}-rule-check",
                category=f"category_{i}",
                severity=ATSFindingSeverity.WARNING if i % 2 == 0 else ATSFindingSeverity.SUGGESTION,
                title=f"Rule Check Title {i}",
                description=f"Rule Check Description {i} explaining parsing concern.",
                recommendation=f"Rule Check Recommendation {i}.",
            )
        )

    return ATSAnalyzeRequest(
        request_id="33333333-3333-3333-3333-333333333333",
        learner_id="44444444-4444-4444-4444-444444444444",
        document=DocumentMetadata(
            file_name="alex_mercer_resume.pdf",
            file_type=DocumentFileType.PDF,
            page_count=2,
            extracted_character_count=4200,
        ),
        extracted_text="Alex Mercer. Software Engineer with expertise in distributed systems and cloud computing...",
        rule_score=RuleScore(
            value=84.5,
            max_value=100.0,
            methodology="defined-rule-based-checks",
            methodology_version="1.0",
        ),
        rule_findings=findings,
    )


# ---------------------------------------------------------------------------
# Test Suites
# ---------------------------------------------------------------------------

class TestCareerServiceResumeGeneration(unittest.TestCase):
    """Test suite for Resume Generation service layer operations."""

    def setUp(self):
        self.mock_provider = MockLLMProvider()
        self.service = CareerService(provider=self.mock_provider)

    def test_01_successful_resume_generation_with_mock_provider(self):
        """Resume generation must return a validated ResumeGenerateResponse."""
        req = create_valid_resume_request()
        resp = self.service.generate_resume(req)

        self.assertIsInstance(resp, ResumeGenerateResponse)
        self.assertIsInstance(resp.content, ResumeDraft)
        self.assertTrue(len(resp.content.skills) > 0)
        self.assertIsNotNone(resp.content.headline)
        self.assertIsNotNone(resp.content.summary)

    def test_02_preferences_reach_prompt_builder(self):
        """Target role and tone preferences must reach the prompt builder."""
        req = create_valid_resume_request(
            target_role="Principal Distributed Systems Engineer",
            tone=ResumeTone.CONCISE,
        )

        with patch("app.services.career_service.build_resume_generation_prompt") as mock_builder:
            # Return valid prompt structure for mock provider
            mock_builder.return_value = "You are the UniOS Career Intelligence Engine. Target Role: 'Principal Distributed Systems Engineer'"
            self.service.generate_resume(req)

            mock_builder.assert_called_once_with(req)

    def test_03_missing_contact_details_remain_null_rather_than_fabricated(self):
        """Missing phone, URLs, or location must remain null and not be fabricated."""
        req = create_valid_resume_request(with_contact_details=False)

        # Provider might attempt to hallucinate contact details
        hallucinating_provider = MagicMock()
        hallucinating_provider.generate_career_response.return_value = {
            "contact": {
                "fullName": "Alex Mercer",
                "email": "hallucinated.email@mock.com",
                "phone": "+1-999-000-1111",
                "location": "Fabricated City",
                "linkedInUrl": "https://linkedin.com/in/fake",
                "githubUrl": "https://github.com/fake",
                "portfolioUrl": "https://fake.dev",
            },
            "headline": "Elevated Headline",
            "summary": "Executive summary.",
            "skills": ["Python", "AWS"],
            "education": [],
            "experience": [],
            "projects": [],
            "achievements": [],
        }

        service = CareerService(provider=hallucinating_provider)
        resp = service.generate_resume(req)

        # Contact details not in original request MUST be null
        self.assertIsNone(resp.content.contact.phone)
        self.assertIsNone(resp.content.contact.email)
        self.assertIsNone(resp.content.contact.location)
        self.assertIsNone(resp.content.contact.linkedin_url)
        self.assertIsNone(resp.content.contact.github_url)
        self.assertIsNone(resp.content.contact.portfolio_url)

    def test_04_preserves_existing_entry_ids(self):
        """Education, experience, project, and achievement IDs must be preserved."""
        req = create_valid_resume_request(with_entries=True)

        # Provider returns items without IDs or with altered IDs
        mock_provider = MagicMock()
        mock_provider.generate_career_response.return_value = {
            "contact": {"fullName": "Alex Mercer"},
            "headline": "Elevated Headline",
            "summary": "Executive summary.",
            "skills": ["Python"],
            "education": [
                {
                    "institution": "Georgia Tech",
                    "degree": "B.S. Computer Science",
                }
            ],
            "experience": [
                {
                    "company": "Stripe",
                    "role": "Senior Engineer",
                    "description": "Architected payments pipeline.",
                }
            ],
            "projects": [
                {
                    "name": "Distributed Cache Cluster",
                    "description": "High performance cache.",
                    "technologies": ["Go"],
                }
            ],
            "achievements": [
                {
                    "title": "AWS Certified Solutions Architect",
                    "description": "Professional certificate.",
                }
            ],
        }

        service = CareerService(provider=mock_provider)
        resp = service.generate_resume(req)

        self.assertEqual(resp.content.education[0].id, "edu-rec-001")
        self.assertEqual(resp.content.experience[0].id, "exp-rec-001")
        self.assertEqual(resp.content.projects[0].id, "proj-rec-001")
        self.assertEqual(resp.content.achievements[0].id, "ach-rec-001")

    def test_05_empty_sections_not_fabricated(self):
        """When candidate has no work experience or achievements, empty sections are preserved."""
        req = create_valid_resume_request(with_entries=False)

        hallucinating_provider = MagicMock()
        hallucinating_provider.generate_career_response.return_value = {
            "contact": {"fullName": "Alex Mercer"},
            "headline": "Junior Developer",
            "summary": "Entry level summary.",
            "skills": ["Python"],
            "education": [],
            "experience": [
                {
                    "company": "Hallucinated Corp",
                    "role": "Software Intern",
                    "description": "Fabricated internship.",
                }
            ],
            "projects": [],
            "achievements": [
                {
                    "title": "Fabricated Award",
                    "description": "Invented award.",
                }
            ],
        }

        service = CareerService(provider=hallucinating_provider)
        resp = service.generate_resume(req)

        # Candidate had 0 work experience and 0 achievements; guardrail must block fabrication
        self.assertEqual(len(resp.content.experience), 0)
        self.assertEqual(len(resp.content.achievements), 0)

    def test_06_malformed_json_handled_safely(self):
        """Malformed JSON from provider must raise LLMParseError with 502 status code."""
        bad_provider = MagicMock()
        bad_provider.generate_career_response.return_value = "{malformed: JSON: not-closed"

        service = CareerService(provider=bad_provider)
        req = create_valid_resume_request()

        with self.assertRaises(LLMParseError) as ctx:
            service.generate_resume(req)
        self.assertEqual(ctx.exception.status_code, 502)

    def test_07_invalid_schema_handled_safely(self):
        """Provider output failing Pydantic schema validation must raise LLMParseError."""
        bad_provider = MagicMock()
        bad_provider.generate_career_response.return_value = {
            "contact": "not-a-dict",
            "education": "not-a-list",
        }

        service = CareerService(provider=bad_provider)
        req = create_valid_resume_request()

        with self.assertRaises(LLMParseError) as ctx:
            service.generate_resume(req)
        self.assertEqual(ctx.exception.status_code, 502)

    def test_08_empty_provider_output_handled_safely(self):
        """Empty string or None from provider must raise LLMParseError."""
        empty_provider = MagicMock()
        empty_provider.generate_career_response.return_value = ""

        service = CareerService(provider=empty_provider)
        req = create_valid_resume_request()

        with self.assertRaises(LLMParseError) as ctx:
            service.generate_resume(req)
        self.assertEqual(ctx.exception.status_code, 502)

        # Test None response
        empty_provider.generate_career_response.return_value = None
        with self.assertRaises(LLMParseError) as ctx2:
            service.generate_resume(req)
        self.assertEqual(ctx2.exception.status_code, 502)

    def test_09_provider_rate_limit_preserves_status_code(self):
        """Provider 429 rate limit error must be propagated with status_code=429."""
        failing_provider = MagicMock()
        failing_provider.generate_career_response.side_effect = LLMProviderError(
            "Groq API rate limit exceeded (HTTP 429).", status_code=429
        )

        service = CareerService(provider=failing_provider)
        req = create_valid_resume_request()

        with self.assertRaises(LLMProviderError) as ctx:
            service.generate_resume(req)
        self.assertEqual(ctx.exception.status_code, 429)

    def test_10_api_keys_and_credentials_redacted_from_errors(self):
        """Provider exceptions containing API keys or bearer tokens must be sanitized."""
        leaky_provider = MagicMock()
        leaky_provider.generate_career_response.side_effect = LLMProviderError(
            "Connection failed with key gsk_1234567890abcdef1234567890 and Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            status_code=502,
        )

        service = CareerService(provider=leaky_provider)
        req = create_valid_resume_request()

        with self.assertRaises(LLMProviderError) as ctx:
            service.generate_resume(req)

        error_msg = str(ctx.exception.message)
        self.assertNotIn("gsk_1234567890abcdef1234567890", error_msg)
        self.assertNotIn("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", error_msg)
        self.assertIn("[REDACTED_API_KEY]", error_msg)
        self.assertIn("Bearer [REDACTED]", error_msg)

    def test_11_supports_varied_provider_formats_str_and_bytes(self):
        """Service must handle provider returning raw JSON string and bytes."""
        payload = {
            "contact": {"fullName": "Alex Mercer"},
            "headline": "Lead Architect",
            "summary": "Proven track record in distributed architecture.",
            "skills": ["Go", "Kubernetes"],
            "education": [],
            "experience": [],
            "projects": [],
            "achievements": [],
        }

        # Test string format
        str_provider = MagicMock()
        str_provider.generate_career_response.return_value = json.dumps(payload)
        service_str = CareerService(provider=str_provider)
        resp_str = service_str.generate_resume(create_valid_resume_request())
        self.assertEqual(resp_str.content.headline, "Lead Architect")

        # Test bytes format
        bytes_provider = MagicMock()
        bytes_provider.generate_career_response.return_value = json.dumps(payload).encode("utf-8")
        service_bytes = CareerService(provider=bytes_provider)
        resp_bytes = service_bytes.generate_resume(create_valid_resume_request())
        self.assertEqual(resp_bytes.content.headline, "Lead Architect")


class TestCareerServiceATSAnalysis(unittest.TestCase):
    """Test suite for ATS Resume Analysis feedback refinement operations."""

    def setUp(self):
        self.mock_provider = MockLLMProvider()
        self.service = CareerService(provider=self.mock_provider)

    def test_01_successful_ats_analysis_with_mock_provider(self):
        """ATS analysis must return a validated ATSAnalyzeResponse with executive summary."""
        req = create_valid_ats_request(findings_count=3)
        resp = self.service.analyze_ats(req)

        self.assertIsInstance(resp, ATSAnalyzeResponse)
        self.assertTrue(len(resp.summary) > 10)
        self.assertEqual(len(resp.findings), 3)

    def test_02_deterministic_score_and_methodology_preserved(self):
        """
        Deterministic rule score and methodology are not overridden or recalculated.
        Input rule score remains authoritative.
        """
        req = create_valid_ats_request(findings_count=2)
        initial_score = req.rule_score.value
        initial_methodology = req.rule_score.methodology

        # Provider attempting to fabricate a different score
        altering_provider = MagicMock()
        altering_provider.generate_career_response.return_value = {
            "summary": "Executive summary assessing ATS liabilities.",
            "rule_score": {"value": 99.9, "methodology": "llm-overridden"},
            "findings": [
                {"id": "f1-rule-check", "title": "Refined 1", "description": "Desc 1"},
                {"id": "f2-rule-check", "title": "Refined 2", "description": "Desc 2"},
            ],
        }

        service = CareerService(provider=altering_provider)
        resp = service.analyze_ats(req)

        # The service response conforms strictly to ATSAnalyzeResponse (summary, findings)
        # and leaves the input rule score authoritative and untouched
        self.assertEqual(req.rule_score.value, initial_score)
        self.assertEqual(req.rule_score.methodology, initial_methodology)
        self.assertFalse(hasattr(resp, "rule_score"))

    def test_03_original_finding_ids_and_count_preserved(self):
        """All original finding IDs and total count must be strictly preserved."""
        req = create_valid_ats_request(findings_count=3)
        original_ids = [f.id for f in req.rule_findings]

        resp = self.service.analyze_ats(req)

        result_ids = [f.id for f in resp.findings]
        self.assertEqual(result_ids, original_ids)
        self.assertEqual(len(resp.findings), len(original_ids))

    def test_04_omitted_findings_by_llm_are_preserved_not_dropped(self):
        """If LLM drops findings or returns fewer findings, original findings must be preserved."""
        req = create_valid_ats_request(findings_count=3)

        # LLM only returns 1 finding instead of 3
        dropping_provider = MagicMock()
        dropping_provider.generate_career_response.return_value = {
            "summary": "Executive summary assessing ATS liabilities.",
            "findings": [
                {
                    "id": "f1-rule-check",
                    "title": "Refined Title 1",
                    "description": "Refined Description 1",
                    "recommendation": "Use XYZ formula.",
                }
            ],
        }

        service = CareerService(provider=dropping_provider)
        resp = service.analyze_ats(req)

        # Must still have all 3 findings!
        self.assertEqual(len(resp.findings), 3)
        self.assertEqual(resp.findings[0].id, "f1-rule-check")
        self.assertEqual(resp.findings[1].id, "f2-rule-check")
        self.assertEqual(resp.findings[2].id, "f3-rule-check")

    def test_05_scrambled_finding_ids_mapped_back_to_originals(self):
        """If LLM returns invented IDs like 'finding_1', they must be mapped to original IDs."""
        req = create_valid_ats_request(findings_count=2)

        inventing_id_provider = MagicMock()
        inventing_id_provider.generate_career_response.return_value = {
            "summary": "Executive summary assessing ATS liabilities.",
            "findings": [
                {
                    "id": "invented-id-1",
                    "title": "Refined Title 1",
                    "description": "Critique 1",
                },
                {
                    "id": "invented-id-2",
                    "title": "Refined Title 2",
                    "description": "Critique 2",
                },
            ],
        }

        service = CareerService(provider=inventing_id_provider)
        resp = service.analyze_ats(req)

        self.assertEqual(resp.findings[0].id, "f1-rule-check")
        self.assertEqual(resp.findings[1].id, "f2-rule-check")

    def test_06_ats_malformed_json_handled_safely(self):
        """Malformed JSON from provider during ATS analysis must raise LLMParseError."""
        bad_provider = MagicMock()
        bad_provider.generate_career_response.return_value = "Non-JSON response from server"

        service = CareerService(provider=bad_provider)
        req = create_valid_ats_request()

        with self.assertRaises(LLMParseError) as ctx:
            service.analyze_ats(req)
        self.assertEqual(ctx.exception.status_code, 502)

    def test_07_ats_missing_summary_raises_parse_error(self):
        """Response missing executive summary must raise LLMParseError."""
        no_summary_provider = MagicMock()
        no_summary_provider.generate_career_response.return_value = {
            "summary": "",
            "findings": [],
        }

        service = CareerService(provider=no_summary_provider)
        req = create_valid_ats_request()

        with self.assertRaises(LLMParseError) as ctx:
            service.analyze_ats(req)
        self.assertEqual(ctx.exception.status_code, 502)

    def test_08_ats_provider_timeout_handled(self):
        """Provider connection or timeout failure must raise LLMProviderError with 504 status."""
        timeout_provider = MagicMock()
        timeout_provider.generate_career_response.side_effect = LLMProviderError(
            "Groq API connection or timeout failure: Read timed out.", status_code=504
        )

        service = CareerService(provider=timeout_provider)
        req = create_valid_ats_request()

        with self.assertRaises(LLMProviderError) as ctx:
            service.analyze_ats(req)
        self.assertEqual(ctx.exception.status_code, 504)


class TestCareerServiceArchitecture(unittest.TestCase):
    """Test suite for CareerService singleton, aliases, and error helpers."""

    @classmethod
    def setUpClass(cls):
        from app.core.config import settings
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        from app.core.config import settings
        settings.LLM_PROVIDER = cls._original_provider

    def test_01_singleton_returns_same_instance(self):
        """get_career_service must return the singleton instance when no provider passed."""
        s1 = get_career_service()
        s2 = get_career_service()
        self.assertIs(s1, s2)

    def test_02_custom_provider_returns_new_instance(self):
        """get_career_service with custom provider must return a new instance."""
        mock_p = MockLLMProvider()
        s = get_career_service(provider=mock_p)
        self.assertIs(s._provider, mock_p)

    def test_03_method_aliases_callable(self):
        """Method aliases (generate_resume_draft, refine_ats, etc.) must match primary methods."""
        service = CareerService(provider=MockLLMProvider())
        self.assertEqual(service.generate_resume_draft, service.generate_resume)
        self.assertEqual(service.refine_ats, service.analyze_ats)
        self.assertEqual(service.refine_ats_analysis, service.analyze_ats)
        self.assertEqual(service.analyze_ats_feedback, service.analyze_ats)

    def test_04_sanitize_error_message_helper(self):
        """_sanitize_error_message must redact various key patterns."""
        self.assertEqual(_sanitize_error_message(""), "")
        self.assertEqual(_sanitize_error_message(None), "")

        raw = "Error at gsk_abcdef1234567890xyz with key='secret12345678'"
        sanitized = _sanitize_error_message(raw)
        self.assertNotIn("gsk_abcdef1234567890xyz", sanitized)
        self.assertIn("[REDACTED_API_KEY]", sanitized)


if __name__ == "__main__":
    unittest.main()

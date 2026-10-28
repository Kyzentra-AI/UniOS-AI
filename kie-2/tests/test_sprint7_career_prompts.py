"""
Sprint 7 — Career Prompt Builder Tests (AI/ML-2 KIE)
Phase 2: Prompt Builders for Resume Generation & ATS Analysis

Coverage:
  - Resume generation prompt building with canonical & custom inputs
  - Injected target role, tone calibration (concise vs. professional)
  - Grounding whitelists: allowed institutions, companies, projects
  - Anti-hallucination constraints and missing contact handling
  - Preservation of entry IDs and JSON output schema directives
  - ATS analysis prompt building with canonical payload
  - Deterministic score boundary protection (no score alteration)
  - 2-4 sentences executive summary requirement
  - Preservation of original finding IDs and XYZ formula recommendations
  - Large document text truncation safeguard
  - Input validation and ValueError raising on missing required arguments
"""

import unittest

from app.schemas.career import (
    ATSAnalyzeRequest,
    CareerContext,
    CareerContextEducation,
    CareerContextLearner,
    CareerReadiness,
    CareerReadinessEvidence,
    CareerReadinessMastery,
    CareerReadinessProject,
    DocumentFileType,
    DocumentMetadata,
    ResumeAchievement,
    ResumeContact,
    ResumeDraft,
    ResumeEducation,
    ResumeExperience,
    ResumeGenerateRequest,
    ResumePreferences,
    ResumeProject,
    ResumeSource,
    ResumeTone,
    RuleFinding,
    RuleScore,
)
from app.services.career_prompt_builder import (
    build_ats_analysis_prompt,
    build_resume_generation_prompt,
)


class TestSprint7ResumePromptBuilder(unittest.TestCase):
    """Test suite for Resume Generation prompt builder."""

    def setUp(self):
        self.canonical_request = ResumeGenerateRequest.model_validate({
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
                        "description": "Worked on backend APIs.",
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
                    "experience": "Worked on backend APIs.",
                },
                "education": {
                    "university": "University of California, Berkeley",
                    "degree_program": "B.S. in Computer Science",
                    "domain": "Distributed Systems",
                    "academic_status": "graduated",
                },
                "career_readiness": {
                    "projects": [
                        {
                            "id": "d61b34e5-9c8a-4d22-9cb7-789a456123ef",
                            "title": "Distributed Task Scheduler",
                            "description": "High-throughput asynchronous task queue.",
                            "skills": ["Python", "Redis", "Docker"],
                            "status": "COMPLETED",
                        }
                    ],
                    "evidence": [
                        {
                            "id": "ev-001",
                            "title": "Production Load Test Evidence",
                            "description": "Benchmarked at 50,000 tasks/second with sub-10ms p99 latency.",
                            "skills": ["Python", "Redis", "Benchmarking"],
                            "created_at": "2024-04-10T12:00:00Z",
                        }
                    ],
                    "mastery": [
                        {
                            "subject": "Distributed Systems",
                            "topic": "Eventual Consistency",
                            "mastery_score": 0.95,
                            "status": "MASTERED",
                        }
                    ],
                },
            },
        })

    def test_build_resume_prompt_contains_all_input_sections(self):
        """Prompt must include contact, headline, education, experience, projects, and career evidence."""
        prompt = build_resume_generation_prompt(self.canonical_request)

        # Contact info
        self.assertIn("Jordan Lee", prompt)
        self.assertIn("jordan.lee@example.com", prompt)
        self.assertIn("https://linkedin.com/in/jordanlee", prompt)

        # Base draft sections
        self.assertIn("University of California, Berkeley", prompt)
        self.assertIn("Acme Cloud Corp", prompt)
        self.assertIn("Distributed Task Scheduler", prompt)
        self.assertIn("AWS Certified Solutions Architect", prompt)

        # Career context evidence
        self.assertIn("Become a Principal Cloud Architect", prompt)
        self.assertIn("Production Load Test Evidence", prompt)
        self.assertIn("50,000 tasks/second", prompt)
        self.assertIn("Eventual Consistency", prompt)

    def test_build_resume_prompt_whitelists_and_grounding(self):
        """Prompt must strictly specify allowed institutions, companies, and projects."""
        prompt = build_resume_generation_prompt(self.canonical_request)

        # Grounding whitelists
        self.assertIn('Allowed companies: "Acme Cloud Corp"', prompt)
        self.assertIn('Allowed institutions: "University of California, Berkeley"', prompt)
        self.assertIn('Allowed projects: "Distributed Task Scheduler"', prompt)

        # Invariants
        self.assertIn("NEVER INVENT CREDENTIALS OR METRICS", prompt)
        self.assertIn("ELEVATE, DO NOT FABRICATE", prompt)
        self.assertIn("PRESERVE ORIGINAL IDS", prompt)

    def test_target_role_and_concise_tone_calibration(self):
        """When tone is 'concise', prompt must require bullets under 20 words."""
        custom_req = self.canonical_request.model_copy(deep=True)
        custom_req.preferences.target_role = "DevOps Platform Engineer"
        custom_req.preferences.tone = ResumeTone.CONCISE

        prompt = build_resume_generation_prompt(custom_req)
        self.assertIn("DevOps Platform Engineer", prompt)
        self.assertIn("CONCISE", prompt)
        self.assertIn("strictly under 20 words", prompt)

    def test_professional_tone_calibration(self):
        """When tone is 'professional', prompt must require executive outcomes-focused terminology."""
        custom_req = self.canonical_request.model_copy(deep=True)
        custom_req.preferences.tone = ResumeTone.PROFESSIONAL

        prompt = build_resume_generation_prompt(custom_req)
        self.assertIn("PROFESSIONAL", prompt)
        self.assertIn("outcomes-focused", prompt)

    def test_missing_contact_treated_as_missing(self):
        """Missing contact info must instruct LLM not to fabricate placeholder details."""
        draft = ResumeDraft(
            contact=ResumeContact(full_name="Sam Solo"),
            headline="Web Developer",
        )
        prompt = build_resume_generation_prompt(content=draft, title="Web Developer")

        self.assertIn("Sam Solo", prompt)
        self.assertIn("Do NOT fabricate", prompt)
        self.assertIn('"linkedInUrl": null', prompt)
        self.assertIn('"githubUrl": null', prompt)

    def test_resume_prompt_direct_keyword_arguments(self):
        """Prompt builder should support standalone keyword arguments without ResumeGenerateRequest wrapper."""
        draft = ResumeDraft(
            headline="ML Engineer",
            skills=["PyTorch", "Transformers"],
            projects=[ResumeProject(name="LLM Finetuner", description="LoRA tuning")],
        )
        prefs = ResumePreferences(target_role="AI Research Engineer", tone=ResumeTone.CONCISE)
        ctx = CareerContext(learner_id="l-100")

        prompt = build_resume_generation_prompt(
            content=draft,
            preferences=prefs,
            career_context=ctx,
            title="ML Engineer Resume",
        )
        self.assertIn("AI Research Engineer", prompt)
        self.assertIn("PyTorch", prompt)
        self.assertIn("LLM Finetuner", prompt)

    def test_missing_content_raises_value_error(self):
        """Calling without content or request must raise ValueError."""
        with self.assertRaises(ValueError):
            build_resume_generation_prompt()


class TestSprint7ATSPromptBuilder(unittest.TestCase):
    """Test suite for ATS Resume Analysis prompt builder."""

    def setUp(self):
        self.canonical_request = ATSAnalyzeRequest.model_validate({
            "request_id": "2d8f99a0-1b2c-4e3d-9f0a-112233445566",
            "learner_id": "00000000-0000-0000-0000-000000000002",
            "document": {
                "fileName": "Jordan_Lee_Resume.pdf",
                "fileType": "pdf",
                "pageCount": 1,
                "extractedCharacterCount": 2150,
            },
            "extracted_text": "Jordan Lee\njordan.lee@example.com | San Francisco, CA\n\nEXPERIENCE\nAcme Cloud Corp - Intern\nWorked on backend APIs.\n\nPROJECTS\nDistributed Task Scheduler",
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
                    "recommendation": "Add a standardized phone number.",
                },
                {
                    "id": "f2-metrics",
                    "category": "missing_information",
                    "severity": "warning",
                    "title": "Few Quantifiable Impact Metrics",
                    "description": "Found only 0 quantifiable data points.",
                    "recommendation": "Include specific numbers.",
                },
            ],
        })

    def test_build_ats_prompt_contains_all_input_sections(self):
        """Prompt must contain metadata, deterministic score, initial findings, and extracted text."""
        prompt = build_ats_analysis_prompt(self.canonical_request)

        # Document metadata
        self.assertIn("Jordan_Lee_Resume.pdf", prompt)
        self.assertIn("pdf", prompt)
        self.assertIn("Pages: 1", prompt)

        # Score & methodology
        self.assertIn("72.0 / 100.0", prompt)
        self.assertIn("defined-rule-based-checks", prompt)

        # Findings
        self.assertIn("Finding ID: f1-contact", prompt)
        self.assertIn("Missing Phone Number", prompt)
        self.assertIn("Finding ID: f2-metrics", prompt)

        # Extracted text
        self.assertIn("Jordan Lee", prompt)
        self.assertIn("Worked on backend APIs", prompt)

    def test_ats_prompt_deterministic_score_preservation(self):
        """Prompt must strictly forbid altering or replacing the deterministic score."""
        prompt = build_ats_analysis_prompt(self.canonical_request)

        self.assertIn("PRESERVE DETERMINISTIC SCORE BOUNDARY", prompt)
        self.assertIn("You MUST NOT calculate a new numerical score", prompt)

    def test_ats_prompt_executive_summary_directive(self):
        """Prompt must explicitly demand a 2 to 4 sentences executive summary."""
        prompt = build_ats_analysis_prompt(self.canonical_request)

        self.assertIn("exactly 2 to 4 sentences", prompt)
        self.assertIn("core strengths", prompt)
        self.assertIn("ATS filter liabilities", prompt)

    def test_ats_prompt_finding_id_preservation_and_xyz_formula(self):
        """Prompt must demand keeping exact finding IDs and recommending Google XYZ formula."""
        prompt = build_ats_analysis_prompt(self.canonical_request)

        self.assertIn("You MUST keep the exact 'id' for each finding", prompt)
        self.assertIn("Google XYZ formula", prompt)
        self.assertIn("Accomplished [X], as measured by [Y], by doing [Z]", prompt)

    def test_ats_prompt_text_truncation_safeguard(self):
        """Extremely large resume text (>12000 chars) must be safely truncated to protect token limits."""
        huge_text = "Experienced Developer with skills in cloud.\n" * 500  # ~22,000 chars
        prompt = build_ats_analysis_prompt(
            extracted_text=huge_text,
            rule_score=RuleScore(value=80.0),
            document=DocumentMetadata(file_name="large.pdf", file_type=DocumentFileType.PDF),
        )

        self.assertIn("truncated for length", prompt)
        self.assertLess(len(prompt), 18000)

    def test_ats_prompt_missing_required_args_raises_value_error(self):
        """Missing extracted_text or rule_score must raise ValueError."""
        with self.assertRaises(ValueError):
            build_ats_analysis_prompt(extracted_text=None, rule_score=RuleScore(value=50.0))

        with self.assertRaises(ValueError):
            build_ats_analysis_prompt(extracted_text="Resume text", rule_score=None)


if __name__ == "__main__":
    unittest.main()

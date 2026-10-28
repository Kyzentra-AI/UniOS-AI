"""
Sprint 7 — Career Intelligence & ATS Schema Tests (AI/ML-2 KIE)
Phase 1: Schemas and Contracts

Coverage:
  - Canonical payloads from launch_aiml_integration_guide.md (Sections 3.3, 3.4, 4.3, 4.4)
  - ResumeGenerateRequest and ResumeGenerateResponse valid & minimal payloads
  - ATSAnalyzeRequest and ATSAnalyzeResponse valid & minimal payloads
  - Missing required fields validation (top-level and nested)
  - Documented enum validation (ResumeSource, ResumeTone, DocumentFileType, ATSFindingSeverity)
  - Score boundary validation (RuleScore: 0.0–100.0, CareerReadinessMastery: 0.0–1.0)
  - camelCase and snake_case alias compatibility for all documented fields
  - Unknown-field tolerance (extra='ignore' policy)
"""

import unittest
from pydantic import ValidationError

from app.schemas.career import (
    ATSAnalyzeRequest,
    ATSAnalyzeResponse,
    ATSFinding,
    ATSFindingSeverity,
    CareerContext,
    CareerContextEducation,
    CareerContextLearner,
    CareerReadiness,
    CareerReadinessEvidence,
    CareerReadinessMastery,
    CareerReadinessProject,
    ContextV2,
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


class TestSprint7ResumeSchemas(unittest.TestCase):
    """Test suite for Resume Generation schemas (BE-S7-01 / BE-S7-04)."""

    def setUp(self):
        """Canonical test payload from launch_aiml_integration_guide.md Section 3.3."""
        self.canonical_resume_request_payload = {
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
                    "academic_status": "graduated",
                },
                "career_readiness": {
                    "projects": [
                        {
                            "id": "d61b34e5-9c8a-4d22-9cb7-789a456123ef",
                            "title": "Distributed Task Scheduler",
                            "description": "High-throughput asynchronous task queue with Redis and priority workers.",
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
                        },
                        {
                            "subject": "Databases",
                            "topic": "PostgreSQL Query Optimization",
                            "mastery_score": 0.92,
                            "status": "MASTERED",
                        },
                    ],
                },
            },
        }

    def test_canonical_resume_request_valid(self):
        """Validate that the canonical integration guide payload parses with 100% field fidelity."""
        req = ResumeGenerateRequest.model_validate(self.canonical_resume_request_payload)
        self.assertEqual(req.request_id, "1c9a9189-3cb4-4b25-a053-467c1c0777d1")
        self.assertEqual(req.learner_id, "00000000-0000-0000-0000-000000000002")
        self.assertEqual(req.title, "Senior Cloud Backend Engineer")
        self.assertEqual(req.source, ResumeSource.PROFILE)

        # Preferences
        self.assertIsNotNone(req.preferences)
        self.assertEqual(req.preferences.target_role, "Backend Systems Architect")
        self.assertEqual(req.preferences.tone, ResumeTone.PROFESSIONAL)

        # Content
        self.assertEqual(req.content.contact.full_name, "Jordan Lee")
        self.assertEqual(req.content.contact.email, "jordan.lee@example.com")
        self.assertEqual(req.content.contact.linkedin_url, "https://linkedin.com/in/jordanlee")
        self.assertEqual(req.content.headline, "Software Engineer")
        self.assertEqual(len(req.content.education), 1)
        self.assertEqual(req.content.education[0].institution, "University of California, Berkeley")
        self.assertEqual(req.content.education[0].field_of_study, "Distributed Systems")
        self.assertEqual(len(req.content.experience), 1)
        self.assertEqual(req.content.experience[0].company, "Acme Cloud Corp")
        self.assertFalse(req.content.experience[0].is_current)
        self.assertEqual(len(req.content.projects), 1)
        self.assertEqual(req.content.projects[0].project_url, "https://github.com/jordanlee/scheduler")
        self.assertEqual(len(req.content.achievements), 1)

        # Career context
        self.assertEqual(req.career_context.learner_id, "00000000-0000-0000-0000-000000000002")
        self.assertEqual(req.career_context.learner.primary_goal, "Become a Principal Cloud Architect")
        self.assertEqual(req.career_context.education.university, "University of California, Berkeley")
        self.assertEqual(len(req.career_context.career_readiness.projects), 1)
        self.assertEqual(len(req.career_context.career_readiness.evidence), 1)
        self.assertEqual(len(req.career_context.career_readiness.mastery), 2)
        self.assertEqual(req.career_context.career_readiness.mastery[0].mastery_score, 0.95)

    def test_minimal_resume_request_valid(self):
        """Preferences are optional; lists in content can be empty."""
        minimal_payload = {
            "request_id": "req-minimal-001",
            "learner_id": "learner-001",
            "title": "Junior Developer",
            "source": "manual",
            "content": {
                "headline": "Aspiring Developer",
            },
            "career_context": {
                "learner_id": "learner-001",
            },
        }
        req = ResumeGenerateRequest.model_validate(minimal_payload)
        self.assertEqual(req.request_id, "req-minimal-001")
        self.assertEqual(req.source, ResumeSource.MANUAL)
        self.assertIsNone(req.preferences)
        self.assertEqual(req.content.skills, [])
        self.assertEqual(req.content.education, [])
        self.assertEqual(req.content.experience, [])
        self.assertIsNone(req.career_context.learner)

    def test_camel_case_and_snake_case_aliases_resume_request(self):
        """Verify camelCase aliases operate symmetrically with snake_case fields."""
        payload = {
            "requestId": "trace-uuid-1234",
            "learnerId": "learner-uuid-5678",
            "title": "Staff Engineer",
            "source": "profile",
            "preferences": {
                "target_role": "Staff Architect",
                "tone": "concise",
            },
            "content": {
                "contact": {
                    "full_name": "Alex Mercer",
                    "email": "alex@example.com",
                    "linkedInUrl": "https://linkedin.com/in/alex",
                    "github_url": "https://github.com/alex",
                    "portfolio_url": "https://alex.dev",
                },
                "education": [
                    {
                        "institution": "MIT",
                        "field_of_study": "AI",
                        "startDate": "2020",
                        "end_date": "2024",
                    }
                ],
                "experience": [
                    {
                        "company": "Tech Corp",
                        "isCurrent": True,
                        "startDate": "2024-01",
                    }
                ],
                "projects": [
                    {
                        "name": "Kernel Module",
                        "projectUrl": "https://github.com/alex/kernel",
                    }
                ],
            },
            "careerContext": {
                "learnerId": "learner-uuid-5678",
                "learner": {
                    "primaryGoal": "Become CTO",
                },
                "education": {
                    "degreeProgram": "Ph.D. CS",
                    "academicStatus": "graduated",
                },
                "careerReadiness": {
                    "evidence": [
                        {
                            "title": "Benchmark",
                            "createdAt": "2024-01-01T00:00:00Z",
                        }
                    ],
                    "mastery": [
                        {
                            "topic": "Concurrency",
                            "masteryScore": 0.99,
                        }
                    ],
                },
            },
        }
        req = ResumeGenerateRequest.model_validate(payload)
        self.assertEqual(req.request_id, "trace-uuid-1234")
        self.assertEqual(req.learner_id, "learner-uuid-5678")
        self.assertEqual(req.preferences.target_role, "Staff Architect")
        self.assertEqual(req.preferences.tone, ResumeTone.CONCISE)
        self.assertEqual(req.content.contact.full_name, "Alex Mercer")
        self.assertEqual(req.content.contact.linkedin_url, "https://linkedin.com/in/alex")
        self.assertEqual(req.content.contact.github_url, "https://github.com/alex")
        self.assertEqual(req.content.education[0].field_of_study, "AI")
        self.assertTrue(req.content.experience[0].is_current)
        self.assertEqual(req.content.projects[0].project_url, "https://github.com/alex/kernel")
        self.assertEqual(req.career_context.learner.primary_goal, "Become CTO")
        self.assertEqual(req.career_context.education.degree_program, "Ph.D. CS")
        self.assertEqual(req.career_context.career_readiness.evidence[0].created_at, "2024-01-01T00:00:00Z")
        self.assertEqual(req.career_context.career_readiness.mastery[0].mastery_score, 0.99)

    def test_missing_required_fields_resume_request(self):
        """Missing top-level required fields must raise ValidationError."""
        base = {
            "request_id": "req-1",
            "learner_id": "l-1",
            "title": "Title",
            "source": "manual",
            "content": {},
            "career_context": {"learner_id": "l-1"},
        }

        # Omit request_id
        payload = dict(base)
        del payload["request_id"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

        # Omit learner_id
        payload = dict(base)
        del payload["learner_id"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

        # Omit title
        payload = dict(base)
        del payload["title"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

        # Omit source
        payload = dict(base)
        del payload["source"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

        # Omit content
        payload = dict(base)
        del payload["content"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

        # Omit career_context
        payload = dict(base)
        del payload["career_context"]
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate(payload)

    def test_nested_required_fields_in_content(self):
        """Nested items (education.institution, experience.company, project.name) are mandatory."""
        with self.assertRaises(ValidationError):
            ResumeEducation.model_validate({})

        with self.assertRaises(ValidationError):
            ResumeExperience.model_validate({})

        with self.assertRaises(ValidationError):
            ResumeProject.model_validate({})

        with self.assertRaises(ValidationError):
            ResumeAchievement.model_validate({})

    def test_resume_enums(self):
        """Verify enum validations and case normalization for source and tone."""
        # Valid source
        req1 = ResumeGenerateRequest.model_validate({
            "request_id": "r1",
            "learner_id": "l1",
            "title": "T",
            "source": "PROFILE",
            "content": {},
            "career_context": {"learner_id": "l1"},
        })
        self.assertEqual(req1.source, ResumeSource.PROFILE)

        # Invalid source
        with self.assertRaises(ValidationError):
            ResumeGenerateRequest.model_validate({
                "request_id": "r1",
                "learner_id": "l1",
                "title": "T",
                "source": "automated",
                "content": {},
                "career_context": {"learner_id": "l1"},
            })

        # Valid tone
        pref = ResumePreferences.model_validate({"tone": "CONCISE"})
        self.assertEqual(pref.tone, ResumeTone.CONCISE)

        # Invalid tone
        with self.assertRaises(ValidationError):
            ResumePreferences.model_validate({"tone": "informal"})

    def test_mastery_score_boundaries(self):
        """Mastery score must be bounded between 0.0 and 1.0."""
        # Valid boundaries
        m0 = CareerReadinessMastery(topic="Algorithms", mastery_score=0.0)
        self.assertEqual(m0.mastery_score, 0.0)

        m1 = CareerReadinessMastery(topic="Algorithms", mastery_score=1.0)
        self.assertEqual(m1.mastery_score, 1.0)

        # Below 0.0
        with self.assertRaises(ValidationError):
            CareerReadinessMastery(topic="Algorithms", mastery_score=-0.01)

        # Above 1.0
        with self.assertRaises(ValidationError):
            CareerReadinessMastery(topic="Algorithms", mastery_score=1.05)

    def test_resume_generate_response_contract(self):
        """Verify ResumeGenerateResponse structure matches integration guide Section 3.4."""
        resp_payload = {
            "content": {
                "headline": "Backend Systems Architect | Distributed Cloud Platforms",
                "summary": "Impact-driven Backend Systems Architect.",
                "skills": ["Python", "FastAPI", "Go"],
                "education": [
                    {
                        "institution": "University of California, Berkeley",
                        "degree": "B.S. in Computer Science",
                    }
                ],
                "experience": [
                    {
                        "company": "Acme Cloud Corp",
                        "role": "Software Engineering Intern",
                        "description": "Architected ingestion services.",
                    }
                ],
                "projects": [
                    {
                        "name": "Distributed Task Scheduler",
                        "description": "Built async worker.",
                    }
                ],
                "achievements": [
                    {
                        "title": "AWS Certified Solutions Architect",
                    }
                ],
            }
        }
        resp = ResumeGenerateResponse.model_validate(resp_payload)
        self.assertIn("Backend Systems Architect", resp.content.headline)
        self.assertEqual(len(resp.content.skills), 3)
        self.assertEqual(resp.content.education[0].institution, "University of California, Berkeley")


class TestSprint7ATSSchemas(unittest.TestCase):
    """Test suite for ATS Resume Analysis schemas (BE-S7-04 / Section 4)."""

    def setUp(self):
        """Canonical test payload from launch_aiml_integration_guide.md Section 4.3."""
        self.canonical_ats_request_payload = {
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

    def test_canonical_ats_request_valid(self):
        """Validate that the canonical ATS payload parses with 100% field fidelity."""
        req = ATSAnalyzeRequest.model_validate(self.canonical_ats_request_payload)
        self.assertEqual(req.request_id, "2d8f99a0-1b2c-4e3d-9f0a-112233445566")
        self.assertEqual(req.learner_id, "00000000-0000-0000-0000-000000000002")
        self.assertEqual(req.document.file_name, "Jordan_Lee_Resume.pdf")
        self.assertEqual(req.document.file_type, DocumentFileType.PDF)
        self.assertEqual(req.document.page_count, 1)
        self.assertEqual(req.document.extracted_character_count, 2150)
        self.assertIn("Jordan Lee", req.extracted_text)
        self.assertEqual(req.rule_score.value, 72.0)
        self.assertEqual(req.rule_score.max_value, 100.0)
        self.assertEqual(req.rule_score.methodology, "defined-rule-based-checks")
        self.assertEqual(len(req.rule_findings), 3)
        self.assertEqual(req.rule_findings[0].id, "f1-contact")
        self.assertEqual(req.rule_findings[0].severity, ATSFindingSeverity.WARNING)

    def test_minimal_ats_request_valid(self):
        """Minimal ATS payload without optional pageCount / extractedCharacterCount."""
        minimal = {
            "request_id": "trace-ats-001",
            "learner_id": "learner-001",
            "document": {
                "file_name": "resume.docx",
                "file_type": "docx",
            },
            "extracted_text": "Simple resume text",
            "rule_score": {
                "value": 85.5,
            },
        }
        req = ATSAnalyzeRequest.model_validate(minimal)
        self.assertEqual(req.document.file_type, DocumentFileType.DOCX)
        self.assertIsNone(req.document.page_count)
        self.assertEqual(req.rule_findings, [])
        self.assertEqual(req.rule_score.max_value, 100.0)

    def test_camel_case_and_snake_case_aliases_ats(self):
        """Verify camelCase and snake_case interchangeable support for ATS schemas."""
        payload = {
            "requestId": "trace-camel-001",
            "learnerId": "learner-camel-002",
            "document": {
                "fileName": "cv.pdf",
                "fileType": "pdf",
                "pageCount": 2,
                "extractedCharacterCount": 4200,
            },
            "extractedText": "Sample resume content",
            "ruleScore": {
                "value": 90.0,
                "maxValue": 100.0,
                "methodologyVersion": "2.0",
            },
            "ruleFindings": [
                {
                    "id": "f-1",
                    "category": "content",
                    "severity": "CRITICAL",
                    "title": "Typo",
                    "description": "Found typo",
                }
            ],
        }
        req = ATSAnalyzeRequest.model_validate(payload)
        self.assertEqual(req.request_id, "trace-camel-001")
        self.assertEqual(req.learner_id, "learner-camel-002")
        self.assertEqual(req.document.file_name, "cv.pdf")
        self.assertEqual(req.document.extracted_character_count, 4200)
        self.assertEqual(req.extracted_text, "Sample resume content")
        self.assertEqual(req.rule_score.value, 90.0)
        self.assertEqual(req.rule_score.methodology_version, "2.0")
        self.assertEqual(len(req.rule_findings), 1)
        self.assertEqual(req.rule_findings[0].severity, ATSFindingSeverity.CRITICAL)

    def test_missing_required_fields_ats(self):
        """Missing top-level and document fields must trigger validation errors."""
        base = {
            "request_id": "r-1",
            "learner_id": "l-1",
            "document": {"file_name": "a.pdf", "file_type": "pdf"},
            "extracted_text": "content",
            "rule_score": {"value": 80.0},
        }

        # Omit document
        payload = dict(base)
        del payload["document"]
        with self.assertRaises(ValidationError):
            ATSAnalyzeRequest.model_validate(payload)

        # Omit extracted_text
        payload = dict(base)
        del payload["extracted_text"]
        with self.assertRaises(ValidationError):
            ATSAnalyzeRequest.model_validate(payload)

        # Omit rule_score
        payload = dict(base)
        del payload["rule_score"]
        with self.assertRaises(ValidationError):
            ATSAnalyzeRequest.model_validate(payload)

        # Omit document.fileName
        with self.assertRaises(ValidationError):
            DocumentMetadata.model_validate({"file_type": "pdf"})

        # Omit document.fileType
        with self.assertRaises(ValidationError):
            DocumentMetadata.model_validate({"file_name": "a.pdf"})

    def test_rule_score_boundaries(self):
        """Rule score values must be bounded between 0.0 and 100.0."""
        # Valid boundaries
        s0 = RuleScore(value=0.0)
        self.assertEqual(s0.value, 0.0)

        s100 = RuleScore(value=100.0)
        self.assertEqual(s100.value, 100.0)

        # Negative score
        with self.assertRaises(ValidationError):
            RuleScore(value=-0.5)

        # Over 100.0 score
        with self.assertRaises(ValidationError):
            RuleScore(value=100.5)

    def test_ats_enums_validation(self):
        """DocumentFileType and ATSFindingSeverity enums must be strictly validated."""
        # Valid file types
        d1 = DocumentMetadata(file_name="doc.pdf", file_type="PDF")
        self.assertEqual(d1.file_type, DocumentFileType.PDF)

        d2 = DocumentMetadata(file_name="doc.docx", file_type="docx")
        self.assertEqual(d2.file_type, DocumentFileType.DOCX)

        # Invalid file type
        with self.assertRaises(ValidationError):
            DocumentMetadata(file_name="doc.txt", file_type="txt")

        # Valid severities
        for sev in ["info", "suggestion", "warning", "critical", "WARNING", "CRITICAL"]:
            finding = RuleFinding(
                id="f1",
                category="content",
                severity=sev,
                title="T",
                description="D",
            )
            self.assertIn(finding.severity, ATSFindingSeverity)

        # Invalid severity
        with self.assertRaises(ValidationError):
            RuleFinding(
                id="f1",
                category="content",
                severity="fatal",
                title="T",
                description="D",
            )

    def test_ats_analyze_response_contract(self):
        """Verify ATSAnalyzeResponse matches integration guide Section 4.4."""
        resp_payload = {
            "summary": "Your resume establishes solid academic credentials from UC Berkeley.",
            "findings": [
                {
                    "id": "f1-contact",
                    "category": "contact_information",
                    "severity": "warning",
                    "title": "Missing Phone & Professional Profiles",
                    "description": "Recruiters require direct contact.",
                    "recommendation": "Place a phone number in header.",
                },
                {
                    "id": "f2-metrics",
                    "category": "missing_information",
                    "severity": "critical",
                    "title": "No Quantifiable Engineering Metrics",
                    "description": "Descriptions give zero indication of scale.",
                    "recommendation": "Use XYZ formula.",
                },
            ],
        }
        resp = ATSAnalyzeResponse.model_validate(resp_payload)
        self.assertIn("solid academic credentials", resp.summary)
        self.assertEqual(len(resp.findings), 2)
        self.assertEqual(resp.findings[1].severity, ATSFindingSeverity.CRITICAL)

        # Missing required summary
        with self.assertRaises(ValidationError):
            ATSAnalyzeResponse.model_validate({"findings": []})


class TestUnknownFieldsPreserved(unittest.TestCase):
    """Test that unknown fields do not cause unexpected validation failures."""

    def test_extra_fields_ignored_gracefully(self):
        """Verify extra='ignore' behaves in line with the project's Pydantic conventions."""
        req_payload = {
            "request_id": "trace-uuid",
            "learner_id": "learner-uuid",
            "title": "Title",
            "source": "manual",
            "extra_telemetry_field": "some_backend_data",
            "content": {
                "headline": "Dev",
                "custom_unsupported_section": {"random": 123},
            },
            "career_context": {
                "learner_id": "learner-uuid",
                "extra_metadata": [1, 2, 3],
            },
        }
        req = ResumeGenerateRequest.model_validate(req_payload)
        self.assertEqual(req.request_id, "trace-uuid")

        ats_payload = {
            "request_id": "trace-uuid",
            "learner_id": "learner-uuid",
            "document": {
                "file_name": "test.pdf",
                "file_type": "pdf",
                "server_storage_path": "/tmp/test.pdf",
            },
            "extracted_text": "Text",
            "rule_score": {"value": 75.0, "extra_backend_weight": 0.8},
        }
        ats_req = ATSAnalyzeRequest.model_validate(ats_payload)
        self.assertEqual(ats_req.document.file_name, "test.pdf")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.core.config import settings
from app.schemas import (
    LearnerStage,
    ReadinessTier,
    SkillCategory,
    DeclaredSkill,
    LearningPreferencesInput,
    LearnerProfileValidationResult,
    OnboardingInputProfile,
    LearnerIntelligenceReport,
)
from app.services import (
    build_onboarding_intelligence_prompt,
    get_llm_provider,
    MockLLMProvider,
    LLMProviderError,
    LLMParseError,
    extract_json_payload,
    normalize_intelligence_dict,
)


class TestSprint2OnboardingIntelligence(unittest.TestCase):
    """Evaluation and contract test harness for AI/ML-2 Sprint-2 (Identity + AI Onboarding).
    Guaranteed to run 100% offline without live external API dependencies.
    """

    @classmethod
    def setUpClass(cls):
        # Enforce offline mock mode for all tests in this suite
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.provider = MockLLMProvider()
        self.client = TestClient(app)

    # 1. Bachelor Learner Test
    def test_bachelor_beginner_onboarding(self):
        """Verify onboarding intelligence for a beginner bachelor student requiring foundational scaffolding."""
        profile = OnboardingInputProfile(
            learner_id="learner_bach_001",
            stage=LearnerStage.BACHELOR,
            academic_program="B.Tech Computer Science",
            current_semester=1,
            target_role="Fullstack Software Engineer",
            declared_skills=[
                DeclaredSkill(
                    skill_name="Python",
                    self_rating=2,
                    category=SkillCategory.PROGRAMMING,
                ),
                DeclaredSkill(
                    skill_name="HTML/CSS",
                    self_rating=2,
                    category=SkillCategory.PROGRAMMING,
                ),
            ],
            interests=["Web Development", "UI Animation"],
            preferences=LearningPreferencesInput(
                preferred_medium="visual",
                pace="moderate",
                weekly_hours=12,
                practical_vs_theory_ratio=0.75,
            ),
            motivation_statement="I want to learn how to build real web applications from scratch.",
        )

        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("Fullstack Software Engineer", prompt)
        self.assertIn("Learner Stage: Bachelor's Degree", prompt)

        report = self.provider.analyze_learner_onboarding(profile, prompt)

        # Validate top-level metadata
        self.assertEqual(report.learner_id, "learner_bach_001")
        self.assertEqual(report.stage, LearnerStage.BACHELOR)
        self.assertEqual(report.target_role, "Fullstack Software Engineer")

        # 6 Intelligence Dimensions
        self.assertTrue(len(report.skill_analysis.baseline_summary) > 10)
        self.assertTrue(len(report.skill_analysis.critical_skill_gaps) > 0)
        self.assertTrue(len(report.knowledge_analysis.recommended_foundation_topics) > 0)
        self.assertTrue(len(report.learning_style.dominant_modality) > 0)
        self.assertTrue(len(report.learning_style.content_format_priorities) > 0)
        self.assertEqual(report.career_goals.target_role, "Fullstack Software Engineer")
        self.assertTrue(0.0 <= report.career_goals.role_alignment_score <= 1.0)
        self.assertTrue(len(report.career_goals.key_milestones) >= 2)
        self.assertTrue(len(report.motivation.primary_driver) > 0)
        self.assertTrue(len(report.motivation.resilience_advice) > 5)
        self.assertTrue(0.0 <= report.readiness.overall_readiness_score <= 1.0)
        self.assertIn(
            report.readiness.readiness_tier,
            [ReadinessTier.HIGH, ReadinessTier.MODERATE, ReadinessTier.NEEDS_SCAFFOLDING],
        )

    # 2. Master Learner Test
    def test_master_student_advanced_onboarding(self):
        """Verify onboarding intelligence for a master's student with high baseline skills."""
        profile = OnboardingInputProfile(
            learner_id="learner_master_003",
            stage=LearnerStage.MASTER,
            academic_program="M.S. Computer Science",
            current_semester=3,
            target_role="Distributed Systems Architect",
            declared_skills=[
                DeclaredSkill(
                    skill_name="Go",
                    self_rating=4,
                    category=SkillCategory.PROGRAMMING,
                ),
                DeclaredSkill(
                    skill_name="Operating Systems",
                    self_rating=4,
                    category=SkillCategory.THEORY,
                ),
                DeclaredSkill(
                    skill_name="Kubernetes & Docker",
                    self_rating=4,
                    category=SkillCategory.TOOLS,
                ),
                DeclaredSkill(
                    skill_name="Distributed Consensus",
                    self_rating=3,
                    category=SkillCategory.THEORY,
                ),
            ],
            interests=["Raft Consensus", "Cloud Native Storage", "Microservice Mesh"],
            preferences=LearningPreferencesInput(
                preferred_medium="theoretical",
                pace="fast-track",
                weekly_hours=15,
                practical_vs_theory_ratio=0.4,
            ),
            motivation_statement="Mastering distributed consensus protocols and lock-free concurrency.",
            prior_projects_summary="Implemented a Raft-based key-value store and distributed caching layer.",
        )

        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("Learner Stage: Master's Degree", prompt)
        report = self.provider.analyze_learner_onboarding(profile, prompt)

        self.assertEqual(report.stage, LearnerStage.MASTER)
        self.assertTrue(report.readiness.overall_readiness_score >= 0.6)
        self.assertTrue(len(report.career_goals.key_milestones) >= 2)

    # 3. Graduate Learner Test
    def test_graduate_career_switcher_onboarding(self):
        """Verify onboarding intelligence for a graduate switching into AI/Machine Learning."""
        profile = OnboardingInputProfile(
            learner_id="learner_grad_002",
            stage=LearnerStage.GRADUATE,
            academic_program="Mechanical Engineering (Transitioning)",
            target_role="AI / Machine Learning Engineer",
            declared_skills=[
                DeclaredSkill(
                    skill_name="Python",
                    self_rating=3,
                    category=SkillCategory.PROGRAMMING,
                ),
                DeclaredSkill(
                    skill_name="Linear Algebra",
                    self_rating=4,
                    category=SkillCategory.THEORY,
                ),
                DeclaredSkill(
                    skill_name="SQL",
                    self_rating=2,
                    category=SkillCategory.TOOLS,
                ),
            ],
            interests=["Deep Learning", "Generative AI", "LLMs"],
            preferences=LearningPreferencesInput(
                preferred_medium="hands-on",
                pace="fast-track",
                weekly_hours=25,
                practical_vs_theory_ratio=0.8,
            ),
            motivation_statement="Transitioning from mechanical engineering into industry AI engineering.",
            prior_projects_summary="Built numerical physics simulations and basic numpy regression models.",
        )

        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("Learner Stage: Recent Graduate", prompt)
        report = self.provider.analyze_learner_onboarding(profile, prompt)

        self.assertEqual(report.stage, LearnerStage.GRADUATE)
        self.assertEqual(report.target_role, "AI / Machine Learning Engineer")
        self.assertTrue(len(report.skill_analysis.critical_skill_gaps) > 0)
        self.assertTrue(len(report.career_goals.high_priority_competencies) > 0)
        self.assertTrue(0.0 <= report.readiness.overall_readiness_score <= 1.0)

    # 4. Valid Onboarding Profile Test
    def test_valid_onboarding_profile_instantiation(self):
        """Verify valid onboarding profile creation and summary generation."""
        profile = OnboardingInputProfile(
            learner_id="valid_user_01",
            stage=LearnerStage.BACHELOR,
            target_role="Data Engineer",
            declared_skills=[
                DeclaredSkill(skill_name="Python", self_rating=4),
                DeclaredSkill(skill_name="SQL", self_rating=5),
            ],
            preferences=LearningPreferencesInput(weekly_hours=15),
        )
        self.assertEqual(profile.learner_id, "valid_user_01")
        summary = profile.to_summary()
        self.assertEqual(summary.learner_id, "valid_user_01")
        self.assertEqual(summary.declared_skills_count, 2)
        self.assertEqual(len(summary.top_skills), 2)

    # 5. Invalid learner_id rejection
    def test_invalid_learner_id_rejection(self):
        """Verify that empty, whitespace, or invalid character learner_id values are rejected."""
        with self.assertRaises(ValidationError):
            OnboardingInputProfile(learner_id="   ", target_role="Backend Dev")
        with self.assertRaises(ValidationError):
            OnboardingInputProfile(learner_id="", target_role="Backend Dev")
        with self.assertRaises(ValidationError):
            OnboardingInputProfile(learner_id="invalid user!@#$ spaces", target_role="Backend Dev")

    # 6. Invalid skill rating rejection
    def test_invalid_skill_rating_rejection(self):
        """Verify skill ratings must be strictly between 1 and 5."""
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="Python", self_rating=0)
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="Python", self_rating=6)

    # 7. Invalid study hours rejection
    def test_invalid_study_hours_rejection(self):
        """Verify study hours are bounded strictly between 1 and 80."""
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(weekly_hours=0)
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(weekly_hours=85)

    # 8. Empty/invalid skill names rejection
    def test_empty_or_invalid_skill_names_rejection(self):
        """Verify skill names cannot be empty, pure whitespace, or single characters."""
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="", self_rating=3)
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="   ", self_rating=3)
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="C", self_rating=3)

    # 9. Missing optional fields handling
    def test_missing_optional_fields_handling(self):
        """Verify that omitting optional fields (interests, motivation, projects) is safely handled."""
        profile = OnboardingInputProfile(
            learner_id="minimal_user_01",
            target_role="Frontend Engineer",
        )
        self.assertEqual(profile.interests, [])
        self.assertIsNone(profile.motivation_statement)
        self.assertIsNone(profile.prior_projects_summary)
        self.assertIsNone(profile.stage)
        self.assertEqual(profile.get_effective_stage(), LearnerStage.BACHELOR)

        # Mock intelligence engine processes minimal profile safely
        prompt = build_onboarding_intelligence_prompt(profile)
        report = self.provider.analyze_learner_onboarding(profile, prompt)
        self.assertEqual(report.learner_id, "minimal_user_01")
        self.assertEqual(report.target_role, "Frontend Engineer")

    # 10. Mock provider deterministic response test
    def test_mock_provider_deterministic_response(self):
        """Verify MockLLMProvider is strictly deterministic and adheres to contract."""
        profile = OnboardingInputProfile(
            learner_id="deterministic_01",
            target_role="DevOps Engineer",
            declared_skills=[DeclaredSkill(skill_name="Linux", self_rating=4)],
        )
        report1 = self.provider.analyze_learner_onboarding(profile, "prompt")
        report2 = self.provider.analyze_learner_onboarding(profile, "prompt")

        self.assertEqual(report1.learner_id, report2.learner_id)
        self.assertEqual(report1.readiness.overall_readiness_score, report2.readiness.overall_readiness_score)
        self.assertEqual(report1.readiness.readiness_tier, report2.readiness.readiness_tier)

    # 11. API /analyze endpoint test
    def test_api_onboarding_analyze_endpoint(self):
        """Verify HTTP POST /api/v1/onboarding/analyze endpoint works end-to-end."""
        payload = {
            "learner_id": "test_http_user",
            "stage": "bachelor",
            "academic_program": "Information Technology",
            "current_semester": 2,
            "target_role": "Backend Engineer",
            "declared_skills": [
                {
                    "skill_name": "Python",
                    "self_rating": 3,
                    "category": "programming",
                },
                {
                    "skill_name": "PostgreSQL",
                    "self_rating": 2,
                    "category": "tools",
                },
            ],
            "interests": ["REST APIs", "Database Optimization"],
            "preferences": {
                "preferred_medium": "interactive",
                "pace": "moderate",
                "weekly_hours": 10,
                "practical_vs_theory_ratio": 0.7,
            },
            "motivation_statement": "Building scalable backend microservices.",
        }

        response = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        report = LearnerIntelligenceReport.model_validate(data)
        self.assertEqual(report.learner_id, "test_http_user")
        self.assertEqual(report.target_role, "Backend Engineer")
        self.assertIsNotNone(report.skill_analysis)
        self.assertIsNotNone(report.knowledge_analysis)
        self.assertIsNotNone(report.learning_style)
        self.assertIsNotNone(report.career_goals)
        self.assertIsNotNone(report.motivation)
        self.assertIsNotNone(report.readiness)

    # 12. API /validate-profile endpoint test
    def test_api_validate_profile_endpoint(self):
        """Verify HTTP POST /api/v1/onboarding/validate-profile performs preflight check without calling LLM."""
        payload_with_skills = {
            "learner_id": "preflight_user_01",
            "stage": "master",
            "academic_program": "Computer Science",
            "target_role": "Cloud Architect",
            "declared_skills": [
                {"skill_name": "AWS", "self_rating": 4, "category": "tools"},
                {"skill_name": "Kubernetes", "self_rating": 4, "category": "tools"},
                {"skill_name": "Go", "self_rating": 4, "category": "programming"},
                {"skill_name": "Distributed Systems", "self_rating": 4, "category": "theory"},
            ],
            "preferences": {"weekly_hours": 20},
        }
        res1 = self.client.post("/api/v1/onboarding/validate-profile", json=payload_with_skills)
        self.assertEqual(res1.status_code, 200)
        result1 = LearnerProfileValidationResult.model_validate(res1.json())
        self.assertTrue(result1.is_valid)
        self.assertEqual(result1.declared_skills_count, 4)
        self.assertEqual(result1.estimated_readiness_indicator, "accelerated_curriculum")

        # Test profile with zero skills flags issue
        payload_no_skills = {
            "learner_id": "preflight_user_02",
            "stage": "bachelor",
            "target_role": "Junior Developer",
            "declared_skills": [],
            "preferences": {"weekly_hours": 3},  # < 5 hours
        }
        res2 = self.client.post("/api/v1/onboarding/validate-profile", json=payload_no_skills)
        self.assertEqual(res2.status_code, 200)
        result2 = LearnerProfileValidationResult.model_validate(res2.json())
        self.assertEqual(result2.declared_skills_count, 0)
        self.assertTrue(len(result2.issues) >= 2)
        self.assertEqual(result2.estimated_readiness_indicator, "foundational_scaffolding")

    # 13. Backward-compatible /learner-intelligence endpoint test
    def test_backward_compatible_learner_intelligence_endpoint(self):
        """Verify /api/v1/onboarding/learner-intelligence alias endpoint behaves identically."""
        payload = {
            "learner_id": "compat_user_01",
            "stage": "graduate",
            "target_role": "Data Analyst",
            "declared_skills": [{"skill_name": "Excel", "self_rating": 4, "category": "tools"}],
        }
        response = self.client.post("/api/v1/onboarding/learner-intelligence", json=payload)
        self.assertEqual(response.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(response.json())
        self.assertEqual(report.learner_id, "compat_user_01")
        self.assertEqual(report.target_role, "Data Analyst")

    # 14. Malformed/incomplete LLM response normalization test
    def test_llm_response_extraction_and_normalization(self):
        """Verify JSON fence extraction and defensive alias repair for imperfect LLM output."""
        raw_llm_output = """
        Here is the synthesized intelligence report for the student:
        ```json
        {
            "executiveSummary": "Strong candidate with solid foundations.",
            "skillAnalysis": {
                "summary": "Demonstrates solid coding basics.",
                "proficiency": "intermediate",
                "strengths": ["Python", "Algorithms"],
                "gaps": ["Docker"]
            },
            "careerGoals": {
                "target_role": "Software Engineer",
                "alignment_score": "80%",
                "milestones": ["Milestone 1", "Milestone 2"]
            },
            "readinessAssessment": {
                "score": "0.75",
                "tier": "MODERATE",
                "entry_level": "intermediate"
            }
        }
        ```
        Hope this analysis is helpful!
        """
        extracted = extract_json_payload(raw_llm_output)
        self.assertTrue(extracted.startswith("{"))
        self.assertTrue(extracted.endswith("}"))

        import json
        data = json.loads(extracted)
        dummy_profile = OnboardingInputProfile(
            learner_id="test_repair_user",
            target_role="Backend Developer",
        )
        normalized = normalize_intelligence_dict(data, dummy_profile)

        # Confirm aliases were mapped cleanly
        self.assertIn("skill_analysis", normalized)
        self.assertIn("career_goals", normalized)
        self.assertIn("readiness", normalized)
        self.assertEqual(normalized["learner_id"], "test_repair_user")
        self.assertEqual(normalized["target_role"], "Backend Developer")

        # Pydantic validates cleanly on repaired dictionary
        report = LearnerIntelligenceReport.model_validate(normalized)
        self.assertEqual(report.learner_id, "test_repair_user")
        self.assertEqual(report.readiness.readiness_tier, ReadinessTier.MODERATE)
        self.assertAlmostEqual(report.career_goals.role_alignment_score, 0.8)

    # 15. Rate-limit and error handling test
    def test_provider_error_and_rate_limit_handling(self):
        """Verify controlled HTTP exception mapping when LLM provider experiences rate-limit or errors."""
        payload = {
            "learner_id": "error_test_user",
            "target_role": "Backend Dev",
        }

        # 1. Simulate 429 Rate Limit
        with patch.object(
            MockLLMProvider,
            "analyze_learner_onboarding",
            side_effect=LLMProviderError("Rate limit exceeded", status_code=429),
        ):
            res_429 = self.client.post("/api/v1/onboarding/analyze", json=payload)
            self.assertEqual(res_429.status_code, 429)
            self.assertIn("Rate limit", res_429.json()["detail"])

        # 2. Simulate 502 Bad Gateway from unparseable LLM output
        with patch.object(
            MockLLMProvider,
            "analyze_learner_onboarding",
            side_effect=LLMParseError("Malformed output", status_code=502),
        ):
            res_502 = self.client.post("/api/v1/onboarding/analyze", json=payload)
            self.assertEqual(res_502.status_code, 502)
            self.assertIn("Malformed output", res_502.json()["detail"])

    # 16. Regression Test: Missing learner information is NOT hallucinated
    def test_grounding_missing_learner_information(self):
        """Verify that when study time, ratio, skills, and projects are missing,

        the engine does NOT hallucinate 10h/week, 0.70 ratio, or phantom projects/skills.
        """
        payload = {
            "learner_id": "test_grounding_user",
            "target_role": "Frontend Engineer",
        }

        # Validate prompt reflects absence
        profile = OnboardingInputProfile.model_validate(payload)
        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("[NONE DECLARED - DO NOT INVENT OR ASSUME ANY DECLARED SKILLS]", prompt)
        self.assertIn("[NOT PROVIDED - DO NOT ASSUME 10h/week OR ANY FIXED HOURS]", prompt)
        self.assertIn("[NOT PROVIDED - information unavailable; do NOT assume any ratio or write 'default to balanced', state clearly that this information is unavailable]", prompt)
        self.assertIn("[NONE PROVIDED - DO NOT INVENT PRIOR PROJECTS]", prompt)
        self.assertIn("[NOT PROVIDED - academic stage is unspecified; do NOT assume bachelor or enrolled university student status]", prompt)

        # Validate API response
        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())

        # Estimated timeline must be None since weekly hours were not specified
        self.assertIsNone(report.career_goals.estimated_timeline_months)

        # Core strengths must not hallucinate study time commitment
        for s in report.skill_analysis.core_strengths:
            self.assertNotIn("10h/week", s.lower())
            self.assertNotIn("10 hours", s.lower())

        # Theoretical vs applied balance must clearly state information is unavailable
        balance_text = report.knowledge_analysis.theoretical_vs_applied_balance
        self.assertNotIn("0.70", balance_text)
        self.assertNotIn("0.7", balance_text)
        self.assertNotIn("default to balanced", balance_text.lower())
        self.assertIn("unavailable", balance_text.lower())

        # Executive summary must not hallucinate 10h/week, 0.70, or university enrollment
        self.assertNotIn("10h/week", report.executive_summary.lower())
        self.assertNotIn("0.70", report.executive_summary)
        self.assertNotIn("bachelor's degree student", report.executive_summary.lower())

    # 17. Regression Test: Concept mastery ingestion and grounding
    def test_grounding_with_concept_mastery(self):
        """Verify that concept_mastery scores are ingested and drive strengths and gaps."""
        payload = {
            "learner_id": "concept_user_01",
            "target_role": "Backend Engineer",
            "concept_mastery": {
                "FastAPI": 0.95,
                "Kubernetes": 0.30,
            },
        }

        profile = OnboardingInputProfile.model_validate(payload)
        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("FastAPI: 0.95", prompt)
        self.assertIn("Kubernetes: 0.30", prompt)

        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())

        # High mastery concept appears in strengths
        strengths_str = " ".join(report.skill_analysis.core_strengths)
        self.assertIn("FastAPI", strengths_str)

        # Low mastery concept appears in gaps or foundation topics
        gaps_and_foundations = (
            " ".join(report.skill_analysis.critical_skill_gaps)
            + " "
            + " ".join(report.knowledge_analysis.recommended_foundation_topics)
        )
        self.assertIn("Kubernetes", gaps_and_foundations)

    # 18. Regression Test: Weak and strong topics ingestion
    def test_grounding_with_weak_and_strong_topics(self):
        """Verify that weak_topics and strong_topics are prioritized in the report."""
        payload = {
            "learner_id": "topics_user_01",
            "target_role": "Systems Engineer",
            "weak_topics": ["Distributed Consensus", "Memory Alignment"],
            "strong_topics": ["Pointer Arithmetic"],
        }

        profile = OnboardingInputProfile.model_validate(payload)
        prompt = build_onboarding_intelligence_prompt(profile)
        self.assertIn("Distributed Consensus", prompt)
        self.assertIn("Pointer Arithmetic", prompt)

        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())

        # Strong topics in core strengths
        self.assertIn("Pointer Arithmetic", report.skill_analysis.core_strengths)

        # Weak topics in critical gaps and foundation topics
        self.assertIn("Distributed Consensus", report.skill_analysis.critical_skill_gaps)
        self.assertIn("Memory Alignment", report.skill_analysis.critical_skill_gaps)

    # 19. Regression Test: Career goal synonym for target role
    def test_grounding_with_career_goal_alias(self):
        """Verify that providing career_goal in place of target_role works seamlessly."""
        payload = {
            "learner_id": "career_user_01",
            "career_goal": "AI Research Scientist",
        }
        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())
        self.assertEqual(report.target_role, "AI Research Scientist")
        self.assertEqual(report.career_goals.target_role, "AI Research Scientist")

    # 20. Regression Test: Nested LearnerState integration
    def test_grounding_with_nested_learner_state(self):
        """Verify that passing an active LearnerState sub-object forwards all context."""
        payload = {
            "learner_id": "state_user_01",
            "learner_state": {
                "learner_id": "state_user_01",
                "career_goal": "Principal Database Engineer",
                "concept_mastery": {"Query Planning": 0.90, "Cache Invalidation": 0.20},
                "weak_topics": ["B-Tree Concurrency"],
                "strong_topics": ["ACID Transactions"],
                "learning_preference": "hands-on",
            },
        }
        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())

        self.assertEqual(report.target_role, "Principal Database Engineer")
        self.assertEqual(report.learning_style.dominant_modality, "hands-on")
        self.assertIn("ACID Transactions", report.skill_analysis.core_strengths)
        self.assertIn("B-Tree Concurrency", report.skill_analysis.critical_skill_gaps)

    # 21. Regression Test: Known learner full profile is accurately used
    def test_grounding_known_learner_full_profile(self):
        """Verify that when all fields are provided, they are faithfully utilized without assumption."""
        payload = {
            "learner_id": "full_user_01",
            "stage": "master",
            "academic_program": "Robotics Engineering",
            "current_semester": 2,
            "target_role": "Robotics Software Engineer",
            "declared_skills": [
                {"skill_name": "C++", "self_rating": 4, "category": "programming"},
                {"skill_name": "ROS2", "self_rating": 4, "category": "framework"},
            ],
            "interests": ["Sensor Fusion", "SLAM"],
            "preferences": {
                "preferred_medium": "hands-on",
                "pace": "fast-track",
                "weekly_hours": 20,
                "practical_vs_theory_ratio": 0.85,
            },
            "motivation_statement": "Autonomous navigation for mobile robots.",
            "prior_projects_summary": "Built LiDAR-based obstacle avoidance robot in C++.",
        }
        res = self.client.post("/api/v1/onboarding/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        report = LearnerIntelligenceReport.model_validate(res.json())

        self.assertEqual(report.target_role, "Robotics Software Engineer")
        self.assertEqual(report.learning_style.dominant_modality, "hands-on")
        self.assertIsNotNone(report.career_goals.estimated_timeline_months)
        self.assertIn("C++", report.skill_analysis.core_strengths)
        self.assertIn("ROS2", report.skill_analysis.core_strengths)


if __name__ == "__main__":
    unittest.main()

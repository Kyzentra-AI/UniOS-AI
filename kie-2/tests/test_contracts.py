import unittest
from pydantic import ValidationError
from app.schemas import (
    LearnerStage,
    ConfidenceLevel,
    LearnerState,
    NormalizedLearningContext,
    TeachingStrategy,
    LessonBlockType,
)
from app.core.config import settings
from app.schemas.memory_context import RelevantMemoryContext
from app.schemas.memory import PreferenceMemory, FrictionMemory, GoalMemory
from app.schemas.memory_events import MemoryUpdateEvent, MemoryEventType, EvidenceSource
from app.services import (
    build_pedagogy_prompt,
    build_lesson_prompt,
    get_llm_provider,
    get_memory_repository,
    get_memory_engine,
)


class TestSprint1IntelligenceHarness(unittest.TestCase):
    """Evaluation and contract test harness for AI/ML-2 Sprint-1 and Sprint-2 contracts."""

    @classmethod
    def setUpClass(cls):
        cls._original_provider = settings.LLM_PROVIDER
        settings.LLM_PROVIDER = "mock"

    @classmethod
    def tearDownClass(cls):
        settings.LLM_PROVIDER = cls._original_provider

    def setUp(self):
        self.provider = get_llm_provider(force_mock=True)

    def test_bachelor_learner_contract(self):
        """Verify Bachelor stage normalized context and foundational prompt generation."""
        state = LearnerState(
            learner_id="bachelor_01",
            stage=LearnerStage.BACHELOR,
            confidence=ConfidenceLevel.LOW,
            weak_topics=["pointers"],
            concept_mastery={"syntax": 0.9, "pointers": 0.2},
        )
        ctx = NormalizedLearningContext(
            topic="Memory Pointers",
            objective="Understand memory addresses and dereferencing",
            learner_state=state,
        )

        prompt = build_pedagogy_prompt(ctx)
        self.assertIn("Bachelor's Degree", prompt)
        self.assertIn("Memory Pointers", prompt)

        decision = self.provider.generate_pedagogy_decision(prompt)
        self.assertIsInstance(decision.strategy, TeachingStrategy)

    def test_master_learner_contract(self):
        """Verify Master's stage normalized context and specialized prompt generation."""
        state = LearnerState(
            learner_id="master_01",
            stage=LearnerStage.MASTER,
            confidence=ConfidenceLevel.HIGH,
            concept_mastery={"distributed_systems": 0.8},
        )
        ctx = NormalizedLearningContext(
            topic="Raft Consensus",
            objective="Evaluate leader election and log replication",
            learner_state=state,
        )

        prompt = build_pedagogy_prompt(ctx)
        self.assertIn("Master's Degree", prompt)
        self.assertIn("Raft Consensus", prompt)

    def test_graduate_learner_contract(self):
        """Verify Graduate stage normalized context and career/interview prompt generation."""
        state = LearnerState(
            learner_id="grad_01",
            stage=LearnerStage.GRADUATE,
            career_goal="Backend Engineer",
            weak_topics=["system_design"],
        )
        ctx = NormalizedLearningContext(
            topic="System Design Mock",
            objective="Design rate limiter for high-traffic API",
            learner_state=state,
        )

        prompt = build_pedagogy_prompt(ctx)
        self.assertIn("Recent Graduate", prompt)
        self.assertIn("System Design Mock", prompt)

    def test_learner_identity_contract_and_boundary(self):
        """Verify LearnerIdentity contract validation and architectural boundaries."""
        from app.schemas import LearnerIdentity

        # Valid identity
        identity = LearnerIdentity(
            learner_id="user_abc-123.test",
            stage=LearnerStage.BACHELOR,
            academic_program="B.Tech CS",
            current_semester=3,
            institution="State University",
        )
        self.assertEqual(identity.learner_id, "user_abc-123.test")
        self.assertEqual(identity.stage, LearnerStage.BACHELOR)

        # Invalid learner_id: empty or whitespace
        with self.assertRaises(ValidationError):
            LearnerIdentity(learner_id="   ")

        # Invalid learner_id: invalid characters (e.g. spaces or quotes)
        with self.assertRaises(ValidationError):
            LearnerIdentity(learner_id="user 123 with space")

    def test_declared_skill_contract_validations(self):
        """Verify strict validations on skill names and ratings."""
        from app.schemas import DeclaredSkill, SkillCategory

        # Valid skill
        skill = DeclaredSkill(
            skill_name="Python",
            self_rating=4,
            category=SkillCategory.PROGRAMMING,
        )
        self.assertEqual(skill.skill_name, "Python")
        self.assertEqual(skill.self_rating, 4)

        # Invalid rating: below 1 or above 5
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="Go", self_rating=0)
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="Go", self_rating=6)

        # Invalid skill_name: empty, whitespace, or less than 2 characters
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="   ", self_rating=3)
        with self.assertRaises(ValidationError):
            DeclaredSkill(skill_name="A", self_rating=3)

    def test_learning_preferences_contract_validations(self):
        """Verify study hours and ratio boundaries."""
        from app.schemas import LearningPreferencesInput

        # Valid preferences
        pref = LearningPreferencesInput(weekly_hours=20, practical_vs_theory_ratio=0.8)
        self.assertEqual(pref.weekly_hours, 20)

        # Invalid weekly_hours: 0 or > 80
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(weekly_hours=0)
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(weekly_hours=85)

        # Invalid practical_vs_theory_ratio
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(practical_vs_theory_ratio=1.5)
        with self.assertRaises(ValidationError):
            LearningPreferencesInput(practical_vs_theory_ratio=-0.2)

    def test_intelligence_schema_defensive_normalization(self):
        """Verify defensive normalization of LLM returns (casing, percentages, comma lists)."""
        from app.schemas import (
            ReadinessAssessment,
            ReadinessTier,
            SkillAnalysis,
            CareerGoalProfile,
        )

        # 1. Readiness tier case-insensitivity & synonym repair
        assessment = ReadinessAssessment.model_validate({
            "overall_readiness_score": "85%",
            "readiness_tier": "HIGH",
            "recommended_entry_level": "advanced",
            "onboarding_recommendations": "Step 1, Step 2; Step 3",
        })
        self.assertEqual(assessment.readiness_tier, ReadinessTier.HIGH)
        self.assertAlmostEqual(assessment.overall_readiness_score, 0.85)
        self.assertEqual(len(assessment.onboarding_recommendations), 3)

        # Clamping slight float noise
        assessment_clamped = ReadinessAssessment.model_validate({
            "overall_readiness_score": 1.05,
            "readiness_tier": "needs-scaffolding",
        })
        self.assertEqual(assessment_clamped.overall_readiness_score, 1.0)
        self.assertEqual(assessment_clamped.readiness_tier, ReadinessTier.NEEDS_SCAFFOLDING)

        # 2. Skill analysis list normalization from comma string
        skill_analysis = SkillAnalysis.model_validate({
            "core_strengths": "Python, SQL, System Architecture",
            "critical_skill_gaps": ["Docker", "Kubernetes"],
        })
        self.assertEqual(len(skill_analysis.core_strengths), 3)
        self.assertIn("Python", skill_analysis.core_strengths)

        # 3. Genuine validation failure when type is completely unparseable
        with self.assertRaises(ValidationError):
            ReadinessAssessment.model_validate({
                "overall_readiness_score": "unparseable_string",
                "readiness_tier": "HIGH",
            })

    def test_structured_lesson_generation_and_boundary_rules(self):
        """Verify that lesson blocks are structured and strictly contain NO raw UI/HTML/React code."""
        state = LearnerState(stage=LearnerStage.BACHELOR)
        ctx = NormalizedLearningContext(
            topic="Binary Search",
            objective="Master O(log n) search",
            learner_state=state,
        )

        decision = self.provider.generate_pedagogy_decision(build_pedagogy_prompt(ctx))
        lesson = self.provider.generate_lesson(
            prompt=build_lesson_prompt(ctx, decision),
            context_id=ctx.context_id,
            topic=ctx.topic,
        )

        # Check lesson structure
        self.assertGreaterEqual(len(lesson.blocks), 1)
        block_types = [b.type for b in lesson.blocks]
        self.assertIn(LessonBlockType.OBJECTIVE, block_types)
        self.assertIn(LessonBlockType.VISUAL_SPEC, block_types)

        # Non-negotiable boundary check: strictly NO raw UI code
        forbidden_tags = [
            "<div",
            "<html",
            "<script",
            "import React",
            "export default function",
        ]
        for block in lesson.blocks:
            for forbidden in forbidden_tags:
                self.assertNotIn(
                    forbidden,
                    block.content,
                    f"Boundary violation: Found raw UI code '{forbidden}' in block content!",
                )

    def test_invalid_context_rejection(self):
        """Verify that invalid payloads without required fields raise ValidationError."""
        with self.assertRaises(ValidationError):
            # Missing required fields 'topic', 'objective', 'learner_state'
            NormalizedLearningContext.model_validate({})

    def test_sprint1_learning_api_endpoints(self):
        """Verify Sprint 1 HTTP POST /api/v1/learning/plan-lesson remains fully operational."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        payload = {
            "context_id": "ctx_test_001",
            "topic": "Graph Traversal",
            "objective": "Understand BFS vs DFS trade-offs",
            "learner_state": {
                "learner_id": "bach_graph_01",
                "stage": "bachelor",
                "confidence": "medium",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "Graph Traversal")
        self.assertGreaterEqual(len(data["blocks"]), 1)

    def test_sprint1_generate_lesson_alias_endpoint(self):
        """Verify alias HTTP POST /api/v1/learning/generate-lesson functions identically and returns 200."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        payload = {
            "context_id": "ctx_test_002",
            "topic": "Dynamic Programming",
            "objective": "Understand memoization vs tabulation",
            "learner_state": {
                "learner_id": "bach_dp_01",
                "stage": "bachelor",
                "confidence": "low",
            },
        }
        response = client.post("/api/v1/learning/generate-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "Dynamic Programming")
        self.assertEqual(data["context_id"], "ctx_test_002")
        self.assertGreaterEqual(len(data["blocks"]), 1)

    def test_generate_lesson_provider_error_handling(self):
        """Verify provider errors are caught cleanly and return 502 instead of unhandled 500."""
        from unittest.mock import patch
        from fastapi.testclient import TestClient
        from app.main import app
        from app.services import LLMParseError

        client = TestClient(app)
        payload = {
            "context_id": "ctx_err_001",
            "topic": "Error Handling",
            "objective": "Verify resilience",
            "learner_state": {
                "learner_id": "err_user",
                "stage": "bachelor",
                "confidence": "low",
            },
        }
        with patch.object(
            self.provider.__class__,
            "generate_lesson",
            side_effect=LLMParseError("Simulated parse failure", raw_content="malformed json"),
        ):
            response = client.post("/api/v1/learning/generate-lesson", json=payload)
            self.assertEqual(response.status_code, 502)
            self.assertIn("Simulated parse failure", response.json()["detail"])

    # A. Existing request without memory_context still returns 200 (backward compatibility)
    def test_lesson_planning_without_memory_context_backward_compatible(self):
        """Verify POST /api/v1/learning/plan-lesson without memory_context returns 200."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        payload = {
            "context_id": "ctx_compat_001",
            "topic": "Recursion Basics",
            "objective": "Understand base cases and recursive calls",
            "learner_state": {
                "learner_id": "compat_user_no_mem",
                "stage": "bachelor",
                "confidence": "medium",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "Recursion Basics")
        self.assertIn("pedagogy_decision", data)
        self.assertGreater(len(data["blocks"]), 0)

    # B. Explicit memory_context is accepted and used
    def test_lesson_planning_with_explicit_memory_context(self):
        """Verify explicit memory_context passed in payload is recognized and informs pedagogy."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        payload = {
            "context_id": "ctx_explicit_mem_001",
            "topic": "Binary Search",
            "objective": "Understand search space halving",
            "learner_state": {
                "learner_id": "explicit_mem_student",
                "stage": "bachelor",
                "confidence": "low",
            },
            "memory_context": {
                "learner_id": "explicit_mem_student",
                "topic": "Binary Search",
                "relevant_preferences": {
                    "dominant_modality": "interactive",
                    "pacing": "standard",
                    "practical_vs_theory_ratio": 0.85,
                },
                "relevant_friction": [
                    {
                        "topic": "Binary Search",
                        "struggle_type": "conceptual_gap",
                        "severity": "high",
                        "mistake_count": 3,
                        "unresolved": True,
                        "recommended_intervention": "Visual breakdown of boundary conditions",
                    }
                ],
                "active_goal": {
                    "primary_target_role": "Backend Engineer",
                },
                "recommended_pedagogical_mode": "interactive",
                "rationale": "High-severity friction detected on Binary Search. Immediate remediation required.",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        pedagogy = data["pedagogy_decision"]
        # Active struggle on Binary Search triggers REMEDIATION strategy
        self.assertEqual(pedagogy["strategy"], TeachingStrategy.REMEDIATION.value)
        self.assertEqual(pedagogy["presentation_mode"], "interactive")

    # C. learner_id + no explicit memory_context automatically retrieves relevant memory
    def test_lesson_planning_auto_retrieves_memory_from_learner_id(self):
        """Verify that a learner with existing memory has relevant context auto-retrieved."""
        from fastapi.testclient import TestClient
        from app.main import app

        learner_id = "auto_retrieve_user_001"
        repo = get_memory_repository()
        repo.clear(learner_id)
        engine = get_memory_engine()

        # Seed memory preference for interactive mode
        engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.PREFERENCE_OBSERVED,
                evidence_source=EvidenceSource.EXPLICIT,
                payload={"dominant_modality": "interactive"},
            )
        )

        client = TestClient(app)
        payload = {
            "context_id": "ctx_auto_001",
            "topic": "Sorting Algorithms",
            "objective": "Understand Quicksort pivot selection",
            "learner_state": {
                "learner_id": learner_id,
                "stage": "bachelor",
                "confidence": "medium",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        pedagogy = data["pedagogy_decision"]
        # Automatically inferred presentation_mode from retrieved memory preference
        self.assertEqual(pedagogy["presentation_mode"], "interactive")

    # D. Learner with active friction receives a context-aware pedagogy decision (remediation)
    def test_lesson_planning_with_active_friction_triggers_remediation(self):
        """Verify active friction in memory automatically steers pedagogy to REMEDIATION."""
        from fastapi.testclient import TestClient
        from app.main import app

        learner_id = "struggling_student_001"
        repo = get_memory_repository()
        repo.clear(learner_id)
        engine = get_memory_engine()

        # Record friction on Python Functions
        engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.TOPIC_STRUGGLED,
                evidence_source=EvidenceSource.OBSERVED,
                confidence_score=0.95,
                payload={"topic": "Python Functions", "struggle_type": "conceptual_gap"},
            )
        )
        engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.REPEATED_MISTAKE,
                evidence_source=EvidenceSource.OBSERVED,
                confidence_score=0.95,
                payload={"topic": "Python Functions"},
            )
        )

        client = TestClient(app)
        payload = {
            "context_id": "ctx_fric_001",
            "topic": "Python Functions",
            "objective": "Master function scoping and closures",
            "learner_state": {
                "learner_id": learner_id,
                "stage": "bachelor",
                "confidence": "low",
                "weak_topics": ["Python Functions"],
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        pedagogy = data["pedagogy_decision"]
        self.assertEqual(pedagogy["strategy"], TeachingStrategy.REMEDIATION.value)
        self.assertIn("remediation", pedagogy["rationale"].lower())

    # E. Unknown learner does not crash lesson planning
    def test_lesson_planning_unknown_learner_no_crash(self):
        """Verify that querying a brand new, unknown learner handles baseline defaults safely."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        payload = {
            "context_id": "ctx_unknown_001",
            "topic": "Linear Algebra",
            "objective": "Vector dot product",
            "learner_state": {
                "learner_id": "unknown_student_xyz_9999",
                "stage": "bachelor",
                "confidence": "medium",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "Linear Algebra")
        self.assertGreater(len(data["blocks"]), 0)

    # F. Empty memory does not crash lesson planning
    def test_lesson_planning_empty_memory_no_crash(self):
        """Verify registered learner with empty memory history plans lessons smoothly."""
        from fastapi.testclient import TestClient
        from app.main import app

        learner_id = "empty_mem_user_001"
        repo = get_memory_repository()
        repo.clear(learner_id)
        # Pre-create blank container
        engine = get_memory_engine()
        engine.get_or_create_memory(learner_id)

        client = TestClient(app)
        payload = {
            "context_id": "ctx_empty_mem_001",
            "topic": "Object Oriented Programming",
            "objective": "Polymorphism and inheritance",
            "learner_state": {
                "learner_id": learner_id,
                "stage": "bachelor",
                "confidence": "high",
            },
        }
        response = client.post("/api/v1/learning/plan-lesson", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "Object Oriented Programming")
        self.assertGreater(len(data["blocks"]), 0)


if __name__ == "__main__":
    unittest.main()

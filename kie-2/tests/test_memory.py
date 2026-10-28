import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.memory import (
    PreferenceMemory,
    ConversationMemory,
    LearningHistoryMemory,
    ProjectMemory,
    GoalMemory,
    AchievementMemory,
    FrictionMemory,
    LearnerMemory,
)
from app.schemas.memory_events import (
    MemoryEventType,
    EvidenceSource,
    MemoryUpdateEvent,
    MemoryUpdateResult,
    MemorySeedResult,
)
from app.schemas.intelligence import (
    LearnerIntelligenceReport,
    SkillAnalysis,
    KnowledgeAnalysis,
    LearningStyleProfile,
    CareerGoalProfile,
    MotivationProfile,
    ReadinessAssessment,
    ReadinessTier,
)
from app.schemas.learner import LearnerStage
from app.schemas.memory_context import (
    RelevantMemoryQuery,
    RelevantMemoryContext,
    RoadmapStatus,
    RoadmapRecommendedAction,
    RoadmapAdaptationContext,
)
from app.services.memory_repository import InMemoryMemoryRepository
from app.services.memory_engine import MemoryEngine


class TestSprint3MemoryIntelligence(unittest.TestCase):
    """Evaluation and contract test harness for AI/ML-2 Sprint-3:
    Memory Engine + Context Retrieval + Memory Update Logic.
    """

    def setUp(self):
        # Isolated in-memory repository per test to avoid state pollution
        self.repo = InMemoryMemoryRepository()
        self.engine = MemoryEngine(repository=self.repo)
        self.client = TestClient(app)

    # 1. Memory schema validation
    def test_01_memory_schema_validation(self):
        """Verify schema boundaries, defaults, and normalizers across memory models."""
        pref = PreferenceMemory(
            dominant_modality="INTERACTIVE ",
            pacing="SCAFFOLDED",
            practical_vs_theory_ratio=0.85,
        )
        self.assertEqual(pref.dominant_modality, "interactive")
        self.assertEqual(pref.pacing, "scaffolded")
        self.assertAlmostEqual(pref.practical_vs_theory_ratio, 0.85)

        # Invalid ratio bounds
        with self.assertRaises(ValidationError):
            PreferenceMemory(practical_vs_theory_ratio=1.5)
        with self.assertRaises(ValidationError):
            PreferenceMemory(practical_vs_theory_ratio=-0.1)

        # Learning history score bounds
        with self.assertRaises(ValidationError):
            LearningHistoryMemory(topic="Recursion", assessment_score=1.2)

        # Friction memory defaults
        friction = FrictionMemory(topic="Pointers")
        self.assertEqual(friction.mistake_count, 1)
        self.assertTrue(friction.unresolved)
        self.assertEqual(friction.severity, "moderate")

    # 2. Preference memory update
    def test_02_preference_memory_update(self):
        """Verify explicit and observed preference updates."""
        learner_id = "test_pref_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.PREFERENCE_OBSERVED,
            evidence_source=EvidenceSource.EXPLICIT,
            confidence_score=1.0,
            payload={
                "dominant_modality": "hands-on",
                "pacing": "accelerated",
                "practical_vs_theory_ratio": 0.9,
            },
        )
        result = self.engine.record_event(event)
        self.assertTrue(result.success)
        self.assertIn("preferences", result.updated_facets)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(memory.preferences.dominant_modality, "hands-on")
        self.assertEqual(memory.preferences.pacing, "accelerated")
        self.assertAlmostEqual(memory.preferences.practical_vs_theory_ratio, 0.9)

    # 3. Conversation memory update
    def test_03_conversation_memory_update(self):
        """Verify recording of learner dialogues and question signals."""
        learner_id = "test_conv_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.CONVERSATION_SIGNAL,
            evidence_source=EvidenceSource.OBSERVED,
            payload={
                "topic": "Async Programming",
                "question_summary": "What is the difference between coroutine and task?",
                "confusion_points": ["event loop blocking"],
                "expressed_sentiment": "curious",
            },
        )
        result = self.engine.record_event(event)
        self.assertTrue(result.success)
        self.assertIn("conversations", result.updated_facets)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.conversations), 1)
        self.assertEqual(memory.conversations[0].topic, "Async Programming")
        self.assertIn("event loop blocking", memory.conversations[0].confusion_points)

    # 4. Learning history update
    def test_04_learning_history_update(self):
        """Verify recording of completed lessons and assessment attempts."""
        learner_id = "test_hist_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.LESSON_COMPLETED,
            evidence_source=EvidenceSource.OBSERVED,
            payload={
                "topic": "Binary Search",
                "lesson_id": "lsn_bs_01",
                "score": 0.85,
                "time_spent_minutes": 25,
            },
        )
        result = self.engine.record_event(event)
        self.assertTrue(result.success)
        self.assertIn("learning_history", result.updated_facets)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.learning_history), 1)
        self.assertEqual(memory.learning_history[0].topic, "Binary Search")
        self.assertAlmostEqual(memory.learning_history[0].assessment_score, 0.85)

    # 5. Project memory update
    def test_05_project_memory_update(self):
        """Verify project start and completion lifecycle with achievement auto-granting."""
        learner_id = "test_proj_user"
        # Start project
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.PROJECT_STARTED,
                payload={
                    "title": "REST API with FastAPI",
                    "technologies_used": ["FastAPI", "Python", "Docker"],
                    "complexity": "intermediate",
                },
            )
        )
        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.projects), 1)
        self.assertEqual(memory.projects[0].status, "started")

        # Complete project
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.PROJECT_COMPLETED,
                payload={"title": "REST API with FastAPI"},
            )
        )
        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(memory.projects[0].status, "completed")
        self.assertIsNotNone(memory.projects[0].completed_at)
        # Verify achievement created
        self.assertTrue(any("Project Builder" in a.title for a in memory.achievements))

    # 6. Goal update and historical tracking
    def test_06_goal_update_and_history(self):
        """Verify career goal update and preservation of change history."""
        learner_id = "test_goal_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.GOAL_UPDATED,
            payload={
                "target_role": "Machine Learning Engineer",
                "target_timeline_months": 8,
                "milestones": ["Python & Math Foundations", "PyTorch", "MLOps"],
                "reason": "Interest shifted towards AI engineering",
            },
        )
        result = self.engine.record_event(event)
        self.assertIn("goals", result.updated_facets)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(memory.goals.primary_target_role, "Machine Learning Engineer")
        self.assertEqual(memory.goals.target_timeline_months, 8)
        self.assertEqual(len(memory.goals.milestones), 3)
        self.assertEqual(len(memory.goals.goal_change_history), 1)
        self.assertEqual(memory.goals.goal_change_history[0]["previous_role"], "Software Engineer")

    # 7. Achievement update
    def test_07_achievement_update(self):
        """Verify manual or platform-awarded achievements."""
        learner_id = "test_ach_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.ACHIEVEMENT_EARNED,
            payload={
                "title": "7-Day Study Streak",
                "category": "streak",
                "description": "Logged study sessions 7 days consecutively.",
            },
        )
        result = self.engine.record_event(event)
        self.assertIn("achievements", result.updated_facets)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.achievements), 1)
        self.assertEqual(memory.achievements[0].category, "streak")

    # 8. Friction update and escalation
    def test_08_friction_update_and_escalation(self):
        """Verify friction tracking on struggle signals."""
        learner_id = "test_fric_user"
        event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.FRICTION_SIGNAL,
            confidence_score=0.9,
            payload={
                "topic": "Dynamic Programming",
                "struggle_type": "conceptual_gap",
                "details": "Struggled with optimal substructure formulation",
            },
        )
        result = self.engine.record_event(event)
        self.assertTrue(result.friction_level_updated)

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.friction), 1)
        self.assertEqual(memory.friction[0].topic, "Dynamic Programming")
        self.assertTrue(memory.friction[0].unresolved)

    # 9. Multiple updates for the same learner
    def test_09_multiple_updates_same_learner(self):
        """Verify that multiple consecutive events across facets properly aggregate."""
        learner_id = "multi_update_user"
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                payload={"topic": "Variables", "score": 0.9},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                payload={"topic": "Control Flow", "score": 0.85},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.PREFERENCE_OBSERVED,
                payload={"dominant_modality": "interactive"},
            )
        )

        memory = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(memory.learning_history), 2)
        self.assertEqual(memory.preferences.dominant_modality, "interactive")
        self.assertEqual(len(self.repo.list_events(learner_id)), 3)

    # 10. Relevant memory retrieval
    def test_10_relevant_memory_retrieval(self):
        """Verify that relevant context filters history, friction, and projects matching query."""
        learner_id = "retrieval_user"
        # Seed history
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                payload={"topic": "SQL Joins", "score": 0.95},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                payload={"topic": "Tree Traversal", "score": 0.4},
            )
        )
        # Query relevant to SQL
        query = RelevantMemoryQuery(
            learner_id=learner_id,
            topic="SQL Indexing",
            objective="Optimize query performance",
        )
        context = self.engine.retrieve_relevant_context(query)
        self.assertEqual(context.learner_id, learner_id)
        self.assertEqual(context.topic, "SQL Indexing")
        self.assertIn("SQL Joins", [h.topic for h in context.relevant_history])

    # 11. Empty memory handling
    def test_11_empty_memory_handling(self):
        """Verify graceful defaults when querying an unrecorded learner."""
        query = RelevantMemoryQuery(learner_id="brand_new_student_999")
        context = self.engine.retrieve_relevant_context(query)
        self.assertEqual(context.learner_id, "brand_new_student_999")
        self.assertEqual(len(context.relevant_history), 0)
        self.assertEqual(len(context.relevant_friction), 0)
        self.assertIn("No previous memory recorded", context.rationale)

    # 12. Unknown learner handling
    def test_12_unknown_learner_roadmap(self):
        """Verify roadmap intelligence for an unknown learner defaults to ON_TRACK."""
        roadmap = self.engine.generate_roadmap_context("unknown_student")
        self.assertEqual(roadmap.status, RoadmapStatus.ON_TRACK)
        self.assertEqual(roadmap.recommended_action, RoadmapRecommendedAction.PROCEED_NEXT_TOPIC)

    # 13. Contradictory evidence (remediation resolves friction)
    def test_13_contradictory_evidence_resolves_friction(self):
        """Verify that high assessment score resolves prior friction on the same topic."""
        learner_id = "contradiction_user"
        # Initial struggle
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=0.9,
                payload={"topic": "Recursion", "score": 0.3},
            )
        )
        memory = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(any(f.topic == "Recursion" and f.unresolved for f in memory.friction))

        # Subsequent mastery
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=1.0,
                payload={"topic": "Recursion", "score": 0.95},
            )
        )
        memory = self.engine.get_or_create_memory(learner_id)
        recursion_friction = [f for f in memory.friction if f.topic == "Recursion"]
        self.assertTrue(all(not f.unresolved for f in recursion_friction))

    # 14. Repeated learning events (friction compounding)
    def test_14_repeated_struggles_compound_severity(self):
        """Verify mistake counts increment and escalate severity to high."""
        learner_id = "struggle_user"
        for _ in range(3):
            self.engine.record_event(
                MemoryUpdateEvent(
                    learner_id=learner_id,
                    event_type=MemoryEventType.REPEATED_MISTAKE,
                    confidence_score=0.8,
                    payload={"topic": "Memory Leaks", "struggle_type": "conceptual_gap"},
                )
            )
        memory = self.engine.get_or_create_memory(learner_id)
        fric = next(f for f in memory.friction if f.topic == "Memory Leaks")
        self.assertEqual(fric.mistake_count, 3)
        self.assertEqual(fric.severity, "high")
        self.assertIn("Immediate foundational remediation", fric.recommended_intervention)

    # 15. Learner state + memory context construction
    def test_15_context_construction_with_active_friction(self):
        """Verify that high-severity friction recommends visual scaffolding."""
        learner_id = "scaffold_req_user"
        for _ in range(3):
            self.engine.record_event(
                MemoryUpdateEvent(
                    learner_id=learner_id,
                    event_type=MemoryEventType.REPEATED_MISTAKE,
                    payload={"topic": "Binary Search Trees"},
                )
            )
        context = self.engine.retrieve_relevant_context(
            RelevantMemoryQuery(learner_id=learner_id, topic="Binary Search Trees")
        )
        self.assertEqual(context.recommended_pedagogical_mode, "visual")
        self.assertIn("Binary Search Trees", context.detected_weaknesses)

    # 16. Roadmap-relevant memory retrieval
    def test_16_roadmap_adaptation_triggers(self):
        """Verify roadmap adaptation detects needs_remediation vs ready_for_advancement."""
        # Case A: Needs remediation
        learner_a = "learner_needs_remed"
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_a,
                event_type=MemoryEventType.REPEATED_MISTAKE,
                payload={"topic": "Pointers"},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_a,
                event_type=MemoryEventType.REPEATED_MISTAKE,
                payload={"topic": "Memory Allocation"},
            )
        )
        roadmap_a = self.engine.generate_roadmap_context(learner_a)
        self.assertEqual(roadmap_a.status, RoadmapStatus.NEEDS_REMEDIATION)
        self.assertEqual(roadmap_a.recommended_action, RoadmapRecommendedAction.INSERT_REMEDIATION)
        self.assertIn("Pointers", roadmap_a.remediation_topics)

        # Case B: Ready for advancement
        learner_b = "learner_advance"
        for topic in ["Syntax", "Loops", "Functions", "OOP"]:
            self.engine.record_event(
                MemoryUpdateEvent(
                    learner_id=learner_b,
                    event_type=MemoryEventType.LESSON_COMPLETED,
                    payload={"topic": topic, "score": 0.95},
                )
            )
        roadmap_b = self.engine.generate_roadmap_context(learner_b)
        self.assertEqual(roadmap_b.status, RoadmapStatus.READY_FOR_ADVANCEMENT)
        self.assertEqual(roadmap_b.recommended_action, RoadmapRecommendedAction.ACCELERATE)

    # 17. API validation errors
    def test_17_api_validation_error(self):
        """Verify API returns 422 for malformed requests."""
        # Missing required learner_id
        response = self.client.post("/api/v1/memory/events", json={"event_type": "lesson_completed"})
        self.assertEqual(response.status_code, 422)

        # Empty learner_id in retrieve
        response = self.client.post("/api/v1/memory/retrieve", json={"learner_id": ""})
        self.assertEqual(response.status_code, 422)

    # 18. API successful responses
    def test_18_api_successful_responses(self):
        """Verify end-to-end HTTP 200 responses across memory endpoints."""
        learner_id = "http_api_test_user"

        # 1. POST /api/v1/memory/events
        event_payload = {
            "learner_id": learner_id,
            "event_type": "lesson_completed",
            "evidence_source": "observed",
            "confidence_score": 0.9,
            "payload": {"topic": "FastAPI Basics", "score": 0.92},
        }
        res_evt = self.client.post("/api/v1/memory/events", json=event_payload)
        self.assertEqual(res_evt.status_code, 200)
        data_evt = res_evt.json()
        self.assertTrue(data_evt["success"])
        self.assertEqual(data_evt["learner_id"], learner_id)

        # 2. POST /api/v1/memory/retrieve
        res_ret = self.client.post("/api/v1/memory/retrieve", json={"learner_id": learner_id})
        self.assertEqual(res_ret.status_code, 200)
        data_ret = res_ret.json()
        self.assertEqual(data_ret["learner_id"], learner_id)
        self.assertEqual(len(data_ret["learning_history"]), 1)

        # 3. POST /api/v1/memory/relevant-context
        res_ctx = self.client.post(
            "/api/v1/memory/relevant-context",
            json={"learner_id": learner_id, "topic": "FastAPI Basics"},
        )
        self.assertEqual(res_ctx.status_code, 200)
        data_ctx = res_ctx.json()
        self.assertEqual(data_ctx["learner_id"], learner_id)
        self.assertIn("FastAPI Basics", [h["topic"] for h in data_ctx["relevant_history"]])

        # 4. POST /api/v1/memory/roadmap-context
        res_rdm = self.client.post(
            "/api/v1/memory/roadmap-context",
            json={"learner_id": learner_id},
        )
        self.assertEqual(res_rdm.status_code, 200)
        data_rdm = res_rdm.json()
        self.assertIn(data_rdm["status"], [s.value for s in RoadmapStatus])

    # 19. Invalid requests and boundary handling
    def test_19_invalid_event_types(self):
        """Verify that invalid event types are rejected with 422."""
        response = self.client.post(
            "/api/v1/memory/events",
            json={"learner_id": "test_id", "event_type": "unsupported_event_type"},
        )
        self.assertEqual(response.status_code, 422)

    # 20. Edge cases (Unicode learner names, empty topic queries, score clamping)
    def test_20_edge_cases(self):
        """Verify edge cases like Unicode learner IDs, empty topic queries, and score clamping."""
        unicode_id = "learner_日本語_001"
        event = MemoryUpdateEvent(
            learner_id=unicode_id,
            event_type=MemoryEventType.LESSON_COMPLETED,
            confidence_score=1.5,  # Should clamp to 1.0
            payload={"topic": "Recursion", "score": -0.2},
        )
        self.assertEqual(event.confidence_score, 1.0)
        result = self.engine.record_event(event)
        self.assertTrue(result.success)

        retrieved = self.engine.get_or_create_memory(unicode_id)
        self.assertEqual(retrieved.learner_id, unicode_id)

    # 21. Explicit assessment threshold boundary tests (poor < 0.50, high > 0.85)
    def test_21_exact_assessment_threshold_boundaries(self):
        """Verify exact boundary behavior:
        - score 0.82 must NOT resolve friction or indicate mastery (under threshold)
        - score 0.85 must NOT resolve friction (strictly > 0.85 required)
        - score 0.86 must resolve/de-escalate friction (> 0.85 met)
        - score 0.90 must resolve/de-escalate friction and grant mastery
        """
        learner_id = "threshold_boundary_student"

        # Step 1: Establish active friction with poor assessment score (0.40 < 0.50)
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=0.95,
                payload={"topic": "Pointers", "score": 0.40},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        friction_pointers = [f for f in mem.friction if f.topic == "Pointers"]
        self.assertEqual(len(friction_pointers), 1)
        self.assertTrue(friction_pointers[0].unresolved)

        # Step 2: Score 0.82 must NOT resolve friction (0.82 <= 0.85)
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=1.0,
                payload={"topic": "Pointers", "score": 0.82},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(
            any(f.topic == "Pointers" and f.unresolved for f in mem.friction),
            "Score 0.82 must not resolve friction (strictly > 0.85 required)",
        )

        # Step 3: Score 0.85 must NOT resolve friction (strictly > 0.85 required)
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                confidence_score=1.0,
                payload={"topic": "Pointers", "score": 0.85},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(
            any(f.topic == "Pointers" and f.unresolved for f in mem.friction),
            "Score 0.85 must not resolve friction (strictly > 0.85 required)",
        )

        # Step 4: Score 0.86 must resolve/de-escalate friction (0.86 > 0.85)
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=1.0,
                payload={"topic": "Pointers", "score": 0.86},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(
            all(not f.unresolved for f in mem.friction if f.topic == "Pointers"),
            "Score 0.86 must resolve friction (0.86 > 0.85)",
        )

        # Step 5: Test score 0.90 on a new struggling topic
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.REPEATED_MISTAKE,
                payload={"topic": "Memory Leaks"},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(any(f.topic == "Memory Leaks" and f.unresolved for f in mem.friction))

        # Score 0.90 resolves friction and creates mastery achievement
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                confidence_score=1.0,
                payload={"topic": "Memory Leaks", "score": 0.90},
            )
        )
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertTrue(
            all(not f.unresolved for f in mem.friction if f.topic == "Memory Leaks"),
            "Score 0.90 must resolve friction",
        )
        self.assertTrue(any("Topic Mastery: Memory Leaks" in a.title for a in mem.achievements))

    # 22. Successful onboarding memory initialization
    def test_22_initialize_memory_from_onboarding_success(self):
        """Verify initialize_memory_from_onboarding seeds goals, preferences, skills, and metadata."""
        learner_id = "onboarding_seed_student"
        report = LearnerIntelligenceReport(
            learner_id=learner_id,
            stage=LearnerStage.BACHELOR,
            target_role="AI/ML Engineer",
            executive_summary="Learner has strong Python and Math foundations with career focus on AI/ML.",
            skill_analysis=SkillAnalysis(
                baseline_summary="Strong programming fundamentals, ready for ML algorithms.",
                proficiency_level="intermediate",
                core_strengths=["Python", "Linear Algebra"],
                critical_skill_gaps=["PyTorch", "MLOps"],
            ),
            knowledge_analysis=KnowledgeAnalysis(
                conceptual_depth="applied",
                prerequisite_health="solid",
                theoretical_vs_applied_balance="applied",
                recommended_foundation_topics=["Probability", "Optimization"],
            ),
            learning_style=LearningStyleProfile(
                dominant_modality="interactive",
                secondary_modality="visual",
                recommended_pacing="accelerated",
                feedback_cadence="milestone",
                content_format_priorities=["worked_examples", "code_challenges"],
            ),
            career_goals=CareerGoalProfile(
                target_role="AI/ML Engineer",
                role_alignment_score=0.85,
                key_milestones=["Math for ML", "Deep Learning Foundations", "Production Model Deployment"],
                high_priority_competencies=["Model Optimization", "Data Pipelines"],
                estimated_timeline_months=6,
            ),
            motivation=MotivationProfile(
                primary_driver="career_transition",
                intrinsic_vs_extrinsic="mostly_intrinsic",
                engagement_hooks=["Computer Vision", "Applied Neural Nets"],
                potential_frustration_triggers=["Dense theoretical proofs"],
                resilience_advice="Build hands-on prototypes first.",
            ),
            readiness=ReadinessAssessment(
                overall_readiness_score=0.90,
                readiness_tier=ReadinessTier.HIGH,
                recommended_entry_level="intermediate",
                onboarding_recommendations=["Proceed directly to neural network fundamentals"],
            ),
        )

        result = self.engine.initialize_memory_from_onboarding(report)
        self.assertTrue(result.success)
        self.assertTrue(result.is_new_initialization)
        self.assertEqual(result.learner_id, learner_id)
        self.assertIn("goals", result.seeded_facets)
        self.assertIn("preferences", result.seeded_facets)
        self.assertIn("metadata", result.seeded_facets)

        # Retrieve and inspect memory container
        mem = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(mem.goals.primary_target_role, "AI/ML Engineer")
        self.assertEqual(mem.goals.target_timeline_months, 6)
        self.assertIn("Math for ML", mem.goals.milestones)
        self.assertIn("Computer Vision", mem.goals.secondary_interests)
        # Goal change history must be clean (initialization, not a role shift)
        self.assertEqual(len(mem.goals.goal_change_history), 0)

        # Preferences
        self.assertEqual(mem.preferences.dominant_modality, "interactive")
        self.assertEqual(mem.preferences.secondary_modality, "visual")
        self.assertEqual(mem.preferences.pacing, "accelerated")
        self.assertAlmostEqual(mem.preferences.practical_vs_theory_ratio, 0.8)
        self.assertIn("code_challenges", mem.preferences.content_format_priorities)

        # Metadata
        self.assertTrue(mem.metadata.get("onboarding_seeded"))
        self.assertEqual(mem.metadata.get("academic_stage"), "bachelor")
        self.assertIn("Python", mem.metadata.get("baseline_skills", []))
        self.assertIn("PyTorch", mem.metadata.get("critical_skill_gaps", []))
        self.assertEqual(mem.metadata.get("readiness_tier"), "high")

        # Milestone achievement for high readiness
        self.assertTrue(any(a.title == "Onboarding Excellence" for a in mem.achievements))

        # Event audit trail
        events = self.repo.list_events(learner_id)
        self.assertTrue(len(events) >= 1)
        self.assertEqual(events[0].payload.get("source"), "onboarding_intelligence_report")

    # 23. Idempotent initialization
    def test_23_initialize_memory_from_onboarding_idempotent(self):
        """Verify repeated calls do not duplicate milestones, skills, or format priorities."""
        learner_id = "idempotent_student"
        report = LearnerIntelligenceReport(
            learner_id=learner_id,
            stage=LearnerStage.BACHELOR,
            target_role="Backend Developer",
            career_goals=CareerGoalProfile(
                target_role="Backend Developer",
                key_milestones=["Milestone A", "Milestone B"],
            ),
            learning_style=LearningStyleProfile(
                dominant_modality="hands-on",
                content_format_priorities=["worked_examples"],
            ),
            skill_analysis=SkillAnalysis(
                core_strengths=["Go", "SQL"],
                critical_skill_gaps=["Kafka"],
            ),
            readiness=ReadinessAssessment(
                overall_readiness_score=0.75,
                readiness_tier=ReadinessTier.MODERATE,
            ),
        )

        # First call: fresh initialization
        res1 = self.engine.initialize_memory_from_onboarding(report)
        self.assertTrue(res1.is_new_initialization)

        # Second call: idempotent update
        res2 = self.engine.initialize_memory_from_onboarding(report)
        self.assertFalse(res2.is_new_initialization)

        mem = self.engine.get_or_create_memory(learner_id)
        # Milestones must not be duplicated
        self.assertEqual(mem.goals.milestones.count("Milestone A"), 1)
        self.assertEqual(mem.goals.milestones.count("Milestone B"), 1)

        # Content format priorities must not be duplicated
        self.assertEqual(mem.preferences.content_format_priorities.count("worked_examples"), 1)

        # Baseline skills must not be duplicated
        self.assertEqual(mem.metadata["baseline_skills"].count("Go"), 1)
        self.assertEqual(mem.metadata["critical_skill_gaps"].count("Kafka"), 1)

    # 24. Existing learner history is preserved
    def test_24_initialize_memory_from_onboarding_preserves_existing_history(self):
        """Verify existing learning history, active friction, and projects are not overwritten."""
        learner_id = "existing_history_student"

        # Pre-populate existing history & friction
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.LESSON_COMPLETED,
                payload={"topic": "Binary Trees", "score": 0.92},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.TOPIC_STRUGGLED,
                payload={"topic": "Graph Algorithms"},
            )
        )
        self.engine.record_event(
            MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.PROJECT_COMPLETED,
                payload={"title": "Custom Shell", "technologies_used": ["C"]},
            )
        )

        mem_before = self.engine.get_or_create_memory(learner_id)
        self.assertEqual(len(mem_before.learning_history), 1)
        self.assertEqual(len(mem_before.friction), 1)
        self.assertEqual(len(mem_before.projects), 1)

        # Now execute onboarding seeding
        report = LearnerIntelligenceReport(
            learner_id=learner_id,
            stage=LearnerStage.MASTER,
            target_role="Systems Engineer",
            learning_style=LearningStyleProfile(dominant_modality="theoretical"),
        )
        result = self.engine.initialize_memory_from_onboarding(report)
        self.assertTrue(result.success)

        mem_after = self.engine.get_or_create_memory(learner_id)
        # Existing history, friction, and projects MUST remain intact
        self.assertEqual(len(mem_after.learning_history), 1)
        self.assertEqual(mem_after.learning_history[0].topic, "Binary Trees")
        self.assertEqual(len(mem_after.friction), 1)
        self.assertEqual(mem_after.friction[0].topic, "Graph Algorithms")
        self.assertEqual(len(mem_after.projects), 1)
        self.assertEqual(mem_after.projects[0].title, "Custom Shell")

        # Goals and preferences successfully seeded
        self.assertEqual(mem_after.goals.primary_target_role, "Systems Engineer")
        self.assertEqual(mem_after.preferences.dominant_modality, "theoretical")

    # 25. Malformed input error handling
    def test_25_initialize_memory_from_onboarding_malformed_input(self):
        """Verify ValueError is raised when given malformed or empty learner data."""
        with self.assertRaises(ValueError):
            self.engine.initialize_memory_from_onboarding(None)

    # 26. API endpoint POST /api/v1/memory/seed-from-onboarding success
    def test_26_seed_from_onboarding_api_endpoint(self):
        """Verify API contract for POST /api/v1/memory/seed-from-onboarding."""
        learner_id = "http_seed_user"
        report_payload = {
            "learner_id": learner_id,
            "stage": "bachelor",
            "target_role": "Data Engineer",
            "executive_summary": "Aspiring data engineer with strong SQL skills.",
            "skill_analysis": {
                "baseline_summary": "SQL proficient, needs Spark and cloud data lakes.",
                "proficiency_level": "intermediate",
                "core_strengths": ["SQL", "Python"],
                "critical_skill_gaps": ["Apache Spark", "Airflow"],
            },
            "knowledge_analysis": {
                "conceptual_depth": "applied",
                "prerequisite_health": "solid",
                "theoretical_vs_applied_balance": "practical",
                "recommended_foundation_topics": ["Relational Algebra"],
            },
            "learning_style": {
                "dominant_modality": "hands-on",
                "secondary_modality": "visual",
                "recommended_pacing": "standard",
                "feedback_cadence": "milestone",
                "content_format_priorities": ["worked_examples", "code_challenges"],
            },
            "career_goals": {
                "target_role": "Data Engineer",
                "role_alignment_score": 0.8,
                "key_milestones": ["Advanced SQL & Databases", "ETL Pipelines with Airflow", "Distributed Systems"],
                "high_priority_competencies": ["Data Modeling", "ETL"],
                "estimated_timeline_months": 5,
            },
            "motivation": {
                "primary_driver": "career_growth",
                "intrinsic_vs_extrinsic": "balanced",
                "engagement_hooks": ["Big Data Analytics"],
                "potential_frustration_triggers": [],
                "resilience_advice": "Focus on pipeline projects.",
            },
            "readiness": {
                "overall_readiness_score": 0.82,
                "readiness_tier": "moderate",
                "recommended_entry_level": "intermediate",
                "onboarding_recommendations": ["Start with data warehouse architecture"],
            },
        }

        # First call: 200 OK, is_new_initialization = True
        resp = self.client.post("/api/v1/memory/seed-from-onboarding", json=report_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["learner_id"], learner_id)
        self.assertTrue(data["is_new_initialization"])
        self.assertIn("goals", data["seeded_facets"])
        self.assertIn("preferences", data["seeded_facets"])

        # Second call: 200 OK, is_new_initialization = False (idempotent)
        resp2 = self.client.post("/api/v1/memory/seed-from-onboarding", json=report_payload)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertTrue(data2["success"])
        self.assertFalse(data2["is_new_initialization"])

    # 27. API endpoint validation error handling
    def test_27_seed_from_onboarding_api_validation_error(self):
        """Verify API returns 422 Unprocessable Entity for malformed payloads."""
        # Missing required target_role
        resp = self.client.post("/api/v1/memory/seed-from-onboarding", json={"learner_id": "bad_user"})
        self.assertEqual(resp.status_code, 422)

    # 28. GET /api/v1/memory/{learner_id} for existing learner
    def test_28_get_complete_memory_existing_learner(self):
        """Verify GET /api/v1/memory/{learner_id} returns 200 and full 7-dimension schema."""
        from app.services import get_memory_engine
        learner_id = "test_get_existing_user_01"
        mem = get_memory_engine().get_or_create_memory(learner_id)
        mem.goals.primary_target_role = "Machine Learning Engineer"
        mem.preferences.dominant_modality = "hands-on"
        mem.friction.append(
            FrictionMemory(
                topic="Transformers",
                struggle_type="conceptual",
                severity="moderate",
                mistake_count=2,
                unresolved=True,
                first_observed_at=datetime.now(timezone.utc),
                last_observed_at=datetime.now(timezone.utc),
            )
        )
        get_memory_engine().repository.save_memory(mem)

        resp = self.client.get(f"/api/v1/memory/{learner_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Validate complete schema
        validated = LearnerMemory.model_validate(data)
        self.assertEqual(validated.learner_id, learner_id)
        self.assertEqual(validated.goals.primary_target_role, "Machine Learning Engineer")
        self.assertEqual(validated.preferences.dominant_modality, "hands-on")
        self.assertEqual(len(validated.friction), 1)
        self.assertEqual(validated.friction[0].topic, "Transformers")

        # Verify all 7 memory dimensions exist in payload
        for facet in ["preferences", "conversations", "learning_history", "projects", "goals", "achievements", "friction"]:
            self.assertIn(facet, data)

    # 29. GET /api/v1/memory/{learner_id} for unknown learner
    def test_29_get_complete_memory_unknown_learner(self):
        """Verify GET /api/v1/memory/{learner_id} returns 404 for unknown learners."""
        resp = self.client.get("/api/v1/memory/totally_unknown_learner_99999")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("not found", resp.json()["detail"].lower())

        # Whitespace learner_id returns 422
        resp_invalid = self.client.get("/api/v1/memory/%20%20")
        self.assertEqual(resp_invalid.status_code, 422)

    # 30. GET /api/v1/memory/{learner_id}/relevant with topic and objective
    def test_30_get_relevant_memory_scoped(self):
        """Verify GET /api/v1/memory/{learner_id}/relevant returns scoped context."""
        from app.services import get_memory_engine
        learner_id = "test_get_scoped_user_01"
        mem = get_memory_engine().get_or_create_memory(learner_id)
        mem.goals.primary_target_role = "Backend Developer"
        mem.friction.append(
            FrictionMemory(
                topic="AsyncIO",
                struggle_type="concurrency_deadlock",
                severity="high",
                mistake_count=3,
                unresolved=True,
                first_observed_at=datetime.now(timezone.utc),
                last_observed_at=datetime.now(timezone.utc),
            )
        )
        get_memory_engine().repository.save_memory(mem)

        resp = self.client.get(
            f"/api/v1/memory/{learner_id}/relevant?topic=AsyncIO&objective=Master%20event%20loop"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        validated = RelevantMemoryContext.model_validate(data)
        self.assertEqual(validated.learner_id, learner_id)
        self.assertEqual(validated.topic, "AsyncIO")
        self.assertEqual(len(validated.relevant_friction), 1)
        self.assertEqual(validated.relevant_friction[0].topic, "AsyncIO")

    # 31. GET /api/v1/memory/{learner_id}/relevant for empty or unknown memory
    def test_31_get_relevant_memory_empty_or_unknown(self):
        """Verify GET /api/v1/memory/{learner_id}/relevant handles unknown learners gracefully with defaults."""
        resp = self.client.get(
            "/api/v1/memory/brand_new_unseeded_user_01/relevant?topic=Graphs&objective=BFS"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        validated = RelevantMemoryContext.model_validate(data)
        self.assertEqual(validated.learner_id, "brand_new_unseeded_user_01")
        self.assertEqual(validated.topic, "Graphs")
        self.assertEqual(validated.relevant_friction, [])
        self.assertEqual(validated.relevant_history, [])
        self.assertEqual(validated.recommended_pedagogical_mode, "visual")

    # 32. GET /api/v1/memory/{learner_id}/relevant parity with MemoryEngine
    def test_32_get_relevant_memory_parity_with_engine(self):
        """Verify GET endpoint matches direct MemoryEngine.retrieve_relevant_context() results."""
        from app.services import get_memory_engine
        learner_id = "test_parity_user_01"
        engine = get_memory_engine()

        # Engine direct call
        query = RelevantMemoryQuery(
            learner_id=learner_id,
            topic="Dynamic Programming",
            objective="Memoization vs Tabulation",
        )
        engine_context = engine.retrieve_relevant_context(query)

        # API call
        resp = self.client.get(
            f"/api/v1/memory/{learner_id}/relevant?topic=Dynamic%20Programming&objective=Memoization%20vs%20Tabulation"
        )
        self.assertEqual(resp.status_code, 200)
        api_data = resp.json()

        self.assertEqual(api_data["learner_id"], engine_context.learner_id)
        self.assertEqual(api_data["topic"], engine_context.topic)
        self.assertEqual(api_data["recommended_pedagogical_mode"], engine_context.recommended_pedagogical_mode)

    # 33. POST /api/v1/memory/seed alias endpoint
    def test_33_seed_alias_endpoint(self):
        """Verify POST /api/v1/memory/seed alias endpoint functions identically to /seed-from-onboarding."""
        learner_id = "http_seed_alias_user"
        report_payload = {
            "learner_id": learner_id,
            "stage": "bachelor",
            "target_role": "Security Engineer",
            "executive_summary": "Cybersecurity student interested in application security.",
            "skill_analysis": {
                "baseline_summary": "Network security basics, needs cryptography.",
                "proficiency_level": "beginner",
                "core_strengths": ["Networking"],
                "critical_skill_gaps": ["Cryptography"],
            },
            "knowledge_analysis": {
                "conceptual_depth": "applied",
                "prerequisite_health": "solid",
                "theoretical_vs_applied_balance": "practical",
                "recommended_foundation_topics": ["Discrete Math"],
            },
            "learning_style": {
                "dominant_modality": "hands-on",
                "secondary_modality": "visual",
                "recommended_pacing": "standard",
                "feedback_cadence": "immediate",
                "content_format_priorities": ["code_challenges"],
            },
            "career_goals": {
                "target_role": "Security Engineer",
                "role_alignment_score": 0.85,
                "key_milestones": ["Web App Security", "Penetration Testing"],
                "high_priority_competencies": ["Threat Modeling"],
                "estimated_timeline_months": 6,
            },
            "motivation": {
                "primary_driver": "problem_solving",
                "intrinsic_vs_extrinsic": "intrinsic",
                "engagement_hooks": ["Capture The Flag"],
                "potential_frustration_triggers": [],
                "resilience_advice": "Practice systematically.",
            },
            "readiness": {
                "overall_readiness_score": 0.75,
                "readiness_tier": "moderate",
                "recommended_entry_level": "beginner",
                "onboarding_recommendations": ["Start with OWASP Top 10"],
            },
        }

        resp = self.client.post("/api/v1/memory/seed", json=report_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["learner_id"], learner_id)
        self.assertTrue(data["is_new_initialization"])


if __name__ == "__main__":
    unittest.main()

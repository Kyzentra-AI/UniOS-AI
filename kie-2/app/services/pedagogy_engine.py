from typing import Optional
from app.schemas.learner import LearnerStage, ConfidenceLevel
from app.schemas.context import NormalizedLearningContext
from app.schemas.pedagogy import (
    TeachingStrategy,
    DifficultyLevel,
    PresentationMode,
    PracticeLevel,
    PedagogyDecision,
)


class PedagogyEngine:
    """Universal AI/ML-2 Pedagogy Engine (Task A2-S4-01).
    
    Answers the core question:
    'Given this learner's actual state and disciplinary domain, how should this topic be taught?'
    
    Adheres strictly to the Universal Student Platform contract:
    - Supports Bachelor's, Master's, and Graduate stages.
    - Adapts across academic domains (Engineering, Commerce, Humanities, Science, Management, Law).
    - Bases all decisions on concrete learner evidence (mastery, friction, stage, goals, history).
    """

    def determine_pedagogy(self, context: NormalizedLearningContext) -> PedagogyDecision:
        """Evaluates learner evidence, domain context, and memory to produce a structured pedagogy decision."""
        learner = context.learner_state
        topic = context.topic
        clean_topic = topic.strip().lower()

        # 1. Identify Academic Domain & Stage
        stage = learner.stage if learner else LearnerStage.BACHELOR
        domain = ""
        if context.academic_domain:
            domain = context.academic_domain.strip().lower()
        elif learner and learner.academic_domain:
            domain = learner.academic_domain.strip().lower()
        elif learner and learner.academic_program:
            domain = learner.academic_program.strip().lower()

        # 2. Extract Evidence Signals: Mastery, Weaknesses, Friction
        concept_mastery = learner.concept_mastery if learner else {}
        topic_mastery = concept_mastery.get(topic)
        if topic_mastery is None:
            # Case-insensitive topic search in concept_mastery
            for k, v in concept_mastery.items():
                if k.strip().lower() == clean_topic:
                    topic_mastery = v
                    break

        weak_topics_lower = [w.strip().lower() for w in (learner.weak_topics if learner else [])]
        is_in_weak_topics = clean_topic in weak_topics_lower or any(w in clean_topic for w in weak_topics_lower)

        # Check Active Friction in Memory Context
        has_memory_friction = False
        friction_severity = "none"
        if context.memory_context and context.memory_context.relevant_friction:
            for f in context.memory_context.relevant_friction:
                if f.topic.strip().lower() == clean_topic or clean_topic in f.topic.strip().lower():
                    if f.unresolved:
                        has_memory_friction = True
                        friction_severity = f.severity
                        break

        # Check Recent History in Memory Context
        history_score = None
        if context.memory_context and context.memory_context.relevant_history:
            for h in context.memory_context.relevant_history:
                if h.topic.strip().lower() == clean_topic and h.assessment_score is not None:
                    history_score = h.assessment_score
                    break

        # Check Performance telemetry if provided
        performance_score = None
        if context.performance and isinstance(context.performance, dict):
            tp = context.performance.get("topic_performance", {})
            if isinstance(tp, dict) and topic in tp:
                val = tp[topic]
                if isinstance(val, (int, float)):
                    performance_score = float(val)

        # Effective performance indicator
        effective_score = history_score if history_score is not None else performance_score
        is_poor_performer = (topic_mastery is not None and topic_mastery < 0.50) or (
            effective_score is not None and effective_score < 0.50
        )

        # 3. Determine Teaching Strategy & Remediation Mode
        is_remediation = is_in_weak_topics or has_memory_friction or is_poor_performer
        confidence = learner.confidence if learner else ConfidenceLevel.MEDIUM

        if is_remediation:
            strategy = TeachingStrategy.REMEDIATION
            difficulty = DifficultyLevel.BEGINNER
            practice_level = PracticeLevel.REMEDIAL
            explanation_depth = "step-by-step"
            remediation = True
            sequence = [
                "prerequisite_review",
                "simplified_concept_breakdown",
                "scaffolded_worked_example",
                "guided_remedial_practice",
                "formative_reassessment",
            ]
            rationale = (
                f"Remediation intervention triggered for topic '{topic}' based on concrete evidence: "
                f"{'active memory friction (' + friction_severity + ')' if has_memory_friction else ''}"
                f"{'known weak topic' if is_in_weak_topics else ''}"
                f"{'low mastery/performance score' if is_poor_performer else ''}. "
                f"Calibrating to beginner scaffolding with step-by-step prerequisite review."
            )
        elif topic_mastery is not None and topic_mastery >= 0.80 and confidence == ConfidenceLevel.HIGH:
            strategy = TeachingStrategy.ADVANCEMENT
            difficulty = DifficultyLevel.ADVANCED
            practice_level = PracticeLevel.CHALLENGE_BASED
            explanation_depth = "deep-dive"
            remediation = False
            sequence = [
                "concept_synthesis",
                "advanced_domain_tradeoffs",
                "complex_edge_cases",
                "challenge_based_practice",
                "summative_assessment",
            ]
            rationale = (
                f"Advancement strategy selected for '{topic}' due to high verified mastery "
                f"({topic_mastery:.2f}) and high learner confidence. Deep-dive into architectural and domain trade-offs."
            )
        elif topic_mastery is not None and topic_mastery >= 0.50:
            strategy = TeachingStrategy.REINFORCEMENT
            difficulty = DifficultyLevel.INTERMEDIATE
            practice_level = PracticeLevel.INDEPENDENT
            explanation_depth = "step-by-step"
            remediation = False
            sequence = [
                "core_concept_reinforcement",
                "domain_practical_application",
                "guided_practice",
                "independent_practice_task",
                "formative_assessment",
            ]
            rationale = (
                f"Reinforcement strategy selected for '{topic}' with intermediate mastery "
                f"({topic_mastery:.2f}). Balancing conceptual clarity with independent practice."
            )
        else:
            strategy = TeachingStrategy.FOUNDATIONAL
            difficulty = DifficultyLevel.BEGINNER
            practice_level = PracticeLevel.GUIDED
            explanation_depth = "step-by-step"
            remediation = False
            sequence = [
                "prerequisite_check",
                "core_concept_introduction",
                "worked_example",
                "guided_practice",
                "formative_assessment",
            ]
            rationale = (
                f"Foundational strategy selected for '{topic}'. Introducing core mechanics "
                f"with structured guidance suitable for stage '{stage.value}'."
            )

        # 4. Domain & Modality Calibration for Presentation Mode
        presentation_mode = self._calibrate_presentation_mode(domain, learner, context)

        # 5. Stage-specific explanation depth tuning (if not already overridden by remediation/advancement)
        if not is_remediation and strategy != TeachingStrategy.ADVANCEMENT:
            if stage == LearnerStage.MASTER:
                explanation_depth = "deep-dive"
                if difficulty == DifficultyLevel.BEGINNER:
                    difficulty = DifficultyLevel.INTERMEDIATE
            elif stage == LearnerStage.GRADUATE:
                explanation_depth = "step-by-step"

        return PedagogyDecision(
            strategy=strategy,
            difficulty=difficulty,
            presentation_mode=presentation_mode,
            explanation_depth=explanation_depth,
            rationale=rationale,
            sequence=sequence,
            practice_level=practice_level,
            remediation=remediation,
            recommended_level=difficulty.value,
            reasoning_summary=rationale,
        )

    def _calibrate_presentation_mode(
        self, domain: str, learner, context: NormalizedLearningContext
    ) -> PresentationMode:
        """Calibrates presentation mode according to learner preference and academic domain."""
        # 1. Check Memory Recommended Mode
        if context.memory_context:
            rec = context.memory_context.recommended_pedagogical_mode
            if rec:
                r_lower = rec.strip().lower()
                for mode in PresentationMode:
                    if mode.value == r_lower:
                        return mode
            if context.memory_context.relevant_preferences:
                dom_mod = context.memory_context.relevant_preferences.dominant_modality
                if dom_mod and dom_mod.strip().lower() != "visual":
                    d_lower = dom_mod.strip().lower()
                    for mode in PresentationMode:
                        if mode.value == d_lower:
                            return mode

        # 2. Domain Adaptation (Universal Student Platform)
        d_lower = domain.lower()
        if any(term in d_lower for term in ["commerce", "finance", "accounting", "economics", "b.com", "bcom"]):
            return PresentationMode.CASE_STUDY
        elif any(term in d_lower for term in ["law", "legal", "jurisprudence", "constitution"]):
            return PresentationMode.ANALYTICAL
        elif any(term in d_lower for term in ["management", "business", "mba", "marketing"]):
            return PresentationMode.CASE_STUDY
        elif any(term in d_lower for term in ["humanities", "arts", "psychology", "history", "philosophy"]):
            return PresentationMode.ANALYTICAL
        elif any(term in d_lower for term in ["science", "biotech", "physics", "chemistry", "biology", "msc"]):
            return PresentationMode.SIMULATION
        elif any(term in d_lower for term in ["design", "architecture"]):
            return PresentationMode.VISUAL

        # 3. Check Learner State Preference
        if learner and learner.learning_preference:
            pref = learner.learning_preference.strip().lower()
            for mode in PresentationMode:
                if mode.value == pref:
                    return mode

        # Default fallback
        return PresentationMode.VISUAL



_pedagogy_engine: Optional[PedagogyEngine] = None


def get_pedagogy_engine() -> PedagogyEngine:
    """Singleton provider for PedagogyEngine."""
    global _pedagogy_engine
    if _pedagogy_engine is None:
        _pedagogy_engine = PedagogyEngine()
    return _pedagogy_engine

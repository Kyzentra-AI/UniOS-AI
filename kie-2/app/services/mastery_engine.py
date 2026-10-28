from typing import Dict, List, Optional
from app.schemas.mastery import (
    MasteryTier,
    AssessmentAttemptType,
    AssessmentEvidence,
    RemediationSignal,
    MasteryUpdateResult,
)
from app.schemas.memory_events import MemoryUpdateEvent, MemoryEventType, EvidenceSource
from app.services.memory_engine import get_memory_engine


class MasteryEngine:
    """Universal AI/ML-2 Mastery and Weakness Intelligence Engine (Task A2-S4-03).
    
    Evaluates assessment evidence deterministically (Section 6.4 & 10):
    - Computes mastery score and classifies into canonical BRD tiers:
        * Weak: < 50% (< 0.50)
        * Developing: 50% - 79% (0.50 - 0.79)
        * Proficient: 80% - 100% (0.80 - 1.00)
    - Detects weak areas and strong areas.
    - Emits measurable remediation signals.
    - Synchronizes with MemoryEngine without creating an independent persistent DB.
    """

    def __init__(self):
        # Ephemeral cache of active topic mastery scores per learner
        self._mastery_cache: Dict[str, Dict[str, float]] = {}

    def get_topic_mastery(self, learner_id: str, topic: str) -> float:
        """Retrieves current mastery score for learner on topic (defaulting to 0.0 or memory)."""
        clean_id = learner_id.strip()
        clean_topic = topic.strip()
        if clean_id in self._mastery_cache and clean_topic in self._mastery_cache[clean_id]:
            return self._mastery_cache[clean_id][clean_topic]

        # Check memory learning_history if available
        mem_engine = get_memory_engine()
        mem = mem_engine.get_or_create_memory(clean_id)
        for h in mem.learning_history:
            if h.topic.strip().lower() == clean_topic.lower():
                return h.mastery_level
        return 0.0


    def evaluate_assessment(self, evidence: AssessmentEvidence) -> MasteryUpdateResult:
        """Evaluates assessment evidence, computes updated mastery, and generates remediation signals."""
        learner_id = evidence.learner_id.strip()
        topic = evidence.topic.strip()
        score = evidence.score

        # 1. Retrieve previous mastery
        prev_mastery = self.get_topic_mastery(learner_id, topic)

        # 2. Evidence-driven mastery update formula
        if prev_mastery == 0.0 or evidence.attempt_type == AssessmentAttemptType.DIAGNOSTIC:
            # First observation or diagnostic establishes baseline directly from evidence
            new_mastery = round(score, 2)
        elif evidence.attempt_type == AssessmentAttemptType.REASSESSMENT:
            # Reassessment: high score directly confirms remediation recovery
            if score >= 0.80:
                new_mastery = round(score, 2)
            else:
                new_mastery = round((prev_mastery * 0.3) + (score * 0.7), 2)
        else:
            # Standard formative assessment
            new_mastery = round((prev_mastery * 0.35) + (score * 0.65), 2)

        new_mastery = max(0.0, min(1.0, new_mastery))


        # Update cache
        if learner_id not in self._mastery_cache:
            self._mastery_cache[learner_id] = {}
        self._mastery_cache[learner_id][topic] = new_mastery

        # 3. Determine Canonical BRD Mastery Tier (Section 6.4)
        if new_mastery < 0.50:
            tier = MasteryTier.WEAK
            is_proficient = False
        elif new_mastery < 0.80:
            tier = MasteryTier.DEVELOPING
            is_proficient = False
        else:
            tier = MasteryTier.PROFICIENT
            is_proficient = True

        # 4. Detect Weak and Strong Areas across learner topics
        weak_areas: List[str] = []
        strong_areas: List[str] = []
        for top, mast in self._mastery_cache[learner_id].items():
            if mast < 0.50:
                weak_areas.append(top)
            elif mast >= 0.80:
                strong_areas.append(top)

        if topic not in weak_areas and tier == MasteryTier.WEAK:
            weak_areas.append(topic)
        if topic not in strong_areas and tier == MasteryTier.PROFICIENT:
            strong_areas.append(topic)

        # 5. Produce Measurable Remediation Signal (A2-S4-03)
        if score < 0.50 or tier == MasteryTier.WEAK:
            severity = "high" if score < 0.35 else "moderate"
            remediation_sig = RemediationSignal(
                remediation_required=True,
                severity=severity,
                topic=topic,
                recommended_strategy="remediation",
                recommended_action=(
                    f"Initiate remediation loop for '{topic}': Review foundational prerequisites, "
                    f"deliver simplified scaffolding blocks, and schedule formative reassessment."
                ),
                weak_concepts=[topic] + (evidence.subtopic.split(",") if evidence.subtopic else []),
                rationale=(
                    f"Assessment score of {score:.2f} (< 0.50) results in '{tier.value}' mastery ({new_mastery:.2f}). "
                    f"Measurable struggle detected requiring active pedagogical intervention."
                ),
            )
        elif tier == MasteryTier.PROFICIENT:
            remediation_sig = RemediationSignal(
                remediation_required=False,
                severity="none",
                topic=topic,
                recommended_strategy="advancement",
                recommended_action=(
                    f"Advance learner to next sequential concept, practical challenge, or build milestone for '{topic}'."
                ),
                weak_concepts=[],
                rationale=(
                    f"Assessment score of {score:.2f} confirms proficient mastery ({new_mastery:.2f}). "
                    f"Prerequisite competency achieved."
                ),
            )
        else:
            remediation_sig = RemediationSignal(
                remediation_required=False,
                severity="low",
                topic=topic,
                recommended_strategy="reinforcement",
                recommended_action=(
                    f"Reinforce '{topic}' with guided practice tasks to transition from developing to proficient tier."
                ),
                weak_concepts=[],
                rationale=(
                    f"Assessment score of {score:.2f} achieves developing tier ({new_mastery:.2f}). "
                    f"Continued practice recommended before advanced topics."
                ),
            )

        # 6. Synchronize with MemoryEngine (Record ASSESSMENT_RESULT event)
        try:
            mem_engine = get_memory_engine()
            mem_event = MemoryUpdateEvent(
                learner_id=learner_id,
                event_type=MemoryEventType.ASSESSMENT_RESULT,
                source=EvidenceSource.OBSERVED,
                confidence_score=1.0,
                payload={
                    "topic": topic,
                    "score": score,
                    "mastery_level": new_mastery,
                    "attempt_type": evidence.attempt_type.value,
                    "questions_correct": evidence.questions_correct,
                    "questions_total": evidence.questions_total,
                },
            )

            mem_engine.record_event(mem_event)
        except Exception as err:
            # Memory sync is non-blocking for mastery intelligence
            print(f"[MasteryEngine] Memory synchronization notice: {err}")

        return MasteryUpdateResult(
            learner_id=learner_id,
            topic=topic,
            previous_mastery=prev_mastery,
            new_mastery=new_mastery,
            mastery_tier=tier,
            mastery_percentage=round(new_mastery * 100.0, 1),
            is_proficient=is_proficient,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            remediation_signal=remediation_sig,
        )


_mastery_engine: Optional[MasteryEngine] = None


def get_mastery_engine() -> MasteryEngine:
    """Singleton provider for MasteryEngine."""
    global _mastery_engine
    if _mastery_engine is None:
        _mastery_engine = MasteryEngine()
    return _mastery_engine

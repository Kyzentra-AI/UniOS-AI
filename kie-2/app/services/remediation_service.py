import uuid
from typing import Optional
from app.schemas.learner import LearnerState, LearnerStage, ConfidenceLevel
from app.schemas.context import NormalizedLearningContext
from app.schemas.mastery import (
    MasteryTier,
    AssessmentAttemptType,
    AssessmentEvidence,
    ClosedLoopStep,
    ClosedLoopResult,
)
from app.services.mastery_engine import get_mastery_engine
from app.services.pedagogy_engine import get_pedagogy_engine
from app.services.memory_engine import get_memory_engine


class RemediationLoopService:
    """Universal AI/ML-2 Remediation Closed-Loop Engine (Task A2-S4-04).
    
    Orchestrates the complete adaptive feedback loop:
    Performance (Assessment Result)
    ↓
    Mastery Update (BRD Tiers)
    ↓
    Weakness / Friction Detection
    ↓
    Remediation Strategy (Scaffolding & Prerequisite Review)
    ↓
    Reassessment
    ↓
    Updated Learner State & Next Action
    """

    def __init__(self):
        self.mastery_engine = get_mastery_engine()
        self.pedagogy_engine = get_pedagogy_engine()
        self.memory_engine = get_memory_engine()

    def run_remediation_cycle(
        self,
        learner_id: str,
        topic: str,
        initial_score: float,
        reassessment_score: Optional[float] = None,
        learner_stage: LearnerStage = LearnerStage.BACHELOR,
        academic_domain: Optional[str] = None,
    ) -> ClosedLoopResult:
        """Executes or simulates a full closed-loop remediation cycle."""
        cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
        clean_id = learner_id.strip()
        clean_topic = topic.strip()
        steps = []

        # 1. Step 1: Initial Assessment Evaluation
        initial_evidence = AssessmentEvidence(
            learner_id=clean_id,
            topic=clean_topic,
            score=initial_score,
            attempt_type=AssessmentAttemptType.FORMATIVE,
        )
        initial_result = self.mastery_engine.evaluate_assessment(initial_evidence)
        steps.append(
            ClosedLoopStep(
                step_name="initial_assessment",
                status="completed",
                evidence_score=initial_score,
                mastery_level=initial_result.new_mastery,
                strategy_applied="diagnostic_evaluation",
                notes=f"Initial score {initial_score:.2f} placed learner in '{initial_result.mastery_tier.value}' tier.",
            )
        )

        remediation_needed = initial_result.remediation_signal.remediation_required

        # 2. Step 2: Formulate Remedial Pedagogy Decision
        learner_state = LearnerState(
            learner_id=clean_id,
            stage=learner_stage,
            confidence=ConfidenceLevel.LOW if initial_score < 0.50 else ConfidenceLevel.MEDIUM,
            concept_mastery={clean_topic: initial_result.new_mastery},
            weak_topics=[clean_topic] if remediation_needed else [],
            academic_domain=academic_domain,
        )
        context = NormalizedLearningContext(
            context_id=f"ctx_{cycle_id}",
            topic=clean_topic,
            objective=f"Master fundamental mechanics and overcome active difficulty in {clean_topic}",
            learner_state=learner_state,
            academic_domain=academic_domain,
        )
        pedagogy = self.pedagogy_engine.determine_pedagogy(context)

        steps.append(
            ClosedLoopStep(
                step_name="pedagogy_formulation",
                status="completed",
                strategy_applied=pedagogy.strategy.value,
                notes=(
                    f"Pedagogy decision: strategy='{pedagogy.strategy.value}', difficulty='{pedagogy.difficulty.value}', "
                    f"remediation={pedagogy.remediation}."
                ),
            )
        )

        # 3. Step 3: Handle Reassessment if provided
        final_tier = initial_result.mastery_tier
        progression_status = "remediation_active" if remediation_needed else "on_track"
        next_action = initial_result.remediation_signal.recommended_action

        if reassessment_score is not None:
            reassessment_evidence = AssessmentEvidence(
                learner_id=clean_id,
                topic=clean_topic,
                score=reassessment_score,
                attempt_type=AssessmentAttemptType.REASSESSMENT,
            )
            reassessment_result = self.mastery_engine.evaluate_assessment(reassessment_evidence)
            final_tier = reassessment_result.mastery_tier

            steps.append(
                ClosedLoopStep(
                    step_name="reassessment",
                    status="completed",
                    evidence_score=reassessment_score,
                    mastery_level=reassessment_result.new_mastery,
                    notes=f"Reassessment score {reassessment_score:.2f} resulted in '{final_tier.value}' mastery.",
                )
            )

            if reassessment_score >= 0.80 or final_tier == MasteryTier.PROFICIENT:
                progression_status = "remediated_proficient"
                next_action = f"Promote learner to next sequential topic or practical application in {clean_topic}."
            elif reassessment_score >= 0.50:
                progression_status = "remediation_in_progress"
                next_action = f"Provide targeted reinforcement practice on {clean_topic} to achieve proficiency."
            else:
                progression_status = "escalated"
                next_action = f"Escalate struggle on {clean_topic} to core prerequisite review and tutor assistance."

        return ClosedLoopResult(
            cycle_id=cycle_id,
            learner_id=clean_id,
            topic=clean_topic,
            initial_score=initial_score,
            initial_tier=initial_result.mastery_tier,
            remediation_applied=remediation_needed,
            remediation_strategy=pedagogy.strategy.value,
            reassessment_score=reassessment_score,
            final_tier=final_tier,
            progression_status=progression_status,
            next_recommended_action=next_action,
            steps=steps,
        )


_remediation_service: Optional[RemediationLoopService] = None


def get_remediation_service() -> RemediationLoopService:
    """Singleton provider for RemediationLoopService."""
    global _remediation_service
    if _remediation_service is None:
        _remediation_service = RemediationLoopService()
    return _remediation_service

from typing import Any

from app.schemas.learning_interpreter import (
    LearningInterpretRequest,
    LearningInterpretResponse,
)


class LearningRequestInterpreter:
    """Sprint 4 AI/ML-1 learning request interpreter."""

    REMEDIATION_TERMS = (
        "struggling",
        "confused",
        "don't understand",
        "do not understand",
        "wrong answer",
        "incorrect",
        "weak",
        "revise",
        "remediate",
        "help me again",
        "explain again",
        "practice more",
    )

    CLARIFICATION_TERMS = (
        "clarify",
        "what does",
        "what is",
        "what are",
        "explain",
        "meaning of",
        "how does",
        "how do",
        "help me understand",
    )

    def interpret(
        self,
        request: LearningInterpretRequest,
    ) -> LearningInterpretResponse:
        user_intent = request.user_intent.strip().lower()
        context = request.context

        if any(
            term in user_intent
            for term in self.REMEDIATION_TERMS
        ):
            category = "REMEDIATION"
            strategy = "GUIDED_REMEDIATION"
            notes = (
                "The request contains wording associated "
                "with difficulty or a need for additional practice."
            )

        elif any(
            term in user_intent
            for term in self.CLARIFICATION_TERMS
        ):
            category = "CLARIFICATION"
            strategy = "CONCEPT_EXPLANATION"
            notes = (
                "The request appears to seek clarification "
                "or an explanation of the topic."
            )

        else:
            category = "NEXT_TOPIC"
            strategy = "STRUCTURED_LEARNING"
            notes = (
                "No explicit clarification or remediation "
                "signal was detected; defaulting to a structured "
                "learning request."
            )

        knowledge_gaps = self._identify_gaps(context)
        difficulty = self._recommend_difficulty(context)

        return LearningInterpretResponse(
            request_id=request.request_id,
            intent_category=category,
            pedagogical_strategy=strategy,
            knowledge_gaps_identified=knowledge_gaps,
            recommended_difficulty=difficulty,
            internal_notes=notes,
        )

    @staticmethod
    def _identify_gaps(
        context: dict[str, Any],
    ) -> list[str]:
        gaps: list[str] = []

        for key in ("knowledge_gaps", "weak_topics", "weak_areas"):
            value = context.get(key)

            if isinstance(value, list):
                gaps.extend(
                    item for item in value
                    if isinstance(item, str) and item.strip()
                )

        # Preserve order and remove duplicates.
        return list(dict.fromkeys(gaps))

    @staticmethod
    def _recommend_difficulty(
        context: dict[str, Any],
    ) -> int:
        learner = context.get("learner", {})
        if not isinstance(learner, dict):
            learner = {}

        level = str(
            learner.get("knowledge_level", "")
            or learner.get("current_level", "")
        ).lower()

        if level in {"beginner", "novice", "basic"}:
            return 1

        if level in {"intermediate", "developing"}:
            return 3

        if level in {"advanced", "expert"}:
            return 5

        return 3
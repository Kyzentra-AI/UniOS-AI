"""
UniOS — Assessment & Mastery Evaluation Service (AI/ML KIE)
Tasks:
  - Dynamic Assessment Generation (POST /api/v1/kie/assessments/generate)
  - Attempt Evaluation & Mastery Updates (POST /api/v1/kie/mastery/evaluate)
"""

import logging
from typing import Any, Dict, List, Optional
from pydantic import ValidationError

from app.schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentQuestion,
    AssessmentOption,
    AssessmentRubric,
    MasteryEvaluateRequest,
    MasteryEvaluateResponse,
    QuestionEvaluation,
    TopicMasteryDetail,
)
from app.services.assessment_prompt_builder import (
    build_assessment_generation_prompt,
    build_mastery_evaluation_prompt,
)
from app.services.llm_provider import (
    BaseLLMProvider,
    LLMParseError,
    LLMProviderError,
    MockLLMProvider,
    get_llm_provider,
)

logger = logging.getLogger(__name__)


class AssessmentService:
    """Core orchestration service for dynamic assessment synthesis and mastery attempt evaluation."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self._mock_provider = MockLLMProvider()

    def generate_assessment(
        self, request: AssessmentGenerateRequest
    ) -> AssessmentGenerateResponse:
        """Synthesize questions with private answer keys and rubrics."""
        prompt = build_assessment_generation_prompt(request)

        raw_data: Optional[Dict[str, Any]] = None
        try:
            raw_data = self.provider.generate_assessment(prompt)
        except (LLMProviderError, LLMParseError, Exception) as err:
            logger.warning(
                f"[AssessmentService] Provider failed for topic '{request.topic}' ({err}); falling back to deterministic mock provider."
            )
            raw_data = self._mock_provider.generate_assessment(prompt)

        try:
            return AssessmentGenerateResponse.model_validate(raw_data)
        except ValidationError as val_err:
            logger.error(
                f"[AssessmentService] Schema validation error on generated assessment: {val_err}. Generating fallback."
            )
            fallback_data = self._mock_provider.generate_assessment(prompt)
            return AssessmentGenerateResponse.model_validate(fallback_data)

    def evaluate_mastery(
        self, request: MasteryEvaluateRequest
    ) -> MasteryEvaluateResponse:
        """Evaluate submitted attempt, score responses, and compute hierarchical mastery deltas."""
        prompt = build_mastery_evaluation_prompt(request)

        raw_data: Optional[Dict[str, Any]] = None
        try:
            raw_data = self.provider.evaluate_mastery_attempt(prompt)
        except (LLMProviderError, LLMParseError, Exception) as err:
            logger.warning(
                f"[AssessmentService] Provider failed for mastery evaluation '{request.topic}' ({err}); falling back to deterministic mock."
            )
            raw_data = self._mock_provider.evaluate_mastery_attempt(prompt)

        try:
            # Ensure score is clamped strictly between 0.0 and 1.0
            if "score" in raw_data:
                raw_data["score"] = max(0.0, min(1.0, float(raw_data["score"])))
            return MasteryEvaluateResponse.model_validate(raw_data)
        except ValidationError as val_err:
            logger.error(
                f"[AssessmentService] Schema validation error on mastery evaluation: {val_err}. Generating fallback."
            )
            fallback_data = self._mock_provider.evaluate_mastery_attempt(prompt)
            return MasteryEvaluateResponse.model_validate(fallback_data)


_assessment_service_instance: Optional[AssessmentService] = None


def get_assessment_service() -> AssessmentService:
    """Singleton accessor for AssessmentService."""
    global _assessment_service_instance
    if _assessment_service_instance is None:
        _assessment_service_instance = AssessmentService()
    return _assessment_service_instance

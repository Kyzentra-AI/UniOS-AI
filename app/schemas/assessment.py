"""
UniOS — Assessments & Mastery Evaluation Schemas (AI/ML KIE)
Contracts for:
  - POST /api/v1/kie/assessments/generate (Dynamic Assessment Synthesis with Private Keys/Rubrics)
  - POST /api/v1/kie/mastery/evaluate    (Attempt Evaluation & Hierarchical Mastery Graph Delta)
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class AssessmentQuestionType(str, Enum):
    MCQ = "mcq"
    SUBJECTIVE = "subjective"
    VIVA = "viva"
    CASE_STUDY = "case-study"
    CODING = "coding"


class AssessmentOption(BaseModel):
    """An option choice for multiple-choice questions."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Stable option ID (e.g. 'opt-1')")
    text: str = Field(..., description="Option text content")


class QuestionRubric(BaseModel):
    """Grading rubric for non-MCQ questions (coding, subjective, viva, case-study)."""
    model_config = ConfigDict(populate_by_name=True)

    required_clauses: Optional[List[str]] = Field(
        default=None,
        validation_alias=AliasChoices("required_clauses", "requiredClauses"),
        description="Required keywords or clauses",
    )
    ideal_solution: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ideal_solution", "idealSolution"),
        description="Ideal or reference response",
    )
    criteria: Optional[List[str]] = Field(
        default=None, description="Key grading criteria"
    )
    key_points: Optional[List[str]] = Field(
        default=None,
        validation_alias=AliasChoices("key_points", "keyPoints"),
        description="Required conceptual points",
    )


class AssessmentQuestion(BaseModel):
    """Individual assessment question entity."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Stable question identifier (e.g. 'q1')")
    type: str = Field(
        default="mcq",
        description="Question type ('mcq' | 'subjective' | 'viva' | 'case-study' | 'coding')",
    )
    question: str = Field(..., description="The question text or problem prompt")
    options: Optional[List[AssessmentOption]] = Field(
        default=None, description="Selectable options (required for 'mcq')"
    )
    correct_option_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("correct_option_id", "correctOptionId"),
        description="Private answer key matching an option id for MCQs",
    )
    explanation: Optional[str] = Field(
        default=None, description="Pedagogical explanation of the correct answer"
    )
    code: Optional[str] = Field(
        default=None, description="Initial starter code snippet for coding questions"
    )
    language: Optional[str] = Field(
        default=None, description="Programming language for coding problems (e.g. 'sql', 'python')"
    )
    rubric: Optional[Union[QuestionRubric, Dict[str, Any]]] = Field(
        default=None, description="Grading criteria and ideal solution for subjective/coding questions"
    )


class AssessmentRubric(BaseModel):
    """Overall assessment scoring and passing threshold configuration."""
    model_config = ConfigDict(populate_by_name=True)

    total_points: float = Field(
        default=2.0,
        validation_alias=AliasChoices("total_points", "totalPoints"),
        description="Total score points possible",
    )
    passing_threshold: float = Field(
        default=0.70,
        validation_alias=AliasChoices("passing_threshold", "passingThreshold"),
        ge=0.0,
        le=1.0,
        description="Minimum score ratio to pass",
    )


class AssessmentGenerateRequest(BaseModel):
    """Inbound request from FastAPI Backend to generate a dynamic assessment."""
    model_config = ConfigDict(populate_by_name=True)

    learner_id: str = Field(
        ...,
        validation_alias=AliasChoices("learner_id", "learnerId"),
        min_length=1,
        description="Learner UUID",
    )
    session_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("session_id", "sessionId"),
        description="Session identifier",
    )
    lesson_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("lesson_id", "lessonId"),
        description="Lesson identifier",
    )
    topic: str = Field(..., min_length=1, description="Curriculum or assessment topic")
    preferred_type: Optional[str] = Field(
        default="mcq",
        validation_alias=AliasChoices("preferred_type", "preferredType"),
        description="Preferred question type (mcq, coding, subjective, viva, case-study)",
    )
    question_count: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        validation_alias=AliasChoices("question_count", "questionCount"),
        description="Target number of questions to generate",
    )
    difficulty: Optional[str] = Field(
        default="PROFICIENT",
        description="Target difficulty level (NOVICE, DEVELOPING, PROFICIENT, MASTERED)",
    )

    @field_validator("topic")
    @classmethod
    def validate_topic_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("topic cannot be empty or whitespace.")
        return cleaned


class AssessmentGenerateResponse(BaseModel):
    """Outbound response containing questions with private answer keys & rubrics."""
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., description="Assessment title")
    type: str = Field(default="mcq", description="Dominant assessment type")
    instructions: str = Field(..., description="Learner-facing instructions")
    questions: List[AssessmentQuestion] = Field(..., description="Synthesized questions with answer keys")
    rubric: Union[AssessmentRubric, Dict[str, Any]] = Field(
        ..., description="Overall scoring rubric and threshold"
    )


# ============================================================================
# Mastery Evaluation Schemas (POST /api/v1/kie/mastery/evaluate)
# ============================================================================

class SubmittedAnswer(BaseModel):
    """Student's submitted response to an individual assessment question."""
    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(
        ...,
        validation_alias=AliasChoices("question_id", "questionId"),
        description="Referenced question ID",
    )
    answer: str = Field(..., description="Submitted option ID or textual / code solution")
    hints_used: Optional[int] = Field(
        default=0,
        validation_alias=AliasChoices("hints_used", "hintsUsed"),
        ge=0,
        description="Count of hints requested",
    )
    time_spent_seconds: Optional[int] = Field(
        default=0,
        validation_alias=AliasChoices("time_spent_seconds", "timeSpentSeconds"),
        ge=0,
        description="Time spent on this question",
    )


class MasteryEvaluateRequest(BaseModel):
    """Inbound request from FastAPI Backend to evaluate attempt and compute mastery delta."""
    model_config = ConfigDict(populate_by_name=True)

    learner_id: str = Field(
        ...,
        validation_alias=AliasChoices("learner_id", "learnerId"),
        min_length=1,
        description="Learner UUID",
    )
    assessment_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("assessment_id", "assessmentId"),
        description="Assessment identifier",
    )
    topic: str = Field(..., min_length=1, description="Assessed curriculum topic")
    total_time_spent_seconds: Optional[int] = Field(
        default=0,
        validation_alias=AliasChoices("total_time_spent_seconds", "totalTimeSpentSeconds"),
        ge=0,
        description="Total seconds taken for attempt",
    )
    answers: List[SubmittedAnswer] = Field(default_factory=list, description="Submitted question answers")

    @field_validator("topic")
    @classmethod
    def validate_topic_not_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("topic cannot be empty or whitespace.")
        return cleaned


class QuestionEvaluation(BaseModel):
    """Granular evaluation result for a single question response."""
    model_config = ConfigDict(populate_by_name=True)

    question_id: str = Field(
        ...,
        validation_alias=AliasChoices("question_id", "questionId"),
        description="Referenced question ID",
    )
    is_correct: bool = Field(
        ...,
        validation_alias=AliasChoices("is_correct", "isCorrect"),
        description="Whether response meets passing criteria",
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized question score (0.0 to 1.0)")
    feedback: str = Field(..., description="Actionable qualitative feedback for learner")


class TopicMasteryDetail(BaseModel):
    """Mastery update details for a specific sub-topic or skill node."""
    model_config = ConfigDict(populate_by_name=True)

    score: float = Field(..., ge=0.0, le=1.0, description="Updated absolute mastery score (0.0 to 1.0)")
    status: str = Field(..., description="Mastery classification: NOVICE | DEVELOPING | PROFICIENT | MASTERED")
    delta: float = Field(..., description="Score change delta relative to prior mastery")
    reason: str = Field(..., description="Pedagogical rationale for the mastery update")


class MasteryEvaluateResponse(BaseModel):
    """Outbound response with normalized score, feedback, and nested mastery delta."""
    model_config = ConfigDict(populate_by_name=True)

    score: float = Field(..., ge=0.0, le=1.0, description="Normalized total attempt score between 0.0 and 1.0")
    feedback: str = Field(..., description="Overall executive pedagogical feedback")
    question_evaluations: List[QuestionEvaluation] = Field(
        ...,
        validation_alias=AliasChoices("question_evaluations", "questionEvaluations"),
        description="Question-level evaluations",
    )
    mastery_updates: Dict[str, Dict[str, Union[TopicMasteryDetail, Dict[str, Any]]]] = Field(
        ...,
        validation_alias=AliasChoices("mastery_updates", "masteryUpdates"),
        description='Nested mastery mapping: { "<Subject>": { "<Topic>": { "score": float, "status": str, "delta": float, "reason": str } } }',
    )

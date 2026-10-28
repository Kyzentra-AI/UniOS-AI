from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    CONCEPTUAL_EXPLANATION = "CONCEPTUAL_EXPLANATION"
    CODE_WALKTHROUGH = "CODE_WALKTHROUGH"
    REVISION = "REVISION"
    EXAM_PREP = "EXAM_PREP"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"


class PedagogicalStrategy(str, Enum):
    ANALOGY_THEN_CODE = "ANALOGY_THEN_CODE"
    SOCRATIC_INQUIRY = "SOCRATIC_INQUIRY"
    HANDS_ON_FIRST = "HANDS_ON_FIRST"
    STEP_BY_STEP_DERIVATION = "STEP_BY_STEP_DERIVATION"


class InterpretRequest(BaseModel):
    """Section 14.1.1 Payload Sent by Backend → KIE (AI-1 Request)."""

    request_id: str = Field(..., description="Correlation ID for distributed tracing")
    learner_id: str = Field(..., description="Identifier of the learner")
    topic: str = Field(..., description="Current topic being studied")
    user_intent: str = Field(default="", description="Explicit learner guidance/prompt from client")
    references: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Grounding excerpts extracted from syllabus",
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Unified multi-dimensional ContextV2 assembled for the learner",
    )


class InterpretResponse(BaseModel):
    """Section 14.1.2 Payload Expected from KIE → Backend (AI-1 Response)."""

    intent_category: str = Field(
        ...,
        description="Categorized learner intent (CONCEPTUAL_EXPLANATION, CODE_WALKTHROUGH, REVISION, EXAM_PREP, PROBLEM_SOLVING)",
    )
    pedagogical_strategy: str = Field(
        ...,
        description="Teaching strategy (ANALOGY_THEN_CODE, SOCRATIC_INQUIRY, HANDS_ON_FIRST, STEP_BY_STEP_DERIVATION)",
    )
    knowledge_gaps_identified: List[str] = Field(
        default_factory=list,
        description="Pre-requisite or conceptual gaps identified from learner context & history",
    )
    target_difficulty: Optional[str] = Field(
        default="INTERMEDIATE",
        description="Recommended difficulty tier (BEGINNER, INTERMEDIATE, ADVANCED)",
    )
    recommended_block_flow: Optional[List[str]] = Field(
        default_factory=lambda: ["TEXT", "CODE", "INTERACTIVE", "QUIZ"],
        description="Recommended sequence of block types",
    )
    key_concepts_to_cover: Optional[List[str]] = Field(
        default_factory=list,
        description="Key conceptual milestones to address in the lesson",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional pedagogical annotations (scaffolding level, read minutes, etc.)",
    )

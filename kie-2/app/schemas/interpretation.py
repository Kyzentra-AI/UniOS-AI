import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


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

    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Correlation ID for distributed tracing",
    )
    learner_id: Optional[str] = Field(
        default="learner_001",
        description="Identifier of the learner",
    )
    topic: Optional[str] = Field(
        default="General Concepts",
        description="Current topic being studied",
    )
    user_intent: Optional[str] = Field(
        default="",
        description="Explicit learner guidance/prompt from client",
    )
    references: Optional[List[Any]] = Field(
        default_factory=list,
        description="Grounding excerpts extracted from syllabus",
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Unified multi-dimensional ContextV2 assembled for the learner",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_interpret_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if not data.get("request_id"):
            data["request_id"] = str(uuid.uuid4())
        if not data.get("learner_id"):
            data["learner_id"] = data.get("user_id") or "learner_001"
        if not data.get("topic"):
            data["topic"] = data.get("current_topic") or data.get("title") or "General Concepts"
        if data.get("user_intent") is None:
            data["user_intent"] = ""

        # Normalize references (can be strings, dicts, or None)
        raw_refs = data.get("references")
        if raw_refs is None:
            data["references"] = []
        elif isinstance(raw_refs, list):
            cleaned_refs = []
            for r in raw_refs:
                if isinstance(r, dict):
                    cleaned_refs.append(r)
                elif r is not None:
                    cleaned_refs.append({"content": str(r)})
            data["references"] = cleaned_refs
        else:
            data["references"] = [{"content": str(raw_refs)}]

        if data.get("context") is None or not isinstance(data["context"], dict):
            data["context"] = {}

        return data


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

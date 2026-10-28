from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from app.schemas.learner import LearnerState
from app.schemas.memory_context import RelevantMemoryContext


class NormalizedLearningContext(BaseModel):
    """The normalized context payload passed to AI/ML-2 for pedagogy and generation.
    Supports both legacy context_id and canonical cross-service request_id.
    Defensively normalizes simplified payloads to eliminate 422 Unprocessable Content errors.
    """

    context_id: str = "ctx_001"
    request_id: Optional[str] = Field(
        default=None,
        description="Canonical cross-service tracing ID (synced with context_id)",
    )
    topic: str
    objective: str
    learner_id: Optional[str] = Field(
        default=None,
        description="Optional top-level learner identifier shortcut",
    )
    learner_state: LearnerState = Field(
        default_factory=LearnerState,
        description="Learner state object containing academic stage and preferences",
    )
    lesson_id: Optional[str] = Field(
        default=None,
        description="Target lesson identifier from Backend (mapped to context_id)",
    )
    user_intent: Optional[str] = Field(
        default=None,
        description="Explicit learner prompt or intent from Backend/AI-1",
    )
    interpreted_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full AI-1 interpretation data from POST /api/v1/kie/learn/interpret",
    )
    references: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Grounding syllabus reference objects from Backend ContentReferenceService",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Unified ContextV2 assembled for the learner",
    )
    curriculum_references: List[str] = Field(
        default_factory=list,
        description="Grounded excerpts from syllabus or approved textbooks",
    )
    time_budget_minutes: Optional[int] = 15
    memory_context: Optional[RelevantMemoryContext] = Field(
        default=None,
        description="Optional scoped memory intelligence from AI/ML-2 Memory Engine",
    )
    academic_domain: Optional[str] = Field(
        default=None,
        description="Canonical academic domain (e.g. engineering, commerce, humanities, science, management, law)",
    )
    academic_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed academic context dictionary from Backend",
    )
    content_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Approved syllabus and reference material from Backend/retrieval",
    )
    performance: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Recent learner performance telemetry from Backend",
    )
    mastery: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Authoritative topic mastery records from Backend",
    )
    goals: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Active academic and career goals",
    )
    request_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Interpreted request context from AI/ML-1",
    )

    @model_validator(mode="before")
    @classmethod
    def pre_normalize_context(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # If data is completely empty or has no topic, let standard Pydantic validation reject it
        topic = data.get("topic") or data.get("current_topic") or data.get("title")
        if not topic:
            return data

        data["topic"] = topic

        # Ensure objective exists if topic is provided
        if not data.get("objective"):
            data["objective"] = f"Understand and apply core concepts of {topic}."

        top_lid = data.get("learner_id")
        raw_state = data.get("learner_state")

        # Sync lesson_id to context_id if present
        if data.get("lesson_id") and (not data.get("context_id") or data.get("context_id") == "ctx_001"):
            data["context_id"] = data["lesson_id"]

        # Extract references from backend references list
        if data.get("references") and not data.get("curriculum_references"):
            refs_extracted = []
            for r in data["references"]:
                if isinstance(r, dict):
                    content = r.get("content") or r.get("heading") or r.get("module")
                    if content:
                        refs_extracted.append(content)
                elif isinstance(r, str):
                    refs_extracted.append(r)
            if refs_extracted:
                data["curriculum_references"] = refs_extracted

        # Ingest Backend ContextV2 if present
        backend_ctx = data.get("context")
        if isinstance(backend_ctx, dict):
            ctx_lid = backend_ctx.get("learner_id")
            if ctx_lid and not top_lid:
                top_lid = ctx_lid
                data["learner_id"] = ctx_lid
            edu = backend_ctx.get("education") or {}
            learner_info = backend_ctx.get("learner") or {}
            if not raw_state:
                raw_stage = str(edu.get("academic_status") or "bachelor").lower()
                if raw_stage not in ["bachelor", "master", "graduate"]:
                    raw_stage = "bachelor"
                data["learner_state"] = {
                    "learner_id": top_lid or "learner_001",
                    "stage": raw_stage,
                    "academic_program": edu.get("degree_program") or "Computer Science",
                    "academic_domain": edu.get("domain") or data.get("academic_domain"),
                    "confidence": "medium",
                    "weak_topics": [topic] if data.get("remediation") else [],
                    "strong_topics": learner_info.get("skills") or [],
                    "career_goal": learner_info.get("primary_goal"),
                }
                raw_state = data["learner_state"]

        # Normalize learner_state if absent or incomplete
        if raw_state is None:
            data["learner_state"] = {
                "learner_id": top_lid or "learner_001",
                "stage": data.get("stage") or data.get("learner_stage") or "bachelor",
                "academic_program": data.get("academic_program", "Computer Science"),
                "academic_domain": data.get("academic_domain"),
                "confidence": data.get("confidence", "medium"),
                "weak_topics": [topic] if data.get("remediation") else [],
            }
        elif isinstance(raw_state, dict):
            if top_lid and not raw_state.get("learner_id"):
                raw_state["learner_id"] = top_lid
            if not raw_state.get("learner_id"):
                raw_state["learner_id"] = "learner_001"
            if not raw_state.get("stage") and (data.get("stage") or data.get("learner_stage")):
                raw_state["stage"] = data.get("stage") or data.get("learner_stage")
            if not raw_state.get("academic_program"):
                raw_state["academic_program"] = data.get("academic_program", "Computer Science")
            if data.get("academic_domain") and not raw_state.get("academic_domain"):
                raw_state["academic_domain"] = data.get("academic_domain")
            data["learner_state"] = raw_state

        return data

    def model_post_init(self, __context):
        # Sync request_id and context_id
        if self.request_id is None and self.context_id:
            self.request_id = self.context_id
        elif self.context_id == "ctx_001" and self.request_id:
            self.context_id = self.request_id

        # Sync top-level learner_id into learner_state if needed
        if self.learner_id and self.learner_state:
            if not self.learner_state.learner_id or self.learner_state.learner_id == "learner_001":
                self.learner_state.learner_id = self.learner_id

        # Sync academic_domain to learner_state if specified
        if self.academic_domain and self.learner_state:
            if not self.learner_state.academic_domain:
                self.learner_state.academic_domain = self.academic_domain

        # Extract content references from content_context if curriculum_references is empty
        if self.content_context and not self.curriculum_references:
            refs = self.content_context.get("relevant_content", [])
            if isinstance(refs, list):
                extracted = []
                for item in refs:
                    if isinstance(item, str):
                        extracted.append(item)
                    elif isinstance(item, dict) and "text" in item:
                        extracted.append(item["text"])
                    elif isinstance(item, dict) and "excerpt" in item:
                        extracted.append(item["excerpt"])
                if extracted:
                    self.curriculum_references = extracted

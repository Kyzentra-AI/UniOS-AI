"""
Sprint 5 — Universal Build Engine Endpoints (AI/ML-2)

Routes:
  POST /api/v1/kie/build/coach       — Contextual Build Coach
  GET  /api/v1/kie/build/recommend   — Project Recommendations

These are registered on the /kie/build prefix in api.py.
Route handlers are thin wrappers; business logic lives in BuildCoachService.

Public contract (Backend-approved):
  Coach:   request → {intent, message, context, project_context}
           response → {reply, suggestions, action_items}
  Recommend: request → ?learner_id={learner_id}
             response → {learner_id, recommendations, recommendation_rationale, generated_at}
             each recommendation → {title, description, type, skills, ...}
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.build import (
    ArtifactType,
    BuildCoachPublicRequest,
    BuildCoachPublicResponse,
    BuildCoachRequest,
    BuildRecommendContext,
    BuildRecommendResponse,
)
from app.services.build_coach_service import (
    coaching_response_to_public,
    get_build_coach_service,
)
from app.services.llm_provider import LLMParseError, LLMProviderError

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /coach
# ---------------------------------------------------------------------------

@router.post(
    "/coach",
    response_model=BuildCoachPublicResponse,
    status_code=status.HTTP_200_OK,
    summary="Contextual Build Coach (A2-S5-01)",
    description=(
        "Accepts a learner's coaching intent, message, and project context from Backend / AI/ML-1, "
        "then generates domain-adaptive, evidence-driven coaching. "
        "Returns a structured reply with coaching suggestions and actionable next steps. "
        "Supports all academic artifact types: code projects, essays, lab reports, "
        "business plans, case analyses, oral vivas, and portfolios. "
        "AI/ML-2 never stores the raw artifact binary — Backend owns project persistence."
    ),
    responses={
        200: {"description": "Structured coaching response returned."},
        422: {"description": "Validation error: Malformed request payload."},
        429: {"description": "Too Many Requests: LLM provider rate limit exceeded."},
        502: {"description": "Bad Gateway: LLM provider unavailable or response invalid."},
        504: {"description": "Gateway Timeout: LLM provider connection timeout."},
    },
)
def build_coach(public_request: BuildCoachPublicRequest) -> BuildCoachPublicResponse:
    """
    AI/ML-2 interface: Generates contextual build coaching intelligence.

    Maps the public wire request to the internal coaching engine:
      intent          → coaching focus (informs prompt construction)
      message         → struggle_description
      context         → supplementary context (academic_domain, stage, milestone parsed)
      project_context → project_title, artifact_type, rubric_criteria (skills)

    Returns the Backend-approved response: reply, suggestions, action_items.
    """
    # --- Map public request → internal BuildCoachRequest ---
    pc = public_request.project_context
    project_title = (pc.title if pc and pc.title else "Build Project").strip() or "Build Project"

    # Resolve artifact type from project_context.type
    artifact_type = ArtifactType.GENERAL
    if pc and pc.type:
        try:
            artifact_type = ArtifactType(pc.type.strip().lower())
        except ValueError:
            artifact_type = ArtifactType.GENERAL

    # Rubric criteria from project skills
    rubric_criteria = (pc.skills or []) if pc else []

    # Parse academic domain and learner stage from context string (best-effort)
    context_str = (public_request.context or "").lower()
    academic_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law", "finance"]:
        if domain_kw in context_str:
            academic_domain = domain_kw
            break
    for stage_kw in ["master", "graduate", "bachelor"]:
        if stage_kw in context_str:
            learner_stage = stage_kw
            break

    # Generate a stable request_id for tracing (not exposed on public API)
    request_id = f"coach_{uuid.uuid4().hex[:12]}"

    # Learner ID: use project_context.id if available, else a generic placeholder
    learner_id = (pc.id or "anonymous").strip() if pc else "anonymous"
    # Ensure learner_id only contains safe chars for the internal validator
    import re as _re
    if not _re.match(r"^[a-zA-Z0-9_\-\.:@/]+$", learner_id):
        learner_id = "anonymous"

    internal_request = BuildCoachRequest(
        request_id=request_id,
        learner_id=learner_id,
        project_title=project_title,
        artifact_type=artifact_type,
        academic_domain=academic_domain,
        struggle_description=public_request.message,
        submitted_work_summary=public_request.context,
        learner_stage=learner_stage,
        rubric_criteria=rubric_criteria if rubric_criteria else None,
    )

    print(
        f"\n>>> [API /api/v1/kie/build/coach] "
        f"intent={public_request.intent!r} project={project_title!r} "
        f"artifact={artifact_type.value} domain={academic_domain or 'general'}"
    )

    service = get_build_coach_service()
    try:
        internal_response = service.generate_coaching(internal_request)
    except LLMParseError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Build coaching response could not be parsed: {err.message}",
        )
    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error in build coach: {str(err)}",
        )

    # Map internal response → public wire response
    public_response = coaching_response_to_public(internal_response)

    print(
        f">>> [API /api/v1/kie/build/coach] "
        f"reply={len(public_response.reply)} chars, "
        f"suggestions={len(public_response.suggestions)}, "
        f"action_items={len(public_response.action_items)}"
    )
    return public_response


# ---------------------------------------------------------------------------
# GET /recommend
# ---------------------------------------------------------------------------

@router.get(
    "/recommend",
    response_model=BuildRecommendResponse,
    status_code=status.HTTP_200_OK,
    summary="Project Recommendations (A2-S5-02)",
    description=(
        "Returns a ranked list of domain-adaptive build project recommendations "
        "for a learner. Only learner_id is required as the public query parameter. "
        "Learner context (skills, goals, domain) is retrieved from the AI/ML-2 "
        "Sprint 3 memory engine where available. "
        "Each recommendation exposes: title, description, type, and skills. "
        "Backend is responsible for persisting any selected recommendation as a project record."
    ),
    responses={
        200: {"description": "Project recommendations returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
        500: {"description": "Internal error generating recommendations."},
    },
)
def build_recommend(
    learner_id: str = Query(
        ...,
        min_length=1,
        description="Learner identifier from Backend / KIE. The only required public parameter.",
    ),
) -> BuildRecommendResponse:
    """
    AI/ML-2 interface: Returns domain-adaptive project recommendations.

    Public contract: only learner_id is a documented query parameter.
    Learner context (domain, stage, target role, weak topics, completed milestones)
    is retrieved from the Sprint 3 memory engine (best-effort). If memory has no
    record for this learner, a general fallback recommendation set is returned.
    """
    clean_id = learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )

    print(f"\n>>> [API /api/v1/kie/build/recommend] learner={clean_id!r}")

    # --- Retrieve learner context from Sprint 3 memory engine (best-effort) ---
    academic_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    target_role: Optional[str] = None
    weak_topics: Optional[list] = None
    completed_milestones: Optional[list] = None

    try:
        from app.services.memory_engine import get_memory_engine
        from app.schemas.memory_context import RelevantMemoryQuery

        engine = get_memory_engine()
        query = RelevantMemoryQuery(learner_id=clean_id)
        mem_ctx = engine.retrieve_relevant_context(query)

        # Weak topics from active friction
        weak_topics = [f.topic for f in mem_ctx.relevant_friction if f.unresolved]

        # Completed milestones from active goal
        completed_milestones = mem_ctx.active_goal.completed_milestones or []

        # Target role from active goal
        target_role = mem_ctx.active_goal.primary_target_role or None

        # Academic domain from secondary interests or detected weaknesses
        # secondary_interests may encode domain hints (e.g. "engineering", "commerce")
        for interest in (mem_ctx.active_goal.secondary_interests or []):
            for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law"]:
                if domain_kw in interest.lower():
                    academic_domain = domain_kw
                    break
            if academic_domain:
                break

        # Fallback: infer domain from weak topic content
        if not academic_domain and weak_topics:
            topic_text = " ".join(weak_topics).lower()
            for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law"]:
                if domain_kw in topic_text:
                    academic_domain = domain_kw
                    break

    except Exception:
        # Memory enrichment is best-effort; proceed with empty context
        pass

    context = BuildRecommendContext(
        learner_id=clean_id,
        academic_domain=academic_domain,
        learner_stage=learner_stage,
        target_role=target_role,
        completed_milestones=completed_milestones,
        current_weak_topics=weak_topics,
    )

    # Internal request_id for tracing (not on public API)
    internal_request_id = f"rec_{uuid.uuid4().hex[:12]}"

    service = get_build_coach_service()
    try:
        response = service.generate_recommendations(
            context, request_id=internal_request_id, count=3
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(err)}",
        )

    print(
        f">>> [API /api/v1/kie/build/recommend] "
        f"returning {len(response.recommendations)} recommendations "
        f"domain={academic_domain or 'general'} role={target_role or 'unknown'}"
    )
    return response

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

from fastapi import APIRouter, Body, HTTPException, Query, status

from app.schemas.build import (
    ArtifactType,
    BuildCoachPublicRequest,
    BuildCoachPublicResponse,
    BuildCoachRequest,
    BuildRecommendContext,
    BuildRecommendRequest,
    BuildRecommendResponse,
)
from app.schemas.build_plan import (
    BuildPlanRequest,
    BuildPlanResponse,
)
from app.services.build_coach_service import (
    coaching_response_to_public,
    get_build_coach_service,
)
from app.services.build_plan_service import (
    BuildPlanGenerationEngine,
)
from app.services.llm_provider import LLMParseError, LLMProviderError

router = APIRouter()
_build_plan_engine = BuildPlanGenerationEngine()


# ---------------------------------------------------------------------------
# POST /plan
# ---------------------------------------------------------------------------

@router.post(
    "/plan",
    response_model=BuildPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Universal Build Plan Generator",
    description=(
        "Generates bounded, structured milestones and actionable tasks for "
        "different project artifact types (CODING, RESEARCH, BUSINESS, ANALYSIS, DESIGN). "
        "Backend auto-inserts these into the project workspace."
    ),
    responses={
        200: {"description": "Structured build plan returned successfully."},
        422: {"description": "Validation error: Malformed request payload."},
    },
)
def generate_build_plan(request: BuildPlanRequest) -> BuildPlanResponse:
    """
    Generates domain-adaptive build plan with milestones and tasks.
    Deterministic, instant execution matching backend workspace schema.
    """
    return _build_plan_engine.generate(request)


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
        type_raw = str(pc.type).strip().lower()
        type_map = {
            "coding": ArtifactType.CODE_PROJECT,
            "code": ArtifactType.CODE_PROJECT,
            "code_project": ArtifactType.CODE_PROJECT,
            "research": ArtifactType.RESEARCH_REPORT,
            "research_report": ArtifactType.RESEARCH_REPORT,
            "business": ArtifactType.BUSINESS_PLAN,
            "business_plan": ArtifactType.BUSINESS_PLAN,
            "analysis": ArtifactType.DATA_ANALYSIS,
            "data_analysis": ArtifactType.DATA_ANALYSIS,
            "design": ArtifactType.DESIGN_ARTIFACT,
            "design_artifact": ArtifactType.DESIGN_ARTIFACT,
            "essay": ArtifactType.ESSAY,
            "lab": ArtifactType.LAB_NOTEBOOK,
            "lab_notebook": ArtifactType.LAB_NOTEBOOK,
            "portfolio": ArtifactType.PORTFOLIO,
        }
        if type_raw in type_map:
            artifact_type = type_map[type_raw]
        else:
            try:
                artifact_type = ArtifactType(type_raw)
            except ValueError:
                artifact_type = ArtifactType.GENERAL

    # Rubric criteria from project skills
    rubric_criteria = [str(s) for s in pc.skills if s] if (pc and pc.skills) else []

    # Parse academic domain and learner stage from context (string or dict or list)
    context_str = ""
    if isinstance(public_request.context, (dict, list)):
        import json as _json
        context_str = _json.dumps(public_request.context)
    elif public_request.context:
        context_str = str(public_request.context)

    context_lower = context_str.lower()
    academic_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law", "finance"]:
        if domain_kw in context_lower:
            academic_domain = domain_kw
            break
    for stage_kw in ["master", "graduate", "bachelor"]:
        if stage_kw in context_lower:
            learner_stage = stage_kw
            break

    # Generate a stable request_id for tracing (not exposed on public API)
    request_id = f"coach_{uuid.uuid4().hex[:12]}"

    # Learner ID: use public_request.learner_id, user_id, project_context.id, or generic placeholder
    raw_learner_id = "anonymous"
    if public_request.learner_id:
        raw_learner_id = str(public_request.learner_id).strip()
    elif public_request.user_id:
        raw_learner_id = str(public_request.user_id).strip()
    elif pc and pc.id:
        raw_learner_id = str(pc.id).strip()

    # Ensure learner_id only contains safe chars for the internal validator
    import re as _re
    learner_id = _re.sub(r"[^a-zA-Z0-9_\-\.:@/]", "_", raw_learner_id) or "anonymous"

    submitted_work_summary = context_str[:1900] if context_str else None
    struggle_description = public_request.message[:950] if public_request.message else None

    internal_request = BuildCoachRequest(
        request_id=request_id,
        learner_id=learner_id,
        project_title=project_title,
        artifact_type=artifact_type,
        academic_domain=academic_domain,
        struggle_description=struggle_description,
        submitted_work_summary=submitted_work_summary,
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
# GET & POST /recommend
# ---------------------------------------------------------------------------

def _execute_build_recommend(
    learner_id: Optional[str] = None,
    degree_program: Optional[str] = None,
    academic_domain: Optional[str] = None,
    syllabus_subjects: Optional[list] = None,
    syllabus_topics: Optional[list] = None,
    target_role: Optional[str] = None,
    count: int = 3,
) -> BuildRecommendResponse:
    clean_id = (learner_id or "").strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )

    print(f"\n>>> [API /api/v1/kie/build/recommend] learner={clean_id!r} degree={degree_program!r} domain={academic_domain!r}")

    # --- Retrieve learner context from Sprint 3 memory engine (best-effort) ---
    mem_domain: Optional[str] = None
    learner_stage: Optional[str] = None
    mem_target_role: Optional[str] = None
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
        mem_target_role = mem_ctx.active_goal.primary_target_role or None

        # Academic domain from secondary interests or detected weaknesses
        for interest in (mem_ctx.active_goal.secondary_interests or []):
            for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law"]:
                if domain_kw in interest.lower():
                    mem_domain = domain_kw
                    break
            if mem_domain:
                break

        # Fallback: infer domain from weak topic content
        if not mem_domain and weak_topics:
            topic_text = " ".join(weak_topics).lower()
            for domain_kw in ["engineering", "commerce", "humanities", "science", "management", "law"]:
                if domain_kw in topic_text:
                    mem_domain = domain_kw
                    break

    except Exception:
        # Memory enrichment is best-effort; proceed with empty context
        pass

    effective_domain = academic_domain or mem_domain
    effective_role = target_role or mem_target_role

    context = BuildRecommendContext(
        learner_id=clean_id,
        academic_domain=effective_domain,
        degree_program=degree_program,
        syllabus_subjects=syllabus_subjects,
        syllabus_topics=syllabus_topics,
        learner_stage=learner_stage,
        target_role=effective_role,
        completed_milestones=completed_milestones,
        current_weak_topics=weak_topics,
    )

    # Internal request_id for tracing (not on public API)
    internal_request_id = f"rec_{uuid.uuid4().hex[:12]}"

    service = get_build_coach_service()
    try:
        response = service.generate_recommendations(
            context, request_id=internal_request_id, count=count
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(err)}",
        )

    print(
        f">>> [API /api/v1/kie/build/recommend] "
        f"returning {len(response.recommendations)} recommendations "
        f"domain={effective_domain or 'general'} role={effective_role or 'unknown'}"
    )
    return response


@router.get(
    "/recommend",
    response_model=BuildRecommendResponse,
    status_code=status.HTTP_200_OK,
    summary="Project Recommendations (GET /api/v1/kie/build/recommend)",
    description=(
        "Returns a ranked list of domain-adaptive build project recommendations "
        "for a learner. Only learner_id is required as the public query parameter."
    ),
    responses={
        200: {"description": "Project recommendations returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
        500: {"description": "Internal error generating recommendations."},
    },
)
def build_recommend_get(
    learner_id: str = Query(
        ...,
        min_length=1,
        description="Learner identifier from Backend / KIE. The only required public parameter.",
    ),
) -> BuildRecommendResponse:
    """GET route: accepts learner_id query param for backward compatibility."""
    return _execute_build_recommend(learner_id=learner_id)


@router.post(
    "/recommend",
    response_model=BuildRecommendResponse,
    status_code=status.HTTP_200_OK,
    summary="Project Recommendations (POST /api/v1/kie/build/recommend)",
    description=(
        "Returns a ranked list of syllabus-grounded build project recommendations. "
        "Accepts degree_program, academic_domain, and syllabus subjects/topics."
    ),
    responses={
        200: {"description": "Project recommendations returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
        500: {"description": "Internal error generating recommendations."},
    },
)
def build_recommend_post(
    learner_id: Optional[str] = Query(default=None),
    degree_program: Optional[str] = Query(default=None),
    domain: Optional[str] = Query(default=None),
    payload: Optional[BuildRecommendRequest] = Body(default=None),
) -> BuildRecommendResponse:
    """POST route: supports body and query parameters for full syllabus grounding."""
    eff_id = learner_id or (payload.learner_id if payload else None)
    eff_degree = degree_program or (payload.degree_program if payload else None)
    eff_domain = domain or (payload.academic_domain if payload else None) or (payload.domain if payload else None)
    eff_subjects = payload.syllabus_subjects if payload else None
    eff_topics = payload.syllabus_topics if payload else None
    eff_role = payload.target_role if payload else None
    eff_count = payload.count if payload and payload.count else 3

    return _execute_build_recommend(
        learner_id=eff_id,
        degree_program=eff_degree,
        academic_domain=eff_domain,
        syllabus_subjects=eff_subjects,
        syllabus_topics=eff_topics,
        target_role=eff_role,
        count=eff_count,
    )

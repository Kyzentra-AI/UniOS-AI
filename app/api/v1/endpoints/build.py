"""
Sprint 5 — Universal Build Engine Endpoints (AI/ML-2)

Routes:
  POST /api/v1/kie/build/coach       — Contextual Build Coach
  GET  /api/v1/kie/build/recommend   — Project Recommendations

These are registered on the /kie/build prefix in api.py.
All routes are thin wrappers; business logic lives in BuildCoachService.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.build import (
    ArtifactType,
    BuildCoachRequest,
    BuildCoachResponse,
    BuildRecommendContext,
    BuildRecommendResponse,
)
from app.services.build_coach_service import get_build_coach_service
from app.services.llm_provider import LLMParseError, LLMProviderError

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /coach
# ---------------------------------------------------------------------------

@router.post(
    "/coach",
    response_model=BuildCoachResponse,
    status_code=status.HTTP_200_OK,
    summary="Contextual Build Coach (A2-S5-01)",
    description=(
        "Accepts learner context and active project state from Backend / AI/ML-1, "
        "then generates domain-adaptive, evidence-driven coaching blocks. "
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
def build_coach(request: BuildCoachRequest) -> BuildCoachResponse:
    """
    AI/ML-2 interface: Generates contextual build coaching intelligence.

    The caller (Backend or AI/ML-1) must supply:
    - request_id  for cross-service tracing
    - learner_id  as assigned by Backend
    - project_title + artifact_type + academic_domain

    Optional enrichment:
    - submitted_work_summary (plain text only — no binaries)
    - struggle_description
    - concept_mastery / weak_topics from Backend mastery records
    - rubric_criteria from Backend project definition
    """
    print(
        f"\n>>> [API /api/v1/kie/build/coach] "
        f"request_id={request.request_id} learner={request.learner_id} "
        f"artifact={request.artifact_type.value} domain={request.academic_domain or 'general'}"
    )

    service = get_build_coach_service()
    try:
        response = service.generate_coaching(request)
    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except LLMParseError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Build coaching response could not be parsed: {err.message}",
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error in build coach: {str(err)}",
        )

    print(
        f">>> [API /api/v1/kie/build/coach] "
        f"returned {len(response.coaching_blocks)} blocks, "
        f"tone={response.coaching_tone.value}, "
        f"remediation={response.remediation_recommended}"
    )
    return response


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
        "for a learner, driven by their mastery evidence, academic domain, and career goals. "
        "Learner context is supplied via query parameters from Backend / AI/ML-1. "
        "Backend is responsible for persisting any selected recommendation as a project record."
    ),
    responses={
        200: {"description": "Project recommendations returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
        500: {"description": "Internal error generating recommendations."},
    },
)
def build_recommend(
    learner_id: str = Query(..., min_length=1, description="Learner identifier from Backend."),
    request_id: str = Query(
        ..., min_length=1, description="Cross-service tracing identifier (required)."
    ),
    academic_domain: Optional[str] = Query(
        default=None,
        description="Academic domain: engineering, commerce, humanities, science, management, law.",
    ),
    learner_stage: Optional[str] = Query(
        default=None,
        description="Academic stage: bachelor, master, graduate.",
    ),
    target_role: Optional[str] = Query(
        default=None,
        description="Learner's target career role from Backend goals record.",
    ),
    count: int = Query(
        default=3,
        ge=1,
        le=5,
        description="Number of project recommendations to return (1–5).",
    ),
) -> BuildRecommendResponse:
    """
    AI/ML-2 interface: Returns domain-adaptive project recommendations.

    Context is deliberately kept thin for GET safety:
    - Mastery details that would exceed URL limits should be posted via
      the coach endpoint or passed through AI/ML-1 orchestration context.
    - Backend should supply request_id as a query parameter for tracing.
    """
    clean_id = learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    clean_req_id = request_id.strip()
    if not clean_req_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="request_id cannot be empty or whitespace.",
        )

    print(
        f"\n>>> [API /api/v1/kie/build/recommend] "
        f"request_id={clean_req_id} learner={clean_id} "
        f"domain={academic_domain or 'general'} count={count}"
    )

    # Enrich from memory engine (best-effort)
    weak_topics: Optional[list] = None
    completed_milestones: Optional[list] = None
    try:
        from app.services.memory_engine import get_memory_engine
        from app.schemas.memory_context import RelevantMemoryQuery

        engine = get_memory_engine()
        query = RelevantMemoryQuery(learner_id=clean_id, topic=target_role)
        mem_ctx = engine.retrieve_relevant_context(query)
        weak_topics = [f.topic for f in mem_ctx.relevant_friction if f.unresolved]
        completed_milestones = mem_ctx.active_goal.completed_milestones or []
    except Exception:
        pass

    context = BuildRecommendContext(
        learner_id=clean_id,
        academic_domain=academic_domain,
        learner_stage=learner_stage,
        target_role=target_role,
        completed_milestones=completed_milestones,
        current_weak_topics=weak_topics,
    )

    service = get_build_coach_service()
    try:
        response = service.generate_recommendations(context, request_id=clean_req_id, count=count)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(err)}",
        )

    print(
        f">>> [API /api/v1/kie/build/recommend] "
        f"returning {len(response.recommendations)} recommendations"
    )
    return response

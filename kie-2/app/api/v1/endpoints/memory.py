from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.schemas.memory import LearnerMemory
from app.schemas.memory_events import (
    MemoryUpdateEvent,
    MemoryUpdateResult,
    MemorySeedResult,
)
from app.schemas.intelligence import LearnerIntelligenceReport
from app.schemas.memory_context import (
    RelevantMemoryQuery,
    RelevantMemoryContext,
    RoadmapAdaptationContext,
)
from app.services import get_memory_engine

router = APIRouter()


class MemoryRetrieveRequest(BaseModel):
    """Request payload for retrieving learner memory container."""
    learner_id: str = Field(..., min_length=1, description="Target learner identifier")


class RoadmapContextRequest(BaseModel):
    """Request payload for retrieving roadmap adaptation intelligence."""
    learner_id: str = Field(..., min_length=1, description="Target learner identifier")
    current_topic: Optional[str] = Field(default=None, description="Current topic in progress if any")


@router.post(
    "/events",
    response_model=MemoryUpdateResult,
    status_code=status.HTTP_200_OK,
    summary="Record Learner Event & Update Memory",
    description=(
        "Ingests new learner activity/evidence (lesson completed, assessment score, friction signal, "
        "preference observed, goal change) and executes evidence-driven memory updates."
    ),
    responses={
        200: {"description": "Memory successfully updated with event evidence."},
        422: {"description": "Validation error: Malformed event payload."},
    },
)
@router.post(
    "/update",
    response_model=MemoryUpdateResult,
    status_code=status.HTTP_200_OK,
    summary="Record Learner Event & Update Memory (Alias)",
    description="Alias endpoint for ingesting learner events and updating memory.",
    responses={
        200: {"description": "Memory successfully updated."},
        422: {"description": "Validation error: Malformed event payload."},
    },
)
def record_memory_event(event: MemoryUpdateEvent) -> MemoryUpdateResult:
    """AI/ML-2 interface: Ingests learning event and updates memory intelligence."""
    print(f"\n>>> [API /api/v1/memory] Ingesting event '{event.event_type.value}' for learner '{event.learner_id}'")
    engine = get_memory_engine()
    try:
        result = engine.record_event(event)
        print(f">>> [API /api/v1/memory] Event processed: {result.summary}")
        return result
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing memory event: {str(err)}",
        )


@router.post(
    "/retrieve",
    response_model=LearnerMemory,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Learner Memory Intelligence",
    description="Retrieves the structured multi-facet memory container for a learner.",
    responses={
        200: {"description": "Structured learner memory container returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
    },
)
def retrieve_learner_memory(request: MemoryRetrieveRequest) -> LearnerMemory:
    """AI/ML-2 interface: Retrieves full structured memory for a learner."""
    engine = get_memory_engine()
    clean_id = request.learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    return engine.get_or_create_memory(clean_id)


@router.post(
    "/relevant-context",
    response_model=RelevantMemoryContext,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Relevant Memory Context for Learning Decision",
    description=(
        "Retrieves scoped learner memory (relevant preferences, friction, history, projects, and active goals) "
        "tailored for an upcoming learning unit or pedagogical decision without dumping entire raw history."
    ),
    responses={
        200: {"description": "Scoped relevant memory context returned."},
        422: {"description": "Validation error: Malformed query specification."},
    },
)
def retrieve_relevant_memory_context(query: RelevantMemoryQuery) -> RelevantMemoryContext:
    """AI/ML-2 interface: Provides scoped memory context for pedagogy or AI/ML-1 orchestration."""
    clean_id = query.learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    engine = get_memory_engine()
    try:
        return engine.retrieve_relevant_context(query)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error retrieving relevant memory context: {str(err)}",
        )


@router.post(
    "/roadmap-context",
    response_model=RoadmapAdaptationContext,
    status_code=status.HTTP_200_OK,
    summary="Generate Roadmap Adaptation Intelligence",
    description=(
        "Evaluates learner memory, topic mastery, and active friction to produce roadmap progression intelligence "
        "consumed by AI/ML-1 orchestration (e.g. insert remediation, accelerate, or adjust milestones)."
    ),
    responses={
        200: {"description": "Roadmap adaptation intelligence returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
    },
)
def get_roadmap_adaptation_context(request: RoadmapContextRequest) -> RoadmapAdaptationContext:
    """AI/ML-2 interface: Generates roadmap adaptation intelligence for AI/ML-1."""
    clean_id = request.learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    engine = get_memory_engine()
    try:
        return engine.generate_roadmap_context(clean_id, current_topic=request.current_topic)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error generating roadmap adaptation context: {str(err)}",
        )


@router.post(
    "/seed-from-onboarding",
    response_model=MemorySeedResult,
    status_code=status.HTTP_200_OK,
    summary="Seed Learner Memory from Onboarding Intelligence",
    description=(
        "Idempotently bridges Sprint-2 Onboarding intelligence into the Sprint-3 LearnerMemory container. "
        "Initializes career goals, cognitive preferences, pacing, format priorities, and metadata "
        "without overwriting existing learner history."
    ),
    responses={
        200: {"description": "Memory successfully seeded from onboarding report."},
        422: {"description": "Validation error: Malformed or invalid onboarding report."},
    },
)
@router.post(
    "/seed",
    response_model=MemorySeedResult,
    status_code=status.HTTP_200_OK,
    summary="Seed Learner Memory from Onboarding Intelligence (Alias)",
    description="Alias endpoint for seeding learner memory from onboarding intelligence.",
    responses={
        200: {"description": "Memory successfully seeded from onboarding report."},
        422: {"description": "Validation error: Malformed or invalid onboarding report."},
    },
)
def seed_memory_from_onboarding(report: LearnerIntelligenceReport) -> MemorySeedResult:
    """AI/ML-2 interface: Bridges onboarding intelligence into structured memory."""
    print(f"\n>>> [API /api/v1/memory] Seeding memory from onboarding report for '{report.learner_id}'")
    engine = get_memory_engine()
    try:
        result = engine.initialize_memory_from_onboarding(report)
        print(f">>> [API /api/v1/memory] Seeding complete: {result.summary}")
        return result
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error seeding memory from onboarding report: {str(err)}",
        )


@router.get(
    "/{learner_id}/relevant",
    response_model=RelevantMemoryContext,
    status_code=status.HTTP_200_OK,
    summary="Inspect Scoped Relevant Memory Context",
    description=(
        "Inspects scoped learner memory (relevant preferences, friction, history, projects, and active goals) "
        "tailored for a topic and objective, matching the context used in lesson planning."
    ),
    responses={
        200: {"description": "Scoped relevant memory context returned."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
    },
)
def get_relevant_memory_context(
    learner_id: str,
    topic: Optional[str] = Query(default=None, description="Topic of the upcoming learning activity"),
    objective: Optional[str] = Query(default=None, description="Learning objective"),
    target_role: Optional[str] = Query(default=None, description="Optional target career role"),
) -> RelevantMemoryContext:
    """AI/ML-2 interface: Read-only inspection of scoped relevant memory context."""
    clean_id = learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    engine = get_memory_engine()
    query = RelevantMemoryQuery(
        learner_id=clean_id,
        topic=topic,
        objective=objective,
        target_role=target_role,
    )
    try:
        return engine.retrieve_relevant_context(query)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error retrieving relevant memory context: {str(err)}",
        )


@router.get(
    "/{learner_id}",
    response_model=LearnerMemory,
    status_code=status.HTTP_200_OK,
    summary="Inspect Complete Learner Memory Container",
    description=(
        "Read-only inspection of the learner's complete 7-dimension memory container "
        "for debugging and verification by Backend and AI/ML-1 orchestration."
    ),
    responses={
        200: {"description": "Complete learner memory container returned."},
        404: {"description": "Learner memory not found."},
        422: {"description": "Validation error: Missing or invalid learner_id."},
    },
)
def get_learner_memory(learner_id: str) -> LearnerMemory:
    """AI/ML-2 interface: Read-only retrieval of the complete learner memory container."""
    clean_id = learner_id.strip()
    if not clean_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="learner_id cannot be empty or whitespace.",
        )
    engine = get_memory_engine()
    memory = engine.get_memory(clean_id)
    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner memory not found for '{clean_id}'.",
        )
    return memory

import logging
from fastapi import APIRouter, BackgroundTasks, status
from app.schemas.context_v2 import (
    AnalyzeContextRequest,
    AnalyzeContextResponse,
    ResolveContextRequest,
    ResolveContextResponse,
)
from app.services.context_service import get_context_service

logger = logging.getLogger(__name__)

router = APIRouter()


def _async_process_and_send_questions(request_dict: dict) -> None:
    try:
        user_id = request_dict.get("user_id") or request_dict.get("learner_id") or "unknown"
        service = get_context_service()
        questions = service.generate_questions(request_dict)
        service.post_questions_webhook(user_id=user_id, questions=questions)
    except Exception as e:
        logger.error(f"[ContextEndpoint] Async question processing error: {e}", exc_info=True)


def _async_process_and_send_resolved(request_dict: dict) -> None:
    try:
        user_id = request_dict.get("user_id") or request_dict.get("learner_id") or "unknown"
        service = get_context_service()
        new_context = service.resolve_answers(request_dict.get("answers", []))
        service.post_resolved_webhook(user_id=user_id, new_context=new_context)
    except Exception as e:
        logger.error(f"[ContextEndpoint] Async context resolution error: {e}", exc_info=True)


@router.post(
    "/analyze",
    response_model=AnalyzeContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Onboarding Context (Fire-and-Forget)",
    description=(
        "Endpoint 1: Acknowledges immediately with 200 OK within 10s SLA, then generates "
        "2-5 clarifying questions asynchronously and posts them to Backend Webhook W1."
    ),
)
def analyze_context(
    request: AnalyzeContextRequest,
    background_tasks: BackgroundTasks,
) -> AnalyzeContextResponse:
    user_id = request.user_id or request.learner_id or "unknown"
    logger.info(f"[API POST /api/v1/kie/context/analyze] Received context analysis for user '{user_id}'")

    # Enqueue background work to generate questions and fire webhook
    background_tasks.add_task(_async_process_and_send_questions, request.model_dump())

    return AnalyzeContextResponse(status="processing", questions=[])


@router.post(
    "/resolve",
    response_model=ResolveContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Onboarding Context (Fire-and-Forget)",
    description=(
        "Endpoint 2: Acknowledges immediately with 200 OK within 10s SLA, then maps learner answers "
        "to structured context (primary_languages, experience_level, etc.) and posts to Backend Webhook W2."
    ),
)
def resolve_context(
    request: ResolveContextRequest,
    background_tasks: BackgroundTasks,
) -> ResolveContextResponse:
    user_id = request.user_id or request.learner_id or "unknown"
    logger.info(f"[API POST /api/v1/kie/context/resolve] Received context answers for user '{user_id}' ({len(request.answers)} answers)")

    # Enqueue background work to resolve answers and fire webhook
    background_tasks.add_task(_async_process_and_send_resolved, request.model_dump())

    return ResolveContextResponse(status="ok", new_context={})


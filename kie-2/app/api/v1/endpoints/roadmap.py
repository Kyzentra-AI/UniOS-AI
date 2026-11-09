import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.context_v2 import AnalyzeContextRequest
from app.schemas.roadmap import AIMLRoadmapResponse
from app.services.roadmap_service import get_roadmap_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate",
    response_model=AIMLRoadmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Academic & Career Roadmap (Synchronous)",
    description=(
        "Endpoint 4: Generates a full structured roadmap with semesters, career milestones, "
        "and sequential weekly missions. Validated strictly by Backend against AIMLRoadmapResponse."
    ),
    responses={
        200: {"description": "Roadmap and missions generated successfully."},
        422: {"description": "Validation error: Malformed ContextV2 payload."},
        500: {"description": "Internal server error during roadmap generation."},
    },
)
def generate_roadmap(request: AnalyzeContextRequest) -> AIMLRoadmapResponse:
    learner_id = request.learner_id or request.user_id or "unknown"
    scope = request.scope or "ACADEMIC"
    logger.info(f"[API POST /api/v1/kie/roadmap/generate] Generating roadmap for learner '{learner_id}', scope={scope}")

    service = get_roadmap_service()
    try:
        response = service.generate(request)
        logger.info(
            f"[API POST /api/v1/kie/roadmap/generate] Generated {len(response.missions)} missions, "
            f"{len(response.semesters)} semesters for learner '{learner_id}'"
        )
        return response
    except Exception as e:
        logger.error(f"[API POST /api/v1/kie/roadmap/generate] Failed to generate roadmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}",
        )


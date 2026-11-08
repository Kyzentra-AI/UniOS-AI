import logging
from typing import Any, Dict
from fastapi import APIRouter, status
from app.schemas.memory_summary import MemorySummaryRequest
from app.services.memory_summary_service import get_memory_summary_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/summary",
    status_code=status.HTTP_200_OK,
    summary="Generate Learner Memory Summary (Synchronous)",
    description=(
        "Endpoint 5: Called by ContextV2Assembler.assemble() to produce an opaque pedagogical "
        "summary of recent events (mastered concepts, struggles, pacing recommendation)."
    ),
)
def get_memory_summary(request: MemorySummaryRequest) -> Dict[str, Any]:
    logger.info(f"[API POST /api/v1/kie/memory/summary] Summarizing {len(request.events)} events")
    service = get_memory_summary_service()
    return service.summarize(request.events)


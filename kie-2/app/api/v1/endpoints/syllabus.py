import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.syllabus import SyllabusExtractRequest, SyllabusExtractResponse
from app.services.syllabus_extract_service import get_syllabus_extract_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/extract",
    response_model=SyllabusExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Syllabus Curriculum Structure (Synchronous)",
    description=(
        "Endpoint 3: Synchronous extraction of subjects and topics from raw PDF text. "
        "Strictly validated by Backend ParsedContent schema. Guaranteed to return a non-empty list of subjects."
    ),
    responses={
        200: {"description": "Structured subjects and topics parsed successfully."},
        422: {"description": "Validation error: Malformed syllabus request payload."},
        500: {"description": "Internal server error extracting syllabus content."},
    },
)
def extract_syllabus(request: SyllabusExtractRequest) -> SyllabusExtractResponse:
    logger.info(f"[API POST /api/v1/kie/syllabus/extract] Extracting syllabus '{request.syllabus_id}' ({len(request.text)} chars)")
    service = get_syllabus_extract_service()
    try:
        response = service.extract(request.syllabus_id, request.text)
        logger.info(f"[API POST /api/v1/kie/syllabus/extract] Extracted {len(response.subjects)} subjects")
        return response
    except Exception as e:
        logger.error(f"[API POST /api/v1/kie/syllabus/extract] Failed to extract syllabus: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract syllabus: {str(e)}",
        )


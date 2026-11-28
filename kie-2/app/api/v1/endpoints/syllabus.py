import logging
import uuid
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.syllabus import SyllabusExtractRequest, SyllabusExtractResponse
from app.services.pdf_extract_service import get_pdf_extract_service
from app.services.syllabus_extract_service import get_syllabus_extract_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/extract",
    status_code=status.HTTP_200_OK,
    summary="Syllabus Extraction Route Guidance",
)
@router.get(
    "/extract-file",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def get_syllabus_route_info():
    """Operational status and contract guidance for Backend syllabus extraction integration."""
    return {
        "status": "ready",
        "service": "UniOS Syllabus Intelligence Engine (Endpoint 3)",
        "endpoints": {
            "json_payload": {
                "url": "/api/v1/kie/syllabus/extract",
                "method": "POST",
                "content_type": "application/json",
                "description": "Send extracted text, base64 PDF/image, or pre-signed download URL.",
                "sample_payload": {
                    "syllabus_id": "syl_12345",
                    "text": "Unit 1: Data Structures\nArrays, Linked Lists\nUnit 2: Algorithms\nSorting, Searching",
                    "file_base64": "<optional base64 string for scanned PDFs>",
                    "file_url": "<optional s3/public download url>",
                },
            },
            "multipart_file_upload": {
                "url": "/api/v1/kie/syllabus/extract-file",
                "method": "POST",
                "content_type": "multipart/form-data",
                "description": "Upload PDF or image directly. Performs pypdf extraction or OCR automatically.",
                "form_fields": {
                    "file": "<Binary PDF or Image file (.pdf, .png, .jpg, .jpeg)> (Required)",
                    "syllabus_id": "<string identifier> (Optional)",
                },
            },
        },
        "response_contract": {
            "subjects": [
                {
                    "name": "Data Structures & Algorithms",
                    "topics": ["Arrays & Linked Lists", "Sorting & Searching"],
                }
            ]
        },
    }


@router.post(
    "/extract",
    response_model=SyllabusExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Syllabus Curriculum Structure (JSON / Text / Base64 / URL)",
    description=(
        "Endpoint 3 (JSON Mode): Synchronous extraction of subjects and topics. "
        "Supports raw extracted text, Base64-encoded PDF/image, or remote download URL. "
        "Strictly validated by Backend ParsedContent schema."
    ),
    responses={
        200: {"description": "Structured subjects and topics parsed successfully."},
        422: {"description": "Validation error: Malformed syllabus request payload."},
        500: {"description": "Internal server error extracting syllabus content."},
    },
)
def extract_syllabus(request: SyllabusExtractRequest) -> SyllabusExtractResponse:
    """Extracts curriculum from text, base64 PDF, or file URL."""
    syllabus_service = get_syllabus_extract_service()
    pdf_service = get_pdf_extract_service()

    # 1. Direct text provided by backend
    if request.text and request.text.strip():
        logger.info(f"[API POST /api/v1/kie/syllabus/extract] Processing text payload for '{request.syllabus_id}' ({len(request.text)} chars)")
        raw_text = request.text.strip()

    # 2. Base64-encoded PDF or image provided
    elif request.file_base64 or request.pdf_base64:
        b64_data = request.file_base64 or request.pdf_base64
        logger.info(f"[API POST /api/v1/kie/syllabus/extract] Processing Base64 PDF/image for '{request.syllabus_id}' ({len(b64_data)} chars)")
        raw_text = pdf_service.extract_text_from_base64(b64_data, filename=request.filename)

    # 3. Public or pre-signed URL provided
    elif request.file_url or request.pdf_url:
        doc_url = request.file_url or request.pdf_url
        logger.info(f"[API POST /api/v1/kie/syllabus/extract] Downloading document from URL for '{request.syllabus_id}': {doc_url[:80]}...")
        raw_text = pdf_service.extract_from_url(doc_url, filename=request.filename)

    else:
        logger.warning(f"[API POST /api/v1/kie/syllabus/extract] No text, base64, or url provided for '{request.syllabus_id}'; applying fallback.")
        raw_text = request.filename or "General Academic Curriculum"

    try:
        response = syllabus_service.extract(request.syllabus_id, raw_text)
        logger.info(f"[API POST /api/v1/kie/syllabus/extract] Extracted {len(response.subjects)} subjects for '{request.syllabus_id}'")
        return response
    except Exception as e:
        logger.error(f"[API POST /api/v1/kie/syllabus/extract] Failed to extract syllabus: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract syllabus: {str(e)}",
        )


@router.post(
    "/extract-file",
    response_model=SyllabusExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Syllabus from PDF or Image File (Multipart Form-Data with OCR)",
    description=(
        "Endpoint 3 (File Upload Mode): Upload a PDF document or image file directly. "
        "Extracts digital text using pypdf or runs OCR on scanned/image-based pages via pytesseract. "
        "Always returns structured subjects and topics matching the Backend ParsedContent contract."
    ),
    responses={
        200: {"description": "Structured subjects and topics parsed successfully from file."},
        400: {"description": "Invalid file format or empty document."},
        500: {"description": "Internal server error extracting syllabus file."},
    },
)
@router.post(
    "/upload",
    response_model=SyllabusExtractResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@router.post(
    "/extract/upload",
    response_model=SyllabusExtractResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def extract_syllabus_from_file(
    file: UploadFile = File(..., description="PDF document or image file (.pdf, .png, .jpg, .jpeg)"),
    syllabus_id: Optional[str] = Form(None, description="Optional syllabus ID (defaults to filename or auto-generated UUID)"),
) -> SyllabusExtractResponse:
    """Accepts direct multipart PDF/image upload, runs text/OCR extraction, and parses curriculum."""
    clean_id = (syllabus_id or "").strip() or f"syl_{uuid.uuid4().hex[:8]}"
    filename = file.filename or "syllabus.pdf"
    content_type = file.content_type or ""

    logger.info(f"[API POST /api/v1/kie/syllabus/extract-file] Received file upload '{filename}' ({content_type}) for syllabus '{clean_id}'")

    try:
        file_bytes = await file.read()
    except Exception as read_err:
        logger.error(f"[API POST /api/v1/kie/syllabus/extract-file] Failed to read uploaded file: {read_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(read_err)}",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    try:
        syllabus_service = get_syllabus_extract_service()
        response = syllabus_service.extract_from_bytes(
            syllabus_id=clean_id,
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
        )
        logger.info(f"[API POST /api/v1/kie/syllabus/extract-file] Extracted {len(response.subjects)} subjects from file '{filename}'")
        return response
    except Exception as err:
        logger.error(f"[API POST /api/v1/kie/syllabus/extract-file] Error extracting syllabus from file: {err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract syllabus from file: {str(err)}",
        )

"""
UniOS — Mentor Chat Endpoints (AI/ML KIE)
Endpoints:
  - POST /api/v1/kie/mentor/chat (Persona-Driven Interactive AI Mentor)
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.mentor_service import get_mentor_service

router = APIRouter()


@router.get(
    "/chat",
    status_code=status.HTTP_200_OK,
    summary="Mentor Chat Route Info (GET /api/v1/kie/mentor/chat)",
    description="Operational status and schema guidance for mentor chat.",
)
def get_mentor_chat_info():
    return {
        "status": "ready",
        "service": "UniOS Interactive AI Mentor (AI/ML KIE)",
        "endpoint": "/api/v1/kie/mentor/chat",
        "method": "POST",
        "supported_methods": ["POST", "GET"],
        "supported_modes": ["tutor", "study-coach", "accountability", "motivation"],
        "description": "Send POST request with learner_id, mode, message, context, and history to receive persona-driven pedagogical guidance.",
        "sample_payload": {
            "learner_id": "00000000-0000-0000-0000-000000000002",
            "mode": "tutor",
            "message": "Explain DBMS in simple words",
            "context": {
                "topic": "DBMS Fundamentals",
                "lesson_id": "lesson-123",
                "roadmap_id": "roadmap-123",
                "mission_id": "mission-123",
            },
            "history": [
                {"role": "user", "content": "What is a database?"},
                {"role": "mentor", "content": "A database is an organized collection of data."},
            ],
        },
    }


@router.post(
    "/chat",
    response_model=MentorChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Mentor Persona Chat (POST /api/v1/kie/mentor/chat)",
    description=(
        "Handles conversational turns across 4 distinct persona modes: tutor, study-coach, "
        "accountability, and motivation. Returns concise, structured markdown within SLA."
    ),
    responses={
        200: {"description": "Mentor reply successfully generated."},
        422: {"description": "Validation error: Missing or malformed parameters."},
        500: {"description": "Internal server error during chat synthesis."},
    },
)
def mentor_chat_endpoint(request: MentorChatRequest) -> MentorChatResponse:
    print(f"\n>>> [API POST /api/v1/kie/mentor/chat] Received Mentor Chat Request:")
    print(f"    - Learner:  {request.learner_id}")
    print(f"    - Mode:     {request.mode}")
    print(f"    - Message:  {request.message[:60]}...")
    if request.context:
        print(f"    - Context:  {request.context}")

    service = get_mentor_service()
    try:
        response = service.chat(request)
        print(f">>> [API POST /api/v1/kie/mentor/chat] Reply length: {len(response.reply)} chars.")
        return response
    except Exception as e:
        print(f">>> [API POST /api/v1/kie/mentor/chat] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate mentor chat response: {str(e)}",
        )

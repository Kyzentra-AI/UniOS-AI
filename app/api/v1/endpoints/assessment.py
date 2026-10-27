"""
UniOS — Assessment & Mastery Intelligence Endpoints
Endpoints:
  - POST /api/v1/kie/assessments/generate (Dynamic Question Synthesis with Private Answer Keys/Rubrics)
  - POST /api/v1/kie/mastery/evaluate    (Attempt Evaluation & Hierarchical Mastery Graph Delta)
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    MasteryEvaluateRequest,
    MasteryEvaluateResponse,
)
from app.services.assessment_service import get_assessment_service

assessment_router = APIRouter()
mastery_router = APIRouter()


@assessment_router.get(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Assessment Route Info (GET /api/v1/kie/assessments/generate)",
    description="Operational status and schema guidance for assessment generation.",
)
def get_assessment_generate_info():
    return {
        "status": "ready",
        "service": "UniOS Assessment Generation Engine (AI/ML KIE)",
        "endpoint": "/api/v1/kie/assessments/generate",
        "method": "POST",
        "supported_methods": ["POST", "GET"],
        "description": "Send POST request with topic and options to synthesize questions with private answer keys.",
        "sample_payload": {
            "learner_id": "00000000-0000-0000-0000-000000000002",
            "session_id": "session-123",
            "lesson_id": "lesson-456",
            "topic": "DBMS Fundamentals",
            "preferred_type": "mcq",
            "question_count": 5,
            "difficulty": "PROFICIENT",
        },
    }


@assessment_router.post(
    "/generate",
    response_model=AssessmentGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Synthesize Assessment (POST /api/v1/kie/assessments/generate)",
    description=(
        "Synthesizes questions tailored to topic, preferred type, and difficulty. "
        "Returns questions along with private answer keys (for MCQs) and rubrics (for coding/subjective)."
    ),
    responses={
        200: {"description": "Assessment generated successfully with answer keys."},
        422: {"description": "Validation error: Invalid request parameters."},
        500: {"description": "Internal server error during assessment generation."},
    },
)
def generate_assessment_endpoint(
    request: AssessmentGenerateRequest,
) -> AssessmentGenerateResponse:
    print(f"\n>>> [API POST /api/v1/kie/assessments/generate] Received Assessment Request:")
    print(f"    - Learner:    {request.learner_id}")
    print(f"    - Topic:      {request.topic}")
    print(f"    - Type:       {request.preferred_type}")
    print(f"    - Count:      {request.question_count}")
    print(f"    - Difficulty: {request.difficulty}")

    service = get_assessment_service()
    try:
        response = service.generate_assessment(request)
        print(f">>> [API POST /api/v1/kie/assessments/generate] Returning {len(response.questions)} questions.")
        return response
    except Exception as e:
        print(f">>> [API POST /api/v1/kie/assessments/generate] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate assessment: {str(e)}",
        )


@mastery_router.get(
    "/evaluate",
    status_code=status.HTTP_200_OK,
    summary="Mastery Evaluate Route Info (GET /api/v1/kie/mastery/evaluate)",
    description="Operational status and schema guidance for mastery attempt evaluation.",
)
def get_mastery_evaluate_info():
    return {
        "status": "ready",
        "service": "UniOS Mastery Evaluation Engine (AI/ML KIE)",
        "endpoint": "/api/v1/kie/mastery/evaluate",
        "method": "POST",
        "supported_methods": ["POST", "GET"],
        "description": "Send POST request with submitted answers to evaluate attempt and compute mastery delta.",
        "sample_payload": {
            "learner_id": "00000000-0000-0000-0000-000000000002",
            "assessment_id": "assessment-123",
            "topic": "DBMS Fundamentals",
            "total_time_spent_seconds": 95,
            "answers": [
                {
                    "question_id": "q1",
                    "answer": "opt-1",
                    "hints_used": 0,
                    "time_spent_seconds": 30,
                }
            ],
        },
    }


@mastery_router.post(
    "/evaluate",
    response_model=MasteryEvaluateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Assessment Attempt & Update Mastery (POST /api/v1/kie/mastery/evaluate)",
    description=(
        "Evaluates submitted assessment answers, computes normalized total score (0.0 to 1.0), "
        "provides per-question evaluations, and outputs hierarchical mastery graph updates."
    ),
    responses={
        200: {"description": "Attempt evaluated successfully with mastery updates."},
        422: {"description": "Validation error: Malformed attempt payload."},
        500: {"description": "Internal server error during attempt evaluation."},
    },
)
def evaluate_mastery_endpoint(
    request: MasteryEvaluateRequest,
) -> MasteryEvaluateResponse:
    print(f"\n>>> [API POST /api/v1/kie/mastery/evaluate] Received Mastery Evaluation Request:")
    print(f"    - Learner:        {request.learner_id}")
    print(f"    - Assessment ID:  {request.assessment_id}")
    print(f"    - Topic:          {request.topic}")
    print(f"    - Answer Count:   {len(request.answers)}")
    print(f"    - Time Spent:     {request.total_time_spent_seconds}s")

    service = get_assessment_service()
    try:
        response = service.evaluate_mastery(request)
        print(f">>> [API POST /api/v1/kie/mastery/evaluate] Score: {response.score:.2f}, Feedback: {response.feedback[:60]}...")
        return response
    except Exception as e:
        print(f">>> [API POST /api/v1/kie/mastery/evaluate] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate mastery: {str(e)}",
        )

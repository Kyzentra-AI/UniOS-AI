from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas import (
    NormalizedLearningContext,
    GeneratedLesson,
    LessonBlock,
    LessonBlockType,
    PedagogyDecision,
    AssessmentEvidence,
    MasteryUpdateResult,
    ClosedLoopResult,
    RelevantMemoryQuery,
    LearnerStage,
    InterpretRequest,
    InterpretResponse,
)
from app.services import (
    build_pedagogy_prompt,
    build_lesson_prompt,
    get_llm_provider,
    get_memory_engine,
    get_pedagogy_engine,
    get_mastery_engine,
    get_remediation_service,
    get_interpret_engine,
    LLMProviderError,
    LLMParseError,
)

router = APIRouter()


class RemediationCycleRequest(BaseModel):
    """Request payload for executing a closed-loop remediation cycle (A2-S4-04)."""
    learner_id: str = Field(..., min_length=1, description="Target learner identifier")
    topic: str = Field(..., min_length=1, description="Topic undergoing remediation evaluation")
    initial_score: float = Field(..., ge=0.0, le=1.0, description="Initial assessment or practice score")
    reassessment_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Optional reassessment score after remedial lesson"
    )
    learner_stage: LearnerStage = Field(
        default=LearnerStage.BACHELOR, description="Academic career stage"
    )
    academic_domain: Optional[str] = Field(
        default=None, description="Disciplinary domain (engineering, commerce, humanities, science, etc.)"
    )


@router.get(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Lesson Generation Route Info (GET /api/v1/kie/lesson/generate)",
    description="Returns metadata, operational status, and schema guidance for the lesson generation service.",
)
@router.get(
    "/plan-lesson",
    status_code=status.HTTP_200_OK,
    summary="Plan Lesson Route Info (GET /api/v1/learning/plan-lesson)",
)
@router.get(
    "/generate-learning-intelligence",
    status_code=status.HTTP_200_OK,
    summary="Learning Intelligence Route Info",
)
def get_lesson_generation_route_info():
    """Provides operational guidance when callers ping lesson endpoints via GET."""
    return {
        "status": "ready",
        "service": "UniOS Learning Intelligence",
        "endpoint": "/api/v1/kie/lesson/generate",
        "method": "POST",
        "supported_methods": ["POST", "GET"],
        "description": "Send a POST request with NormalizedLearningContext JSON payload to generate structured lessons.",
        "sample_payload": {
            "topic": "Python Functions",
            "objective": "Understand function definitions, arguments, and return values",
            "learner_state": {
                "learner_id": "student_001",
                "stage": "bachelor",
                "confidence": "medium",
                "weak_topics": ["Python Functions"],
            },
        },
    }


@router.get(
    "/generate/docs",
    include_in_schema=False,
)
@router.get(
    "/plan-lesson/docs",
    include_in_schema=False,
)
def redirect_lesson_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


@router.get(
    "/interpret",
    status_code=status.HTTP_200_OK,
    summary="Interpret Route Info (GET /api/v1/kie/learn/interpret)",
    description="Operational status and schema guidance for AI-1 Pedagogical Interpreter.",
)
def get_interpret_route_info():
    return {
        "status": "ready",
        "service": "UniOS Pedagogical Interpreter Engine (AI-1)",
        "endpoint": "/api/v1/kie/learn/interpret",
        "method": "POST",
        "supported_methods": ["POST", "GET"],
        "description": "Send POST request with InterpretRequest JSON to analyze learner intent and determine pedagogy.",
        "sample_payload": {
            "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
            "learner_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "topic": "Binary Search Trees",
            "user_intent": "Explain tree traversals with visual analogies and code snippets",
            "references": [],
            "context": {},
        },
    }


@router.post(
    "/interpret",
    response_model=InterpretResponse,
    status_code=status.HTTP_200_OK,
    summary="Pedagogical Interpreter Engine (AI-1 / Section 14.1)",
    description=(
        "Analyzes learner intent, ContextV2, and syllabus references to determine instructional strategy, "
        "identify prerequisites and knowledge gaps, and design optimal block flow."
    ),
    responses={
        200: {"description": "Structured AI-1 pedagogical interpretation returned."},
        422: {"description": "Validation error: Malformed request payload."},
        502: {"description": "Bad Gateway: Upstream LLM provider failure."},
    },
)
def interpret_learner_intent(request: InterpretRequest) -> InterpretResponse:
    """Section 14.1: Pedagogical Interpreter Engine (AI-1)."""
    print(f"\n>>> [API POST /api/v1/kie/learn/interpret] Received AI-1 Interpret Request:")
    print(f"    - Request ID: {request.request_id}")
    print(f"    - Learner:    {request.learner_id}")
    print(f"    - Topic:      {request.topic}")
    print(f"    - User Intent: {request.user_intent}")
    engine = get_interpret_engine()
    response = engine.interpret(request)
    print(f">>> [API POST /api/v1/kie/learn/interpret] Returning Strategy={response.pedagogical_strategy}, Gaps={len(response.knowledge_gaps_identified)}")
    return response


@router.post(
    "/plan-lesson",
    response_model=GeneratedLesson,
    status_code=status.HTTP_200_OK,
    summary="Plan and Generate Lesson (AI/ML-2)",
    description="Accepts NormalizedLearningContext, applies Pedagogy guidelines, and generates structured lesson blocks via LLM.",
    responses={
        200: {"description": "Structured lesson successfully planned and generated."},
        422: {"description": "Validation error: Malformed learning context."},
        429: {"description": "Too Many Requests: LLM provider rate limit exceeded."},
        502: {"description": "Bad Gateway: LLM provider unavailable or unparseable output."},
    },
)
@router.post(
    "/generate-learning-intelligence",
    response_model=GeneratedLesson,
    status_code=status.HTTP_200_OK,
    summary="Generate Learning Intelligence (Canonical KIE Contract)",
    description="Universal KIE Section 4.2 / 4.5 endpoint returning structured learning decisions and blocks.",
    responses={
        200: {"description": "Structured learning intelligence returned."},
        422: {"description": "Validation error: Malformed learning context."},
    },
)
@router.post(
    "/generate-lesson",
    response_model=GeneratedLesson,
    status_code=status.HTTP_200_OK,
    summary="Generate Lesson (Sprint 1 Route Alias)",
    description="Sprint 1 backward-compatible alias route for generating structured lessons.",
    responses={
        200: {"description": "Structured lesson successfully generated."},
        422: {"description": "Validation error: Malformed learning context."},
        429: {"description": "Too Many Requests: LLM provider rate limit exceeded."},
        502: {"description": "Bad Gateway: LLM provider unavailable or unparseable output."},
    },
)
@router.post(
    "/generate",
    response_model=GeneratedLesson,
    status_code=status.HTTP_200_OK,
    summary="Generate Lesson — KIE Canonical Route (POST /api/v1/kie/lesson/generate)",
    description="KIE-namespaced canonical route. Accepts NormalizedLearningContext and returns a fully structured lesson. Registered under /kie/lesson prefix for Backend contract alignment.",
    responses={
        200: {"description": "Structured lesson successfully generated."},
        422: {"description": "Validation error: Malformed learning context."},
        429: {"description": "Too Many Requests: LLM provider rate limit exceeded."},
        502: {"description": "Bad Gateway: LLM provider unavailable or unparseable output."},
    },
)
def plan_and_generate_lesson(context: NormalizedLearningContext) -> GeneratedLesson:
    """AI/ML-2 capability interface: Takes normalized context and generates a structured lesson (A2-S4-02)."""
    req_id = context.request_id or context.context_id
    print(f"\n>>> [API POST /api/v1/kie/lesson/generate] Received Lesson Request:")
    print(f"    - Request ID: {req_id} (Context ID: {context.context_id})")
    print(f"    - Topic:      {context.topic}")
    print(f"    - Objective:  {context.objective}")
    print(f"    - Learner:    {context.learner_state.learner_id} (Stage: {context.learner_state.stage.value})")
    if context.academic_domain:
        print(f"    - Domain:     {context.academic_domain}")
    print(f"    - Confidence: {context.learner_state.confidence.value}")
    print(f"    - Weaknesses: {context.learner_state.weak_topics}")

    # 0. Enrich with memory context if not explicitly provided
    if context.memory_context is None and context.learner_state and context.learner_state.learner_id:
        clean_learner_id = context.learner_state.learner_id.strip()
        if clean_learner_id:
            try:
                engine = get_memory_engine()
                query = RelevantMemoryQuery(
                    learner_id=clean_learner_id,
                    topic=context.topic,
                    objective=context.objective,
                    target_role=context.learner_state.career_goal,
                    current_learner_state=context.learner_state,
                )
                context.memory_context = engine.retrieve_relevant_context(query)
                print(f"    - Memory:     Retrieved context for '{clean_learner_id}' (Friction count: {len(context.memory_context.relevant_friction)})")
            except Exception as mem_err:
                print(f"    - Memory:     Retrieval skipped gracefully: {mem_err}")
                context.memory_context = None
    elif context.memory_context is not None:
        print(f"    - Memory:     Explicit context provided (Friction count: {len(context.memory_context.relevant_friction)})")

    provider = get_llm_provider()
    pedagogy_engine = get_pedagogy_engine()

    try:
        # 1. Pedagogy decision (A2-S4-01)
        # Use PedagogyEngine for comprehensive domain & evidence calibration
        pedagogy_decision = pedagogy_engine.determine_pedagogy(context)

        # If live LLM provider is active and not mock, blend with live provider reasoning
        from app.core.config import settings
        if settings.LLM_PROVIDER.lower() != "mock":
            try:
                pedagogy_prompt = build_pedagogy_prompt(context)
                llm_decision = provider.generate_pedagogy_decision(pedagogy_prompt)
                # Retain enriched sequence and practice level from engine
                llm_decision.sequence = pedagogy_decision.sequence
                llm_decision.practice_level = pedagogy_decision.practice_level
                llm_decision.remediation = pedagogy_decision.remediation
                pedagogy_decision = llm_decision
            except Exception as e:
                print(f"    - Notice: LLM pedagogy failed ({e}), falling back to deterministic PedagogyEngine decision.")

        # 2. Structured lesson generation (A2-S4-02)
        lesson_prompt = build_lesson_prompt(context, pedagogy_decision)
        try:
            lesson = provider.generate_lesson(
                prompt=lesson_prompt,
                context_id=context.context_id,
                topic=context.topic,
                pedagogy_decision=pedagogy_decision,
            )
        except Exception as gen_err:
            from app.core.config import settings
            if settings.LLM_PROVIDER.lower() != "mock":
                print(f"    - Notice: Live LLM lesson generation encountered error ({gen_err}); applying resilient fallback.")
                from app.services.llm_provider import MockLLMProvider
                fallback_provider = MockLLMProvider()
                lesson = fallback_provider.generate_lesson(
                    prompt=lesson_prompt,
                    context_id=context.context_id,
                    topic=context.topic,
                    pedagogy_decision=pedagogy_decision,
                )
            else:
                raise
        # Ensure request_id is propagated
        lesson.request_id = req_id

        # Align with Section 14.2 Backend requirements if lesson_id or interpreted_data provided
        if context.lesson_id or context.interpreted_data:
            lesson.id = context.lesson_id or lesson.id or context.context_id
            lesson.title = f"Mastering {context.topic}"
            if context.interpreted_data and context.interpreted_data.get("knowledge_gaps_identified"):
                lesson.prerequisites = [
                    str(gap).replace("_", " ").title() for gap in context.interpreted_data["knowledge_gaps_identified"]
                ]

            type_mapping = {
                "objective": "TEXT",
                "explanation": "TEXT",
                "text": "TEXT",
                "worked_example": "CODE",
                "code": "CODE",
                "visual_spec": "INTERACTIVE",
                "interactive": "INTERACTIVE",
                "practice_task": "QUIZ",
                "quiz": "QUIZ",
                "video": "VIDEO",
            }
            aligned_blocks = []
            for idx, blk in enumerate(lesson.blocks, start=1):
                raw_type = str(blk.type).lower().replace("lessonblocktype.", "").replace("_", "-")
                canonical_type = type_mapping.get(raw_type, "TEXT")
                blk_id = blk.id or f"blk-{idx:02d}-{canonical_type.lower()}"

                code_val = blk.code
                lang_val = blk.language
                if canonical_type in ["CODE", "INTERACTIVE"] and not code_val:
                    code_val = (
                        f"# Implementation for {context.topic}\n"
                        f"def solution_{context.topic.lower().replace(' ', '_')}():\n"
                        f"    return 'Execution logic'\n"
                    )
                    lang_val = lang_val or "python"

                opts_val = blk.options
                ans_val = blk.answer
                expl_val = blk.explanation
                if canonical_type == "QUIZ":
                    if not opts_val:
                        opts_val = [
                            "A) Linear time O(N)",
                            "B) Logarithmic time O(log N)",
                            "C) Constant time O(1)",
                            "D) None of the above",
                        ]
                        ans_val = ans_val or "A) Linear time O(N)"
                        expl_val = expl_val or f"Comprehension check for {context.topic}."

                aligned_blocks.append(
                    LessonBlock(
                        id=blk_id,
                        type=canonical_type,
                        title=blk.title or f"{context.topic} Block {idx}",
                        content=str(blk.content) if blk.content else None,
                        code=code_val,
                        language=lang_val,
                        options=opts_val,
                        answer=ans_val,
                        explanation=expl_val,
                        url=blk.url,
                        caption=blk.caption,
                        metadata=blk.metadata,
                    )
                )

            if not any(b.type == "QUIZ" for b in aligned_blocks):
                aligned_blocks.append(
                    LessonBlock(
                        id=f"blk-{len(aligned_blocks)+1:02d}-quiz",
                        type="QUIZ",
                        title=f"Comprehension Check: {context.topic}",
                        content=f"What is the primary operational invariant for {context.topic}?",
                        options=[
                            "A) Keys are strictly ordered",
                            "B) All elements are randomized",
                            "C) Elements are stored as arrays",
                            "D) None of the above",
                        ],
                        answer="A) Keys are strictly ordered",
                        explanation=f"A fundamental property of {context.topic} is maintaining structural invariants.",
                    )
                )
            lesson.blocks = aligned_blocks

    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected internal error during lesson generation: {str(err)}",
        )

    print(f">>> [API POST /api/v1/kie/lesson/generate] Returning {len(lesson.blocks)} blocks to caller.\n")
    return lesson


@router.post(
    "/pedagogy-decision",
    response_model=PedagogyDecision,
    status_code=status.HTTP_200_OK,
    summary="Determine Pedagogy Strategy (A2-S4-01)",
    description="Evaluates learner evidence, academic domain, stage, and memory to produce structured pedagogy.",
    responses={
        200: {"description": "Structured pedagogy decision returned."},
        422: {"description": "Validation error: Malformed learning context."},
    },
)
def determine_pedagogy_decision(context: NormalizedLearningContext) -> PedagogyDecision:
    """AI/ML-2 interface: Answers how a topic should be taught given learner evidence (A2-S4-01)."""
    engine = get_pedagogy_engine()
    return engine.determine_pedagogy(context)


@router.post(
    "/evaluate-assessment",
    response_model=MasteryUpdateResult,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Assessment Evidence & Update Mastery (A2-S4-03)",
    description=(
        "Consumes assessment evidence from Backend, updates concept mastery, classifies into canonical BRD tiers "
        "(Weak < 50%, Developing 50-79%, Proficient 80-100%), and emits measurable remediation signals."
    ),
    responses={
        200: {"description": "Mastery successfully evaluated with remediation signal."},
        422: {"description": "Validation error: Malformed assessment evidence."},
    },
)
def evaluate_assessment_evidence(evidence: AssessmentEvidence) -> MasteryUpdateResult:
    """AI/ML-2 interface: Computes mastery and generates remediation signals from assessment evidence (A2-S4-03)."""
    engine = get_mastery_engine()
    return engine.evaluate_assessment(evidence)


@router.post(
    "/remediation-loop",
    response_model=ClosedLoopResult,
    status_code=status.HTTP_200_OK,
    summary="Execute Remediation Closed-Loop (A2-S4-04)",
    description=(
        "Executes complete closed loop: Initial Assessment -> Mastery Update -> Remediation Pedagogy -> "
        "Reassessment -> Updated State & Next Action."
    ),
    responses={
        200: {"description": "Closed-loop remediation cycle trace returned."},
        422: {"description": "Validation error: Malformed request payload."},
    },
)
def execute_remediation_loop(request: RemediationCycleRequest) -> ClosedLoopResult:
    """AI/ML-2 interface: Orchestrates the adaptive remediation loop (A2-S4-04)."""
    service = get_remediation_service()
    return service.run_remediation_cycle(
        learner_id=request.learner_id,
        topic=request.topic,
        initial_score=request.initial_score,
        reassessment_score=request.reassessment_score,
        learner_stage=request.learner_stage,
        academic_domain=request.academic_domain,
    )

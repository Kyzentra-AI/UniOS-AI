
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.achievement_event import AchievementEventEngine
from app.core.assessment import AssessmentGenerationEngine
from app.core.aiml2_client import AIML2Client, AIML2ClientError
from app.core.build_coach import BuildCoachEngine
from app.core.build_plan import BuildPlanGenerationEngine
from app.core.build_recommend import BuildRecommendationEngine
from app.core.challenge_reasoning import analyze_challenge
from app.core.collaboration import CollaborationOrchestrationEngine
from app.core.competition_planning import CompetitionPlanningEngine
from app.core.competition_recommend import CompetitionRecommendationEngine
from app.core.context import ContextEngine
from app.core.learning_interpreter import LearningRequestInterpreter
from app.core.mastery import MasteryEvaluationEngine
from app.core.memory_summary import MemorySummaryEngine
from app.core.mentor import MentorChatEngine
from app.core.roadmap_generator import RoadmapGenerationEngine
from app.core.service import KIEService
from app.core.syllabus import SyllabusExtractionEngine
from app.core.webhook import BackendWebhookSender

from app.schemas.achievement_event import (
    AchievementEventRequest,
    AchievementEventResponse,
)
from app.schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
)
from app.schemas.build_coach import (
    BuildCoachRequest,
    BuildCoachResponse,
)
from app.schemas.build_plan import (
    BuildPlanRequest,
    BuildPlanResponse,
)
from app.schemas.build_recommend import BuildRecommendationResponse
from app.schemas.challenge_reasoning import (
    ChallengeReasoningRequest,
    ChallengeReasoningResponse,
)
from app.schemas.collaboration import (
    CollaborationRequest,
    CollaborationResponse,
)
from app.schemas.competition_planning import (
    CompetitionPlanningRequest,
    CompetitionPlanningResponse,
)
from app.schemas.competition_recommend import (
    CompetitionRecommendationRequest,
    CompetitionRecommendationResponse,
)
from app.schemas.learning_interpreter import (
    LearningInterpretRequest,
    LearningInterpretResponse,
)
from app.schemas.mastery import (
    MasteryEvaluateRequest,
    MasteryEvaluateResponse,
)
from app.schemas.memory_summary import MemorySummaryRequest
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.schemas.request import (
    AnalyzeContextRequest,
    KIERequest,
    ResolveContextRequest,
)
from app.schemas.response import (
    AnalyzeContextResponse,
    KIEResponse,
    ResolveContextResponse,
)
from app.schemas.roadmap_generate import (
    AIMLRoadmapResponse,
    RoadmapContextV2Request,
)
from app.schemas.syllabus import (
    SyllabusExtractRequest,
    SyllabusExtractResponse,
)
from app.schemas.career import (
    ATSAnalyzeRequest,
    ATSAnalyzeResponse,
    ResumeGenerateRequest,
)

router = APIRouter(tags=["KIE"])

kie_service = KIEService()
context_engine = ContextEngine()
roadmap_generation_engine = RoadmapGenerationEngine()
syllabus_engine = SyllabusExtractionEngine()
memory_summary_engine = MemorySummaryEngine()
webhook_sender = BackendWebhookSender()

build_plan_engine = BuildPlanGenerationEngine()
build_coach_engine = BuildCoachEngine()
build_recommendation_engine = BuildRecommendationEngine()
learning_interpreter = LearningRequestInterpreter()

aiml2_client = AIML2Client()

competition_planning_engine = CompetitionPlanningEngine()
collaboration_engine = CollaborationOrchestrationEngine()
competition_recommendation_engine = CompetitionRecommendationEngine()
achievement_event_engine = AchievementEventEngine()

assessment_engine = AssessmentGenerationEngine()
mastery_engine = MasteryEvaluationEngine()
mentor_engine = MentorChatEngine()


def _aiml2_error(exc: AIML2ClientError) -> HTTPException:
    return HTTPException(
        status_code=502,
        detail={
            "code": "AIML2_SERVICE_ERROR",
            "message": str(exc),
        },
    )


@router.post("/kie/execute", response_model=KIEResponse)
def execute_kie(request: KIERequest) -> KIEResponse:
    return kie_service.execute(request)


@router.post(
    "/api/v1/kie/context/analyze",
    response_model=AnalyzeContextResponse,
)
def analyze_onboarding_context(
    request: AnalyzeContextRequest,
    background_tasks: BackgroundTasks,
) -> AnalyzeContextResponse:
    result = context_engine.analyze_onboarding_context(request)

    callback_user_id = request.user_id or request.learner_id
    questions = result.get("questions", [])

    if callback_user_id and questions:
        background_tasks.add_task(
            webhook_sender.send_questions,
            callback_user_id,
            questions,
        )

    return AnalyzeContextResponse(**result)


@router.post(
    "/api/v1/kie/context/resolve",
    response_model=ResolveContextResponse,
)
def resolve_onboarding_context(
    request: ResolveContextRequest,
    background_tasks: BackgroundTasks,
) -> ResolveContextResponse:
    result = context_engine.resolve_onboarding_context(request)

    new_context = result.get("new_context", {})

    if request.user_id:
        background_tasks.add_task(
            webhook_sender.send_resolved_context,
            request.user_id,
            new_context,
        )

    return ResolveContextResponse(**result)


@router.post(
    "/api/v1/kie/roadmap/generate",
    response_model=AIMLRoadmapResponse,
)
def generate_roadmap(
    request: RoadmapContextV2Request,
) -> AIMLRoadmapResponse:
    return roadmap_generation_engine.generate(request)


@router.post(
    "/api/v1/kie/syllabus/extract",
    response_model=SyllabusExtractResponse,
)
def extract_syllabus(
    request: SyllabusExtractRequest,
) -> SyllabusExtractResponse:
    result = syllabus_engine.extract(request)
    return SyllabusExtractResponse(**result)


@router.post("/api/v1/kie/memory/summary")
def summarize_memory(
    request: MemorySummaryRequest,
) -> dict[str, Any]:
    return memory_summary_engine.summarize(request)


@router.post(
    "/api/v1/kie/build/plan",
    response_model=BuildPlanResponse,
)
def generate_build_plan(
    request: BuildPlanRequest,
) -> BuildPlanResponse:
    return build_plan_engine.generate(request)


@router.post(
    "/api/v1/kie/build/coach",
    response_model=BuildCoachResponse,
)
def build_coach(
    request: BuildCoachRequest,
) -> BuildCoachResponse:
    context_text = (
        ", ".join(
            f"{key}: {value}"
            for key, value in request.context.items()
        )
        if request.context
        else None
    )

    project_context = {
        key: request.project_context[key]
        for key in ("id", "title", "type", "status", "skills")
        if key in request.project_context
    }

    payload = {
        "intent": request.intent,
        "message": request.message,
        "context": context_text,
        "project_context": project_context or None,
    }

    try:
        result = aiml2_client.coach_build(payload)
        return BuildCoachResponse(**result)
    except AIML2ClientError as exc:
        raise _aiml2_error(exc) from exc


@router.get(
    "/api/v1/kie/build/recommend",
    response_model=BuildRecommendationResponse,
)
def build_recommend(
    learner_id: str,
) -> BuildRecommendationResponse:
    try:
        result = aiml2_client.recommend_builds(learner_id)
        return BuildRecommendationResponse(**result)
    except AIML2ClientError as exc:
        raise _aiml2_error(exc) from exc


@router.post(
    "/api/v1/kie/learn/interpret",
    response_model=LearningInterpretResponse,
)
def interpret_learning_request(
    request: LearningInterpretRequest,
) -> LearningInterpretResponse:
    return learning_interpreter.interpret(request)


@router.post(
    "/api/v1/kie/challenge/analyze",
    response_model=ChallengeReasoningResponse,
)
def analyze_challenge_endpoint(
    request: ChallengeReasoningRequest,
) -> ChallengeReasoningResponse:
    return analyze_challenge(request)


@router.post(
    "/api/v1/kie/competition/plan",
    response_model=CompetitionPlanningResponse,
)
def plan_competition(
    request: CompetitionPlanningRequest,
) -> CompetitionPlanningResponse:
    return competition_planning_engine.generate(request)


@router.post(
    "/api/v1/kie/competition/collaborate",
    response_model=CollaborationResponse,
)
def collaborate_on_competition(
    request: CollaborationRequest,
) -> CollaborationResponse:
    return collaboration_engine.generate(request)


@router.post(
    "/api/v1/kie/competition/recommend",
    response_model=CompetitionRecommendationResponse,
)
def recommend_competitions(
    request: CompetitionRecommendationRequest,
) -> CompetitionRecommendationResponse:
    return competition_recommendation_engine.generate(request)


@router.post(
    "/api/v1/kie/achievement/event",
    response_model=AchievementEventResponse,
)
def create_achievement_event(
    request: AchievementEventRequest,
) -> AchievementEventResponse:
    return achievement_event_engine.generate(request)


# Assessment, mastery evaluation, and mentor chat

@router.post(
    "/api/v1/kie/assessments/generate",
    response_model=AssessmentGenerateResponse,
)
def generate_assessment(
    request: AssessmentGenerateRequest,
) -> AssessmentGenerateResponse:
    return assessment_engine.generate(request)


@router.post(
    "/api/v1/kie/mastery/evaluate",
    response_model=MasteryEvaluateResponse,
)
def evaluate_mastery(
    request: MasteryEvaluateRequest,
) -> MasteryEvaluateResponse:
    return mastery_engine.evaluate(request)


@router.post(
    "/api/v1/kie/mentor/chat",
    response_model=MentorChatResponse,
)
def mentor_chat(
    request: MentorChatRequest,
) -> MentorChatResponse:
    return mentor_engine.generate(request)


# Career integration endpoints

@router.post("/api/v1/kie/career/resume/generate")
def generate_career_resume(
    request: ResumeGenerateRequest,
) -> dict[str, object]:
    career_context = dict(request.career_context)

    learner_context = career_context.get("learner")
    if isinstance(learner_context, dict):
        experience = learner_context.get("experience")

        if isinstance(experience, list):
            experience_lines = []
            for item in experience:
                if isinstance(item, dict):
                    details = [
                        f"{key}: {value}"
                        for key, value in item.items()
                        if value is not None and value != ""
                    ]
                    if details:
                        experience_lines.append("; ".join(details))
                elif item is not None and str(item).strip():
                    experience_lines.append(str(item))

            learner_context["experience"] = "\n".join(
                experience_lines
            )
        elif experience is None:
            learner_context["experience"] = ""
        elif not isinstance(experience, str):
            learner_context["experience"] = str(experience)

    context_learner_id = career_context.get(
        "learnerId",
        career_context.get("learner_id"),
    )

    if (
        context_learner_id
        and context_learner_id != request.learner_id
    ):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "CAREER_CONTEXT_LEARNER_MISMATCH",
                "message": (
                    "Career context learner ID does not match "
                    "the request."
                ),
            },
        )

    career_context["learnerId"] = request.learner_id
    career_context.pop("learner_id", None)

    payload = {
        "requestId": request.request_id,
        "learnerId": request.learner_id,
        "title": request.title,
        "source": request.source,
        "preferences": request.preferences.model_dump(
            by_alias=True,
            exclude_none=True,
        ),
        "content": request.content,
        "careerContext": career_context,
    }

    try:
        result = aiml2_client.generate_resume(payload)

        if not isinstance(result.get("content"), dict):
            raise HTTPException(
                status_code=502,
                detail={
                    "code": "INVALID_AIML2_RESPONSE",
                    "message": (
                        "AI/ML-2 returned an invalid resume response."
                    ),
                },
            )

        return result
    except AIML2ClientError as exc:
        raise _aiml2_error(exc) from exc


@router.post(
    "/api/v1/kie/career/ats/analyze",
    response_model=ATSAnalyzeResponse,
)
def analyze_career_ats(
    request: ATSAnalyzeRequest,
) -> ATSAnalyzeResponse:
    payload = request.model_dump(
        by_alias=True,
        exclude_none=True,
    )

    try:
        result = aiml2_client.analyze_ats(payload)
        return ATSAnalyzeResponse(**result)
    except AIML2ClientError as exc:
        raise _aiml2_error(exc) from exc

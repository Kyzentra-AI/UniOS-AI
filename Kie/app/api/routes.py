
from typing import Any

from fastapi import APIRouter, BackgroundTasks

from app.core.achievement_event import AchievementEventEngine
from app.core.build_coach import BuildCoachEngine
from app.core.build_plan import BuildPlanGenerationEngine
from app.core.build_recommend import BuildRecommendationEngine
from app.core.challenge_reasoning import analyze_challenge
from app.core.collaboration import CollaborationOrchestrationEngine
from app.core.competition_planning import CompetitionPlanningEngine
from app.core.competition_recommend import (
    CompetitionRecommendationEngine,
)
from app.core.context import ContextEngine
from app.core.learning_interpreter import LearningRequestInterpreter
from app.core.memory_summary import MemorySummaryEngine
from app.core.roadmap_generator import RoadmapGenerationEngine
from app.core.service import KIEService
from app.core.syllabus import SyllabusExtractionEngine
from app.core.webhook import BackendWebhookSender

from app.schemas.achievement_event import (
    AchievementEventRequest,
    AchievementEventResponse,
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
from app.schemas.memory_summary import MemorySummaryRequest
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
competition_planning_engine = CompetitionPlanningEngine()
collaboration_engine = CollaborationOrchestrationEngine()
competition_recommendation_engine = CompetitionRecommendationEngine()
achievement_event_engine = AchievementEventEngine()


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
    return build_coach_engine.generate(request)


@router.get(
    "/api/v1/kie/build/recommend",
    response_model=BuildRecommendationResponse,
)
def build_recommend(
    learner_id: str,
) -> BuildRecommendationResponse:
    return build_recommendation_engine.generate(learner_id)


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

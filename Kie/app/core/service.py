from app.agents.registry import AgentRegistry
from app.core.context import ContextEngine
from app.core.executor import ExecutionEngine
from app.core.identity import IdentityEngine
from app.core.intent import IntentEngine
from app.core.memory import MemoryEngine
from app.core.model_router import ModelRouter
from app.core.orchestrator import AgentOrchestrator
from app.core.planner import PlanningEngine
from app.core.roadmap import RoadmapContractBuilder
from app.core.tool_engine import ToolEngine
from app.core.trace import generate_request_id
from app.schemas.request import KIERequest
from app.schemas.response import (
    KIEResponse,
    KIEMetadata,
    RoadmapMetadata,
)


class KIEService:
    """
    Main KIE orchestration service.

    Sprint 3 responsibilities:
    - Resolve learner identity
    - Resolve learner context
    - Retrieve user-specific learner memory
    - Recognize intent
    - Create learner-aware roadmap plans
    - Build Backend-ready roadmap contracts
    - Execute selected agents
    - Classify memory updates
    - Update learner activity memory
    - Return structured roadmap metadata
    - Return Backend-ready roadmap contract

    Sprint 4 responsibilities:
    - Orchestrate agent selection
    - Orchestrate tool selection
    - Prepare execution-ready plans
    - Coordinate the execution flow

    Backend remains responsible for persistent roadmap
    and memory storage.
    """

    def __init__(self):
        self.identity_engine = IdentityEngine()

        self.memory_engine = MemoryEngine()

        self.context_engine = ContextEngine(
            memory_engine=self.memory_engine
        )

        self.intent_engine = IntentEngine()

        self.planning_engine = PlanningEngine()

        self.roadmap_builder = RoadmapContractBuilder()

        self.model_router = ModelRouter()

        self.agent_registry = AgentRegistry()

        self.tool_engine = ToolEngine()

        self.agent_orchestrator = AgentOrchestrator(
            agent_registry=self.agent_registry
        )

        self.execution_engine = ExecutionEngine(
            agent_registry=self.agent_registry,
            tool_engine=self.tool_engine,
        )

    def execute(
        self,
        request: KIERequest,
    ) -> KIEResponse:
        request_id = generate_request_id()

        identity = self.identity_engine.resolve(
            request
        )

        context = self.context_engine.resolve(
            request
        )

        intent = self.intent_engine.recognize(
            request.task
        )

        intent_routing = (
            self.model_router.routing_metadata(
                "intent"
            )
        )

        plan = self.planning_engine.create_plan(
            intent=intent.name,
            task=request.task,
            planning_horizon=request.planning_horizon,
            context=context,
        )

        planning_routing = (
            self.model_router.routing_metadata(
                "planning"
            )
        )

        roadmap_contract = (
            self.roadmap_builder.build(
                user_id=request.user_id,
                session_id=request.session_id,
                planning_horizon=(
                    request.planning_horizon
                ),
                learner_stage=(
                    request.learner_stage
                ),
                career_goal=(
                    request.learner_profile.career_goal
                ),
                plan=plan,
            )
        )

        # -------------------------------------------------
        # Sprint 4 orchestration
        # -------------------------------------------------
        #
        # Convert the Planning Engine output into an
        # execution-ready plan.
        #
        # AgentOrchestrator is responsible for selecting
        # valid agents and resolving explicitly requested
        # tools.
        #
        # ExecutionEngine remains responsible for actually
        # executing the agents and tools.
        # -------------------------------------------------

        execution_plan = (
            self.agent_orchestrator.prepare_plan(
                [
                    step.model_dump()
                    for step in plan
                ]
            )
        )

        result = self.execution_engine.execute(
            task=request.task,
            intent=intent.name,
            plan=execution_plan,
            context=context,
        )

        memory_category = (
            self.memory_engine.resolve_update_category(
                task=request.task,
                intent=intent.name,
            )
        )

        memory_update = self.memory_engine.update(
            category=memory_category,
            content={
                "task": request.task,
                "intent": intent.name,
                "planning_horizon": (
                    request.planning_horizon
                ),
                "status": "completed",
                "request_id": request_id,
            },
            source="kie_execution",
            user_id=request.user_id,
        )

        roadmap_metadata = RoadmapMetadata(
            planning_horizon=(
                roadmap_contract[
                    "planning_horizon"
                ]
            ),
            learner_stage=(
                roadmap_contract[
                    "learner_stage"
                ]
            ),
            career_goal=(
                roadmap_contract[
                    "career_goal"
                ]
            ),
            milestone_count=(
                roadmap_contract[
                    "milestone_count"
                ]
            ),
            planning_status=(
                roadmap_contract[
                    "planning_status"
                ]
            ),
        )

        metadata = KIEMetadata(
            trace={
                "request_id": request_id,
                "session_id": request.session_id,
                "correlation_id": (
                    request.trace.get(
                        "correlation_id"
                    )
                ),
            },
            model_routing={
                "intent": intent_routing,
                "planning": planning_routing,
            },
            planning={
                "horizon": (
                    request.planning_horizon
                ),
            },
            roadmap=roadmap_metadata,
            roadmap_contract=roadmap_contract,
            memory={
                "categories": context[
                    "memory_categories"
                ],
                "source": context[
                    "sources"
                ]["memory"],
                "updated": True,
                "updated_category": (
                    memory_update.category
                ),
                "user_id": request.user_id,
            },
        )

        return KIEResponse(
            request_id=request_id,
            session_id=request.session_id,
            status="success",
            identity=identity,
            context=context,
            intent=intent,
            plan=plan,
            result=result,
            error=None,
            metadata=metadata,
        )
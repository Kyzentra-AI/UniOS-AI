from app.agents.registry import AgentRegistry
from app.core.context import ContextEngine
from app.core.executor import ExecutionEngine
from app.core.identity import IdentityEngine
from app.core.intent import IntentEngine
from app.core.model_router import ModelRouter
from app.core.planner import PlanningEngine
from app.core.trace import generate_request_id
from app.core.tool_engine import ToolEngine
from app.schemas.request import KIERequest
from app.schemas.response import KIEResponse


class KIEService:
    """
    Main KIE orchestration service.

    Sprint 2 / P0 responsibilities:
    - Resolve learner identity
    - Resolve learner context
    - Recognize intent
    - Route model capability for intent
    - Create execution plan
    - Route model capability for planning
    - Select and execute agents
    - Execute approved tools
    - Return a structured KIE response
    """

    def __init__(self):
        self.identity_engine = IdentityEngine()
        self.context_engine = ContextEngine()
        self.intent_engine = IntentEngine()
        self.planning_engine = PlanningEngine()

        self.model_router = ModelRouter()

        self.agent_registry = AgentRegistry()
        self.tool_engine = ToolEngine()

        self.execution_engine = ExecutionEngine(
            agent_registry=self.agent_registry,
            tool_engine=self.tool_engine,
        )

    def execute(self, request: KIERequest) -> KIEResponse:
        """
        Execute a complete KIE request through the
        orchestration pipeline.
        """

        request_id = generate_request_id()

        # -------------------------------------------------
        # 1. Resolve identity
        # -------------------------------------------------

        identity = self.identity_engine.resolve(request)

        # -------------------------------------------------
        # 2. Resolve learner context
        # -------------------------------------------------

        context = self.context_engine.resolve(request)

        # -------------------------------------------------
        # 3. Recognize intent
        # -------------------------------------------------

        intent = self.intent_engine.recognize(
            request.task
        )

        intent_routing = self.model_router.routing_metadata(
            "intent"
        )

        # -------------------------------------------------
        # 4. Create execution plan
        # -------------------------------------------------

        plan = self.planning_engine.create_plan(
            intent=intent.name,
            task=request.task,
        )

        planning_routing = self.model_router.routing_metadata(
            "planning"
        )

        # -------------------------------------------------
        # 5. Execute plan
        # -------------------------------------------------

        result = self.execution_engine.execute(
            task=request.task,
            intent=intent.name,
            plan=[
                step.model_dump()
                for step in plan
            ],
            context=context,
        )

        # -------------------------------------------------
        # 6. Return structured response
        # -------------------------------------------------

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
            metadata={
                "trace": {
                    "request_id": request_id,
                    "session_id": request.session_id,
                    "correlation_id": request.trace.get(
                        "correlation_id"
                    ),
                },
                "model_routing": {
                    "intent": intent_routing,
                    "planning": planning_routing,
                },
            },
        )
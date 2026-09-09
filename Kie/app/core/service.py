from app.agents.registry import AgentRegistry
from app.core.executor import ExecutionEngine
from app.core.intent import IntentEngine
from app.core.planner import PlanningEngine
from app.core.trace import generate_request_id
from app.schemas.request import KIERequest
from app.schemas.response import KIEResponse


class KIEService:
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.intent_engine = IntentEngine()
        self.planning_engine = PlanningEngine()
        self.execution_engine = ExecutionEngine(
            agent_registry=self.agent_registry
        )

    def execute(self, request: KIERequest) -> KIEResponse:
        request_id = generate_request_id()

        # 1. Recognize intent
        intent = self.intent_engine.recognize(
            request.task
        )

        # 2. Create execution plan
        plan = self.planning_engine.create_plan(
            intent=intent.name,
            task=request.task,
        )

        # 3. Execute plan through Agent Registry
        result = self.execution_engine.execute(
            task=request.task,
            intent=intent.name,
            plan=[step.model_dump() for step in plan],
            context=request.context,
        )

        # 4. Return structured KIE response
        return KIEResponse(
            request_id=request_id,
            session_id=request.session_id,
            status="success",
            intent=intent,
            plan=plan,
            result=result,
        )
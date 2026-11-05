
import json

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
    IntentResult,
    PlanStep,
)


class KIEService:
    """Main KIE orchestration service with Ollama intelligence."""

    VALID_INTENTS = {
        "LEARN", "BUILD", "COMPETE", "LAUNCH", "GENERAL"
    }

    VALID_LEARNING_ACTIONS = {
        "explain", "teach", "practice", "revise",
        "assess", "summarize", "continue-learning",
    }

    VALID_BUILD_ACTIONS = {
        "create", "plan", "review", "debug",
        "improve", "document", "present",
    }

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

    @staticmethod
    def _parse_json(content: str) -> dict:
        """Parse a JSON object returned by the LLM."""

        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "", 1)
            content = content.replace("```", "").strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")

            if start == -1 or end <= start:
                raise ValueError("LLM did not return valid JSON.")

            data = json.loads(content[start:end + 1])

        if not isinstance(data, dict):
            raise ValueError("LLM response must be a JSON object.")

        return data

    def _recognize_intent(
        self,
        task: str,
    ) -> tuple[IntentResult, bool]:
        """
        Use deterministic KIE intent recognition first.

        Ollama classifies requests that the existing
        IntentEngine cannot confidently categorize.
        """

        fallback = self.intent_engine.recognize(task)

        # Preserve all explicitly recognized KIE workflows.
        # This protects LEARN, BUILD, COMPETE and LAUNCH.
        if fallback.name != "GENERAL":
            return fallback, False

        # Preserve the existing UniOS roadmap behavior.
        if "roadmap" in task.lower():
            return fallback, False

        prompt = f"""
Classify the following UniOS learner request.

Choose exactly one intent:
LEARN, BUILD, COMPETE, LAUNCH, GENERAL.

For LEARN, learning_action can be:
explain, teach, practice, revise, assess, summarize,
continue-learning, or null.

For BUILD, build_action can be:
create, plan, review, debug, improve, document,
present, or null.

Return only JSON in this format:
{{
  "name": "LEARN",
  "confidence": 0.95,
  "learning_action": "explain",
  "build_action": null
}}

Task: {task}
"""

        try:
            result = self.model_router.generate(
                prompt=prompt,
                capability="intent",
                system=(
                    "You are the KIE intent classification engine. "
                    "Return valid JSON only."
                ),
            )

            data = self._parse_json(result["content"])

            name = str(data.get("name", "")).upper()

            if name not in self.VALID_INTENTS:
                raise ValueError("Invalid intent returned by LLM.")

            confidence = float(data.get("confidence", 0.8))
            confidence = max(0.0, min(1.0, confidence))

            learning_action = data.get("learning_action")
            build_action = data.get("build_action")

            if learning_action not in self.VALID_LEARNING_ACTIONS:
                learning_action = None

            if build_action not in self.VALID_BUILD_ACTIONS:
                build_action = None

            return IntentResult(
                name=name,
                confidence=confidence,
                learning_action=learning_action,
                build_action=build_action,
            ), True

        except Exception:
            return fallback, False

    def _improve_plan(
        self,
        task: str,
        intent: IntentResult,
        plan: list[PlanStep],
        context: dict,
    ) -> tuple[list[PlanStep], bool]:
        """Improve existing plan descriptions using Ollama."""

        if not plan:
            return plan, False

        existing_steps = [
            step.description for step in plan
        ]

        prompt = f"""
Improve the following KIE execution plan.

Task: {task}
Intent: {intent.name}
Learner context: {json.dumps(context, default=str)}

Existing plan:
{json.dumps(existing_steps)}

Return JSON in this format:
{{
  "steps": [
    {{"step": "Improved actionable description"}}
  ]
}}

Rules:
- Return exactly {len(plan)} steps.
- Keep descriptions relevant to the task.
- Do not invent learner information.
- Preserve the original execution sequence.
"""

        try:
            result = self.model_router.generate(
                prompt=prompt,
                capability="planning",
                system=(
                    "You are the KIE planning engine. "
                    "Return valid JSON only."
                ),
            )

            data = self._parse_json(result["content"])
            descriptions = data.get("steps")

            if not isinstance(descriptions, list):
                raise ValueError("Invalid plan returned by LLM.")

            if len(descriptions) != len(plan):
                raise ValueError(
                    "LLM changed the number of plan steps."
                )

            normalized = []

            for item in descriptions:
                if isinstance(item, str):
                    description = item
                elif isinstance(item, dict):
                    description = item.get(
                        "step",
                        item.get("description", ""),
                    )
                else:
                    raise ValueError("Invalid plan step format.")

                if (
                    not isinstance(description, str)
                    or not description.strip()
                ):
                    raise ValueError("Empty plan description.")

                normalized.append(description.strip())

            improved_plan = [
                PlanStep(
                    step_id=step.step_id,
                    description=description,
                    agent=step.agent,
                )
                for step, description in zip(plan, normalized)
            ]

            return improved_plan, True

        except Exception:
            return plan, False

    def execute(self, request: KIERequest) -> KIEResponse:
        """Execute a KIE request using LLM-assisted orchestration."""

        request_id = generate_request_id()

        # 1. Resolve identity and learner context.
        identity = self.identity_engine.resolve(request)
        context = self.context_engine.resolve(request)

        # 2. Recognize intent.
        intent, intent_llm_used = self._recognize_intent(
            request.task
        )

        intent_routing = self.model_router.routing_metadata(
            "intent"
        )

        # 3. Create the original execution plan.
        plan = self.planning_engine.create_plan(
            intent=intent.name,
            task=request.task,
            planning_horizon=request.planning_horizon,
            context=context,
        )

        # 4. Improve plan using Ollama.
        plan, planning_llm_used = self._improve_plan(
            task=request.task,
            intent=intent,
            plan=plan,
            context=context,
        )

        planning_routing = self.model_router.routing_metadata(
            "planning"
        )

        # 5. Build roadmap contract.
        roadmap_contract = self.roadmap_builder.build(
            user_id=request.user_id,
            session_id=request.session_id,
            planning_horizon=request.planning_horizon,
            learner_stage=request.learner_stage,
            career_goal=request.learner_profile.career_goal,
            plan=plan,
        )

        # 6. Preserve Build metadata.
        build_action = getattr(
            intent,
            "build_action",
            None,
        )

        artifact_type = request.context.get(
            "artifact_type"
        )

        plan_steps = []

        for step in plan:
            step_data = step.model_dump()

            if build_action:
                step_data["build_action"] = build_action

            if artifact_type:
                step_data["artifact_type"] = artifact_type

            plan_steps.append(step_data)

        # 7. Prepare agent execution plan.
        execution_plan = self.agent_orchestrator.prepare_plan(
            plan_steps
        )

        # 8. Execute through existing agents and tools.
        result = self.execution_engine.execute(
            task=request.task,
            intent=intent.name,
            plan=execution_plan,
            context=context,
        )

        # 9. Update memory.
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
                "planning_horizon": request.planning_horizon,
                "status": "completed",
                "request_id": request_id,
            },
            source="kie_execution",
            user_id=request.user_id,
        )

        # 10. Build roadmap metadata.
        roadmap_metadata = RoadmapMetadata(
            planning_horizon=roadmap_contract[
                "planning_horizon"
            ],
            learner_stage=roadmap_contract["learner_stage"],
            career_goal=roadmap_contract["career_goal"],
            milestone_count=roadmap_contract["milestone_count"],
            planning_status=roadmap_contract["planning_status"],
        )

        # 11. Build execution metadata.
        metadata = KIEMetadata(
            trace={
                "request_id": request_id,
                "session_id": request.session_id,
                "correlation_id": request.trace.get(
                    "correlation_id"
                ),
                "llm": {
                    "provider": "ollama",
                    "model": self.model_router.route(
                        "general"
                    ).model,
                    "intent_used": intent_llm_used,
                    "planning_used": planning_llm_used,
                },
            },
            model_routing={
                "intent": intent_routing,
                "planning": planning_routing,
            },
            planning={
                "horizon": request.planning_horizon,
            },
            roadmap=roadmap_metadata,
            roadmap_contract=roadmap_contract,
            memory={
                "categories": context["memory_categories"],
                "source": context["sources"]["memory"],
                "updated": True,
                "updated_category": memory_update.category,
                "user_id": request.user_id,
            },
        )

        # 12. Return existing KIE response contract.
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


from typing import Any

from app.agents.registry import AgentRegistry
from app.core.reliability import ExecutionReliability
from app.core.tool_engine import ToolEngine


class ExecutionEngine:
    """
    Executes planned KIE steps with bounded agent retries.

    Sprint 4:
    - Resolve agents through AgentRegistry.
    - Retry failed executions within a bounded limit.
    - Return structured execution failure details.
    - Invoke tools only after successful agent execution.

    Sprint 5:
    - Pass build capability and artifact metadata to agents
      through a dedicated execution_context field.
    - Preserve the existing agent interface and learner context.

    Note:
    This layer provides bounded retries, not hard execution timeouts.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_engine: ToolEngine | None = None,
        reliability: ExecutionReliability | None = None,
    ):
        self.agent_registry = agent_registry
        self.tool_engine = tool_engine or ToolEngine()
        self.reliability = reliability or ExecutionReliability()

    def execute(
        self,
        task: str,
        intent: str,
        plan: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        executed_steps: list[dict[str, Any]] = []
        failed_steps = 0

        for step in plan:
            step_id = step["step_id"]
            agent_name = step.get("agent", "general-agent")

            execution_context = dict(context)

            build_metadata: dict[str, Any] = {}
            for key in (
                "build_action",
                "build_capability",
                "artifact_type",
            ):
                value = step.get(key)
                if value is not None:
                    build_metadata[key] = value

            if build_metadata:
                execution_context["execution_context"] = build_metadata

            def run_agent() -> Any:
                agent = self.agent_registry.get(agent_name)
                return agent.execute(
                    task=task,
                    context=execution_context,
                )

            reliability_result = self.reliability.execute(run_agent)

            step_result: dict[str, Any] = {
                "step_id": step_id,
                "agent": agent_name,
                "result": reliability_result["result"],
                "execution_status": reliability_result["status"],
                "attempts": reliability_result["attempts"],
                "fallback_used": reliability_result["fallback_used"],
            }

            if reliability_result["status"] == "failed":
                failed_steps += 1
                step_result["error"] = reliability_result["error"]
            else:
                tool_name = step.get("tool")

                if tool_name:
                    tool_result = self.tool_engine.invoke(
                        tool_name=tool_name,
                        arguments=step.get("tool_arguments", {}),
                        permission_granted=step.get(
                            "permission_granted",
                            True,
                        ),
                    )

                    step_result["tool"] = tool_name
                    step_result["tool_result"] = tool_result

            executed_steps.append(step_result)

        return {
            "message": (
                f"KIE processed the {intent} request."
                if failed_steps == 0
                else f"KIE processed the {intent} request with failures."
            ),
            "task": task,
            "executed_steps": len(executed_steps),
            "execution_details": executed_steps,
            "status": (
                "success" if failed_steps == 0 else "partial_failure"
            ),
            "failed_steps": failed_steps,
        }

from typing import Any

from app.agents.registry import AgentRegistry
from app.core.tool_engine import ToolEngine


class ExecutionEngine:
    """
    Executes the steps produced by the KIE planning layer.

    Responsibilities:
    - Resolve the selected agent from AgentRegistry.
    - Execute planned steps through the selected agent.
    - Invoke explicitly requested tools through ToolEngine.
    - Keep tool execution allowlisted and permission-aware.
    - Return structured execution results.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_engine: ToolEngine | None = None,
    ):
        self.agent_registry = agent_registry
        self.tool_engine = tool_engine or ToolEngine()

    def execute(
        self,
        task: str,
        intent: str,
        plan: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the KIE plan.

        Each plan step normally contains an agent.

        If a step also contains a tool definition:

        {
            "tool": "calculator",
            "tool_arguments": {
                "a": 10,
                "b": 5
            }
        }

        the ToolEngine is used to execute that tool safely.
        """

        executed_steps = []

        for step in plan:
            agent_name = step.get(
                "agent",
                "general-agent",
            )

            agent = self.agent_registry.get(agent_name)

            agent_result = agent.execute(
                task=task,
                context=context,
            )

            step_result: dict[str, Any] = {
                "step_id": step["step_id"],
                "agent": agent_name,
                "result": agent_result,
            }

            # -------------------------------------------------
            # Optional tool execution
            # -------------------------------------------------

            tool_name = step.get("tool")

            if tool_name:
                tool_arguments = step.get(
                    "tool_arguments",
                    {},
                )

                tool_result = self.tool_engine.invoke(
                    tool_name=tool_name,
                    arguments=tool_arguments,
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
                f"KIE successfully processed the "
                f"{intent} request."
            ),
            "task": task,
            "executed_steps": len(executed_steps),
            "execution_details": executed_steps,
        }
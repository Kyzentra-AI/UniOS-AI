from typing import Any

from app.agents.registry import AgentRegistry


class ExecutionEngine:
    """
    Executes the steps produced by the KIE planning layer.

    Sprint 1 implementation:
    - Resolves the selected agent from AgentRegistry.
    - Executes each planned step through that agent.
    - Returns a structured execution result.
    """

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    def execute(
        self,
        task: str,
        intent: str,
        plan: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:

        executed_steps = []

        for step in plan:
            agent_name = step.get("agent", "general-agent")

            agent = self.agent_registry.get(agent_name)

            agent_result = agent.execute(
                task=task,
                context=context,
            )

            executed_steps.append(
                {
                    "step_id": step["step_id"],
                    "agent": agent_name,
                    "result": agent_result,
                }
            )

        return {
            "message": f"KIE successfully processed the {intent} request.",
            "task": task,
            "executed_steps": len(executed_steps),
            "execution_details": executed_steps,
        }
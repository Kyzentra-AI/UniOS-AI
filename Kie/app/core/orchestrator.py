from typing import Any

from app.agents.registry import AgentRegistry


class AgentOrchestrator:
    """
    Coordinates agent and tool selection for KIE execution.

    Responsibilities:
    - Select the agent for each planned step.
    - Resolve the requested tool for a step.
    - Keep orchestration decisions deterministic.
    - Produce an execution-ready plan.

    The orchestrator does not execute agents or tools itself.
    Execution remains the responsibility of ExecutionEngine.
    """

    DEFAULT_AGENT = "general-agent"

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    def select_agent(
        self,
        step: dict[str, Any],
    ) -> str:
        """
        Select the agent for a planned step.

        If the plan specifies an agent, use it when that
        agent exists in the registry.

        Otherwise fall back to the general agent.
        """

        requested_agent = step.get(
            "agent",
            self.DEFAULT_AGENT,
        )

        try:
            self.agent_registry.get(requested_agent)
            return requested_agent
        except Exception:
            return self.DEFAULT_AGENT

    def select_tool(
        self,
        step: dict[str, Any],
    ) -> str | None:
        """
        Select an explicitly requested tool.

        Tool execution itself is intentionally handled by
        ToolEngine through ExecutionEngine.
        """

        tool_name = step.get("tool")

        if not tool_name:
            return None

        return tool_name

    def prepare_plan(
        self,
        plan: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Convert the planning result into an
        execution-ready orchestration plan.

        The original plan is not mutated.
        """

        orchestrated_plan = []

        for step in plan:
            orchestrated_step = dict(step)

            orchestrated_step["agent"] = self.select_agent(
                step
            )

            tool_name = self.select_tool(step)

            if tool_name:
                orchestrated_step["tool"] = tool_name

            orchestrated_plan.append(orchestrated_step)

        return orchestrated_plan
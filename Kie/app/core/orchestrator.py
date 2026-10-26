
from app.agents.registry import AgentRegistry


class AgentOrchestrator:
    """
    Coordinates agent and capability selection for KIE execution.

    Sprint 4:
    - Select agents.
    - Preserve explicitly requested tools.
    - Prepare execution-ready plans.

    Sprint 5:
    - Route structured Build actions to the project agent.
    - Attach the selected Build capability to each execution step.
    """

    DEFAULT_AGENT = "general-agent"
    BUILD_AGENT = "project-agent"

    BUILD_CAPABILITIES = {
        "create",
        "plan",
        "review",
        "debug",
        "improve",
        "document",
        "present",
    }

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry

    def select_agent(self, step: dict) -> str:
        build_action = step.get("build_action")

        if build_action in self.BUILD_CAPABILITIES:
            requested_agent = self.BUILD_AGENT
        else:
            requested_agent = step.get(
                "agent",
                self.DEFAULT_AGENT,
            )

        try:
            self.agent_registry.get(requested_agent)
            return requested_agent
        except Exception:
            return self.DEFAULT_AGENT

    def select_build_capability(self, step: dict) -> str | None:
        build_action = step.get("build_action")

        if build_action in self.BUILD_CAPABILITIES:
            return build_action

        return None

    def select_tool(self, step: dict) -> str | None:
        tool_name = step.get("tool")

        if not tool_name:
            return None

        return tool_name

    def prepare_plan(self, plan: list[dict]) -> list[dict]:
        orchestrated_plan = []

        for step in plan:
            orchestrated_step = dict(step)

            orchestrated_step["agent"] = self.select_agent(step)

            build_capability = self.select_build_capability(step)

            if build_capability:
                orchestrated_step["build_capability"] = (
                    build_capability
                )

            tool_name = self.select_tool(step)

            if tool_name:
                orchestrated_step["tool"] = tool_name

            orchestrated_plan.append(orchestrated_step)

        return orchestrated_plan

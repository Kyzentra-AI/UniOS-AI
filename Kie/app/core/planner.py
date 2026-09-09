from app.schemas.response import PlanStep


class PlanningEngine:
    """
    Basic planning engine for Sprint 1.

    Creates a simple execution plan based on
    the recognized KIE intent.
    """

    def create_plan(
        self,
        intent: str,
        task: str,
    ) -> list[PlanStep]:

        return [
            PlanStep(
                step_id="step-1",
                description=f"Process {intent} request",
                agent=self._select_agent(intent),
            )
        ]

    def _select_agent(self, intent: str) -> str:

        agent_map = {
            "LEARN": "tutor-agent",
            "BUILD": "project-agent",
            "COMPETE": "hackathon-agent",
            "LAUNCH": "career-agent",
            "GENERAL": "general-agent",
        }

        return agent_map.get(intent, "general-agent")
from typing import Any

from app.agents.base import BaseAgent


class GeneralAgent(BaseAgent):
    name = "general-agent"

    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Processed task: {task}",
        }


class TutorAgent(BaseAgent):
    name = "tutor-agent"

    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Tutor agent processed: {task}",
        }


class ProjectAgent(BaseAgent):
    name = "project-agent"

    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Project agent processed: {task}",
        }


class HackathonAgent(BaseAgent):
    name = "hackathon-agent"

    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Hackathon agent processed: {task}",
        }


class CareerAgent(BaseAgent):
    name = "career-agent"

    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Career agent processed: {task}",
        }


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

        self.register(GeneralAgent())
        self.register(TutorAgent())
        self.register(ProjectAgent())
        self.register(HackathonAgent())
        self.register(CareerAgent())

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' is not registered")

        return self._agents[name]

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())
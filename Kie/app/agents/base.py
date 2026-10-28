from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Base interface for all KIE agents.
    """

    name: str = "base-agent"

    @abstractmethod
    def execute(
        self,
        task: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a task using the provided context.
        """
        pass

import os
from dataclasses import dataclass
from typing import Any

from app.core.ollama_provider import OllamaProvider


@dataclass
class ModelRoute:
    """Describes the model selected for a KIE task."""

    provider: str
    model: str
    capability: str
    reason: str
    fallback_model: str | None = None


class ModelRouter:
    """
    KIE Model Router.

    Selects the model according to task capability
    and sends inference requests to the selected provider.
    """

    def __init__(self, provider: OllamaProvider | None = None):
        self.provider = provider or OllamaProvider()
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        self.routes = {
            "intent": ModelRoute(
                provider="ollama",
                model=model_name,
                capability="structured",
                reason="Intent classification uses Ollama",
            ),
            "planning": ModelRoute(
                provider="ollama",
                model=model_name,
                capability="reasoning",
                reason="Planning uses Ollama",
            ),
            "general": ModelRoute(
                provider="ollama",
                model=model_name,
                capability="general",
                reason="General requests use Ollama",
            ),
        }

    def route(self, capability: str) -> ModelRoute:
        """Select a model route for the requested capability."""

        return self.routes.get(capability, self.routes["general"])

    def routing_metadata(
        self,
        capability: str,
    ) -> dict[str, str | None]:
        """Return routing metadata for tracing."""

        route = self.route(capability)

        return {
            "provider": route.provider,
            "model": route.model,
            "capability": route.capability,
            "reason": route.reason,
            "fallback_model": route.fallback_model,
        }

    def generate(
        self,
        prompt: str,
        capability: str = "general",
        system: str | None = None,
    ) -> dict[str, Any]:
        """Generate an actual LLM response through the selected provider."""

        route = self.route(capability)

        return self.provider.generate(
            prompt=prompt,
            system=system,
            capability=route.capability,
        )

from dataclasses import dataclass


@dataclass
class ModelRoute:
    """
    Describes the model selected for a KIE task.
    """

    provider: str
    model: str
    capability: str
    reason: str
    fallback_model: str | None = None


class ModelRouter:
    """
    KIE Model Router.

    Responsible for selecting a model/provider according to
    task capability while keeping provider-specific details
    outside the orchestration logic.
    """

    def __init__(self):
        self.routes = {
            "intent": ModelRoute(
                provider="local",
                model="fast-structured-model",
                capability="structured",
                reason="Intent classification requires fast structured output",
                fallback_model="general-model",
            ),
            "planning": ModelRoute(
                provider="local",
                model="reasoning-model",
                capability="reasoning",
                reason="Planning requires reasoning capability",
                fallback_model="general-model",
            ),
            "general": ModelRoute(
                provider="local",
                model="general-model",
                capability="general",
                reason="General requests use the general model",
                fallback_model=None,
            ),
        }

    def route(self, capability: str) -> ModelRoute:
        """
        Select a model route for the requested capability.
        """

        if capability not in self.routes:
            return self.routes["general"]

        return self.routes[capability]

    def routing_metadata(
        self,
        capability: str,
    ) -> dict[str, str | None]:
        """
        Return structured routing metadata for tracing
        and reproducibility.
        """

        route = self.route(capability)

        return {
            "provider": route.provider,
            "model": route.model,
            "capability": route.capability,
            "reason": route.reason,
            "fallback_model": route.fallback_model,
        }
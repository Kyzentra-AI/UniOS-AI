
from app.core.model_router import ModelRouter


def test_intent_route_uses_ollama():
    router = ModelRouter()
    route = router.route("intent")

    assert route.provider == "ollama"
    assert route.model == "qwen2.5:3b"
    assert route.capability == "structured"


def test_planning_route_uses_ollama():
    router = ModelRouter()
    route = router.route("planning")

    assert route.provider == "ollama"
    assert route.model == "qwen2.5:3b"
    assert route.capability == "reasoning"


def test_general_route_uses_ollama():
    router = ModelRouter()
    route = router.route("general")

    assert route.provider == "ollama"
    assert route.model == "qwen2.5:3b"
    assert route.capability == "general"


def test_unknown_capability_falls_back_to_general():
    router = ModelRouter()
    route = router.route("unknown-capability")

    assert route.capability == "general"
    assert route.model == "qwen2.5:3b"


def test_intent_route_has_no_unconfigured_fallback():
    router = ModelRouter()
    assert router.route("intent").fallback_model is None


def test_planning_route_has_no_unconfigured_fallback():
    router = ModelRouter()
    assert router.route("planning").fallback_model is None


def test_general_route_has_no_fallback():
    router = ModelRouter()
    assert router.route("general").fallback_model is None


def test_routing_metadata_is_structured():
    router = ModelRouter()
    metadata = router.routing_metadata("planning")

    assert metadata["provider"] == "ollama"
    assert metadata["model"] == "qwen2.5:3b"
    assert metadata["capability"] == "reasoning"
    assert metadata["fallback_model"] is None


def test_unknown_capability_metadata_uses_general_route():
    router = ModelRouter()
    metadata = router.routing_metadata("something-new")

    assert metadata["provider"] == "ollama"
    assert metadata["model"] == "qwen2.5:3b"
    assert metadata["capability"] == "general"


def test_generate_calls_ollama_provider():
    class FakeProvider:
        def generate(self, prompt, system=None, capability="general"):
            return {
                "content": "Test LLM response",
                "provider": "ollama",
                "model": "qwen2.5:3b",
                "capability": capability,
            }

    router = ModelRouter(provider=FakeProvider())
    result = router.generate("Test prompt", "planning")

    assert result["content"] == "Test LLM response"
    assert result["provider"] == "ollama"
    assert result["capability"] == "reasoning"

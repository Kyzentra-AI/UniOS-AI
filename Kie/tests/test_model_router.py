from app.core.model_router import ModelRouter


def test_intent_route_uses_structured_capability():
    router = ModelRouter()

    route = router.route("intent")

    assert route.capability == "structured"
    assert route.provider == "local"
    assert route.model == "fast-structured-model"


def test_planning_route_uses_reasoning_capability():
    router = ModelRouter()

    route = router.route("planning")

    assert route.capability == "reasoning"
    assert route.provider == "local"
    assert route.model == "reasoning-model"


def test_general_route_uses_general_model():
    router = ModelRouter()

    route = router.route("general")

    assert route.capability == "general"
    assert route.provider == "local"
    assert route.model == "general-model"


def test_unknown_capability_falls_back_to_general():
    router = ModelRouter()

    route = router.route("unknown-capability")

    assert route.capability == "general"
    assert route.model == "general-model"


def test_intent_route_has_fallback_model():
    router = ModelRouter()

    route = router.route("intent")

    assert route.fallback_model == "general-model"


def test_planning_route_has_fallback_model():
    router = ModelRouter()

    route = router.route("planning")

    assert route.fallback_model == "general-model"


def test_general_route_has_no_fallback():
    router = ModelRouter()

    route = router.route("general")

    assert route.fallback_model is None


def test_routing_metadata_is_structured():
    router = ModelRouter()

    metadata = router.routing_metadata("planning")

    assert metadata["provider"] == "local"
    assert metadata["model"] == "reasoning-model"
    assert metadata["capability"] == "reasoning"
    assert metadata["fallback_model"] == "general-model"


def test_unknown_capability_metadata_uses_general_route():
    router = ModelRouter()

    metadata = router.routing_metadata("something-new")

    assert metadata["provider"] == "local"
    assert metadata["model"] == "general-model"
    assert metadata["capability"] == "general"
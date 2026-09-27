from app.core.tool_router import ToolRouter


def test_explain_routes_to_knowledge_tool():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "knowledge"


def test_teach_routes_to_knowledge_tool():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="teach",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "knowledge"


def test_practice_routes_to_knowledge_tool():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="practice",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "knowledge"


def test_assess_routes_to_assessment_tool():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="assess",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "assessment"


def test_revise_supports_retrieval():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="revise",
        requested_tool="retrieval",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "retrieval"


def test_summarize_supports_knowledge():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="summarize",
        requested_tool="knowledge",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "knowledge"


def test_continue_learning_supports_retrieval():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="continue-learning",
        requested_tool="retrieval",
    )

    assert result["status"] == "routed"
    assert result["tool"] == "retrieval"


def test_unapproved_tool_is_rejected():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="web_search",
    )

    assert result["status"] == "failed"
    assert (
        result["error"]["code"]
        == "tool_not_allowed_for_action"
    )


def test_non_allowlisted_tool_is_rejected():
    router = ToolRouter(
        allowed_tools={"knowledge"},
    )

    result = router.route_learning_tool(
        learning_action="assess",
        requested_tool="assessment",
    )

    assert result["status"] == "failed"
    assert (
        result["error"]["code"]
        == "tool_not_allowlisted"
    )


def test_permission_denied():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="knowledge",
        permissions={"retrieval"},
    )

    assert result["status"] == "failed"
    assert (
        result["error"]["code"]
        == "tool_permission_denied"
    )


def test_permission_allows_tool():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="knowledge",
        permissions={"knowledge"},
    )

    assert result["status"] == "routed"
    assert result["tool"] == "knowledge"


def test_timeout_is_bounded():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="knowledge",
        timeout_seconds=100,
    )

    assert result["status"] == "routed"
    assert result["timeout_seconds"] == 30


def test_default_timeout_is_applied():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="knowledge",
    )

    assert result["timeout_seconds"] == 10


def test_invalid_learning_action_is_rejected():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="unknown-action",
    )

    assert result["status"] == "failed"
    assert (
        result["error"]["code"]
        == "unsupported_learning_action"
    )


def test_tool_arguments_are_preserved():
    router = ToolRouter()

    result = router.route_learning_tool(
        learning_action="explain",
        requested_tool="knowledge",
        arguments={
            "topic": "recursion",
            "level": "beginner",
        },
    )

    assert result["status"] == "routed"
    assert result["arguments"]["topic"] == "recursion"
    assert result["arguments"]["level"] == "beginner"
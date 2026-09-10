from app.core.tool_engine import ToolDefinition, ToolEngine


def add_numbers(a: int, b: int) -> int:
    return a + b


def failing_tool() -> None:
    raise RuntimeError("Tool failed")


def test_tool_can_be_registered():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="calculator",
            description="Adds two numbers",
            handler=add_numbers,
        )
    )

    assert engine.is_allowed("calculator")
    assert "calculator" in engine.list_tools()


def test_registered_tool_can_be_invoked():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="calculator",
            description="Adds two numbers",
            handler=add_numbers,
        )
    )

    result = engine.invoke(
        "calculator",
        {
            "a": 10,
            "b": 5,
        },
    )

    assert result["status"] == "success"
    assert result["tool"] == "calculator"
    assert result["result"] == 15


def test_unregistered_tool_is_rejected():
    engine = ToolEngine()

    result = engine.invoke(
        "unknown-tool",
        {},
    )

    assert result["status"] == "error"
    assert result["error"]["code"] == "TOOL_NOT_ALLOWED"


def test_permission_required_tool_is_rejected_without_permission():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="protected-tool",
            description="A protected tool",
            handler=lambda: "secret",
            requires_permission=True,
        )
    )

    result = engine.invoke(
        "protected-tool",
        permission_granted=False,
    )

    assert result["status"] == "error"
    assert result["error"]["code"] == "PERMISSION_DENIED"


def test_permission_required_tool_can_run_with_permission():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="protected-tool",
            description="A protected tool",
            handler=lambda: "allowed",
            requires_permission=True,
        )
    )

    result = engine.invoke(
        "protected-tool",
        permission_granted=True,
    )

    assert result["status"] == "success"
    assert result["result"] == "allowed"


def test_tool_execution_failure_is_normalized():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="failing-tool",
            description="A tool that fails",
            handler=failing_tool,
        )
    )

    result = engine.invoke("failing-tool")

    assert result["status"] == "error"
    assert result["tool"] == "failing-tool"
    assert result["error"]["code"] == "TOOL_EXECUTION_ERROR"


def test_empty_arguments_are_supported():
    engine = ToolEngine()

    engine.register(
        ToolDefinition(
            name="simple-tool",
            description="A simple tool",
            handler=lambda: "completed",
        )
    )

    result = engine.invoke("simple-tool")

    assert result["status"] == "success"
    assert result["result"] == "completed"
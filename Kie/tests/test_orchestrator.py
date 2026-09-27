from app.agents.registry import AgentRegistry
from app.core.orchestrator import AgentOrchestrator


def test_orchestrator_selects_registered_agent():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)

    step = {
        "step_id": "step-1",
        "agent": "tutor-agent",
    }

    assert orchestrator.select_agent(step) == "tutor-agent"


def test_orchestrator_falls_back_for_unknown_agent():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)

    step = {
        "step_id": "step-1",
        "agent": "unknown-agent",
    }

    assert orchestrator.select_agent(step) == "general-agent"


def test_orchestrator_selects_explicit_tool():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)

    step = {
        "step_id": "step-1",
        "agent": "general-agent",
        "tool": "calculator",
    }

    assert orchestrator.select_tool(step) == "calculator"


def test_orchestrator_returns_no_tool_when_not_requested():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)

    step = {
        "step_id": "step-1",
        "agent": "general-agent",
    }

    assert orchestrator.select_tool(step) is None


def test_orchestrator_prepares_execution_plan():
    registry = AgentRegistry()
    orchestrator = AgentOrchestrator(registry)

    plan = [
        {
            "step_id": "step-1",
            "agent": "tutor-agent",
        },
        {
            "step_id": "step-2",
            "agent": "project-agent",
            "tool": "calculator",
            "tool_arguments": {
                "a": 10,
                "b": 5,
            },
        },
    ]

    result = orchestrator.prepare_plan(plan)

    assert len(result) == 2

    assert result[0]["agent"] == "tutor-agent"
    assert "tool" not in result[0]

    assert result[1]["agent"] == "project-agent"
    assert result[1]["tool"] == "calculator"

    # Original plan must remain unchanged.
    assert "tool" not in plan[0]
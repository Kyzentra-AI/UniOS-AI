
from app.agents.registry import AgentRegistry
from app.core.orchestrator import AgentOrchestrator


def test_debug_action_selects_project_agent():
    orchestrator = AgentOrchestrator(AgentRegistry())

    plan = orchestrator.prepare_plan(
        [
            {
                "step_id": "step-1",
                "build_action": "debug",
            }
        ]
    )

    assert plan[0]["agent"] == "project-agent"
    assert plan[0]["build_capability"] == "debug"


def test_document_action_selects_project_agent():
    orchestrator = AgentOrchestrator(AgentRegistry())

    plan = orchestrator.prepare_plan(
        [
            {
                "step_id": "step-1",
                "build_action": "document",
            }
        ]
    )

    assert plan[0]["agent"] == "project-agent"
    assert plan[0]["build_capability"] == "document"


def test_artifact_type_is_preserved_in_execution_plan():
    orchestrator = AgentOrchestrator(AgentRegistry())

    plan = orchestrator.prepare_plan(
        [
            {
                "step_id": "step-1",
                "artifact_type": "RESEARCH",
                "build_action": "create",
            }
        ]
    )

    assert plan[0]["artifact_type"] == "RESEARCH"
    assert plan[0]["build_capability"] == "create"

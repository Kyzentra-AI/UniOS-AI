
import pytest

from app.agents.registry import AgentRegistry
from app.core.orchestrator import AgentOrchestrator
from app.core.executor import ExecutionEngine


@pytest.mark.parametrize(
    "action",
    [
        "create",
        "plan",
        "review",
        "debug",
        "improve",
        "document",
        "present",
    ],
)
def test_all_build_actions_route_to_project_agent(action):
    orchestrator = AgentOrchestrator(AgentRegistry())

    plan = orchestrator.prepare_plan(
        [
            {
                "step_id": "step-1",
                "build_action": action,
            }
        ]
    )

    assert plan[0]["agent"] == "project-agent"
    assert plan[0]["build_capability"] == action


@pytest.mark.parametrize(
    "artifact_type",
    [
        "CODING",
        "RESEARCH",
        "BUSINESS",
        "ANALYSIS",
        "DESIGN",
    ],
)
def test_artifact_type_is_preserved_for_all_project_types(artifact_type):
    orchestrator = AgentOrchestrator(AgentRegistry())

    plan = orchestrator.prepare_plan(
        [
            {
                "step_id": "step-1",
                "build_action": "create",
                "artifact_type": artifact_type,
            }
        ]
    )

    assert plan[0]["agent"] == "project-agent"
    assert plan[0]["build_capability"] == "create"
    assert plan[0]["artifact_type"] == artifact_type


class CapturingProjectAgent:
    name = "project-agent"

    def __init__(self):
        self.received_context = None

    def execute(self, task, context):
        self.received_context = context
        return {
            "agent": self.name,
            "status": "completed",
        }


@pytest.mark.parametrize(
    ("action", "artifact_type"),
    [
        ("create", "CODING"),
        ("create", "RESEARCH"),
        ("plan", "BUSINESS"),
        ("review", "DESIGN"),
        ("analyze", "ANALYSIS"),
    ],
)
def test_execution_preserves_build_metadata(action, artifact_type):
    registry = AgentRegistry()
    agent = CapturingProjectAgent()
    registry.register(agent)

    engine = ExecutionEngine(agent_registry=registry)

    original_context = {
        "learner_stage": "final-year",
        "skills": ["Python"],
    }

    plan = [
        {
            "step_id": "step-1",
            "agent": "project-agent",
            "build_action": action,
            "build_capability": action,
            "artifact_type": artifact_type,
        }
    ]

    result = engine.execute(
        task="Work on my project",
        intent="build",
        plan=plan,
        context=original_context,
    )

    assert result["status"] == "success"
    assert agent.received_context["learner_stage"] == "final-year"
    assert agent.received_context["skills"] == ["Python"]
    assert agent.received_context["execution_context"] == {
        "build_action": action,
        "build_capability": action,
        "artifact_type": artifact_type,
    }

    assert original_context == {
        "learner_stage": "final-year",
        "skills": ["Python"],
    }

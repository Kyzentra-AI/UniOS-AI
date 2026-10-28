
from app.agents.registry import AgentRegistry
from app.core.executor import ExecutionEngine


class CapturingProjectAgent:
    name = "project-agent"

    def __init__(self):
        self.received_task = None
        self.received_context = None

    def execute(self, task, context):
        self.received_task = task
        self.received_context = context
        return {
            "agent": self.name,
            "status": "completed",
        }


def test_build_metadata_reaches_agent_context():
    registry = AgentRegistry()
    agent = CapturingProjectAgent()
    registry.register(agent)

    engine = ExecutionEngine(agent_registry=registry)

    learner_context = {
        "learner_stage": "final-year",
        "skills": ["Python"],
    }

    result = engine.execute(
        task="Create a research project",
        intent="build",
        plan=[
            {
                "step_id": "step-1",
                "agent": "project-agent",
                "build_action": "create",
                "build_capability": "create",
                "artifact_type": "RESEARCH",
            }
        ],
        context=learner_context,
    )

    assert result["status"] == "success"
    assert agent.received_task == "Create a research project"
    assert agent.received_context["learner_stage"] == "final-year"
    assert agent.received_context["skills"] == ["Python"]
    assert agent.received_context["execution_context"] == {
        "build_action": "create",
        "build_capability": "create",
        "artifact_type": "RESEARCH",
    }

    # The original learner context must remain unchanged.
    assert learner_context == {
        "learner_stage": "final-year",
        "skills": ["Python"],
    }


def test_regular_execution_does_not_add_build_metadata():
    registry = AgentRegistry()
    agent = CapturingProjectAgent()
    registry.register(agent)

    engine = ExecutionEngine(agent_registry=registry)

    context = {"learner_stage": "second-year"}

    result = engine.execute(
        task="Explain recursion",
        intent="learn",
        plan=[
            {
                "step_id": "step-1",
                "agent": "project-agent",
            }
        ],
        context=context,
    )

    assert result["status"] == "success"
    assert agent.received_context == context
    assert "execution_context" not in agent.received_context

from app.core.context import ContextEngine
from app.core.memory import MemoryEngine
from app.schemas.request import KIERequest


def test_learner_context_is_included():
    memory_engine = MemoryEngine()

    context_engine = ContextEngine(
        memory_engine=memory_engine
    )

    request = KIERequest(
        user_id="learner-context-001",
        session_id="session-001",
        role="student",
        task="Continue my current lesson",
        learner_stage="final-year",
        learner_context={
            "current_lesson": "Python Functions",
            "current_topic": "Decorators",
            "roadmap_id": "roadmap-001",
            "mission_id": "mission-001",
            "learning_session_id": "learning-session-001",
            "project_id": "project-001",
            "workspace_id": "workspace-001",
            "current_progress": {
                "completion_percentage": 65
            },
        },
    )

    resolved = context_engine.resolve(request)

    learner_context = resolved["learner_context"]

    assert learner_context["current_lesson"] == (
        "Python Functions"
    )

    assert learner_context["current_topic"] == (
        "Decorators"
    )

    assert learner_context["roadmap_id"] == (
        "roadmap-001"
    )

    assert learner_context["mission_id"] == (
        "mission-001"
    )

    assert learner_context["learning_session_id"] == (
        "learning-session-001"
    )

    assert learner_context["project_id"] == (
        "project-001"
    )

    assert learner_context["workspace_id"] == (
        "workspace-001"
    )

    assert learner_context["current_progress"][
        "completion_percentage"
    ] == 65


def test_learner_context_defaults_to_empty_values():
    memory_engine = MemoryEngine()

    context_engine = ContextEngine(
        memory_engine=memory_engine
    )

    request = KIERequest(
        user_id="learner-context-002",
        session_id="session-002",
        role="student",
        task="Create my daily plan",
    )

    resolved = context_engine.resolve(request)

    learner_context = resolved["learner_context"]

    assert learner_context["current_lesson"] is None

    assert learner_context["current_topic"] is None

    assert learner_context["roadmap_id"] is None

    assert learner_context["mission_id"] is None

    assert learner_context["learning_session_id"] is None

    assert learner_context["project_id"] is None

    assert learner_context["workspace_id"] is None

    assert learner_context["current_progress"] == {}


def test_learner_context_source_is_tracked():
    memory_engine = MemoryEngine()

    context_engine = ContextEngine(
        memory_engine=memory_engine
    )

    request = KIERequest(
        user_id="learner-context-003",
        session_id="session-003",
        role="student",
        task="Create my weekly roadmap",
        learner_context={
            "roadmap_id": "roadmap-003",
        },
    )

    resolved = context_engine.resolve(request)

    assert resolved["sources"][
        "learner_context"
    ] == "request"


def test_learner_context_isolated_between_requests():
    memory_engine = MemoryEngine()

    context_engine = ContextEngine(
        memory_engine=memory_engine
    )

    request_one = KIERequest(
        user_id="learner-context-004",
        session_id="session-004",
        role="student",
        task="Continue project",
        learner_context={
            "project_id": "project-A",
        },
    )

    request_two = KIERequest(
        user_id="learner-context-005",
        session_id="session-005",
        role="student",
        task="Continue project",
        learner_context={
            "project_id": "project-B",
        },
    )

    context_one = context_engine.resolve(
        request_one
    )

    context_two = context_engine.resolve(
        request_two
    )

    assert context_one[
        "learner_context"
    ]["project_id"] == "project-A"

    assert context_two[
        "learner_context"
    ]["project_id"] == "project-B"
from app.core.context import ContextEngine
from app.core.memory import MemoryEngine
from app.schemas.request import KIERequest


def test_career_context_retrieves_career_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Become a Software Engineer",
        user_id="student-001",
    )

    memory.store(
        category="projects",
        content="Build a full-stack application",
        user_id="student-001",
    )

    memory.store(
        category="achievements",
        content="Completed Python certification",
        user_id="student-001",
    )

    memory.store(
        category="preferences",
        content="Prefer practical learning",
        user_id="student-001",
    )

    context_engine = ContextEngine(
        memory_engine=memory
    )

    request = KIERequest(
        user_id="student-001",
        session_id="session-001",
        task="Create my career roadmap",
        planning_horizon="career",
    )

    context = context_engine.resolve(request)

    assert "goals" in context["memory"]
    assert "projects" in context["memory"]
    assert "achievements" in context["memory"]
    assert "preferences" in context["memory"]

    assert (
        context["memory"]["goals"][0]["content"]
        == "Become a Software Engineer"
    )


def test_weekly_context_retrieves_learning_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Improve DSA",
        user_id="student-002",
    )

    memory.store(
        category="learning_history",
        content="Completed arrays and strings",
        user_id="student-002",
    )

    memory.store(
        category="projects",
        content="KIE Core project",
        user_id="student-002",
    )

    memory.store(
        category="achievements",
        content="Completed Sprint 2",
        user_id="student-002",
    )

    context_engine = ContextEngine(
        memory_engine=memory
    )

    request = KIERequest(
        user_id="student-002",
        session_id="session-002",
        task="Create my weekly learning plan",
        planning_horizon="weekly",
    )

    context = context_engine.resolve(request)

    assert "goals" in context["memory"]
    assert "learning_history" in context["memory"]
    assert "projects" in context["memory"]
    assert "achievements" in context["memory"]

    assert (
        context["memory"]["learning_history"][0]["content"]
        == "Completed arrays and strings"
    )


def test_general_context_retrieves_preferences_and_conversations():
    memory = MemoryEngine()

    memory.store(
        category="preferences",
        content="Prefer hands-on learning",
        user_id="student-003",
    )

    memory.store(
        category="conversations",
        content="Learner wants to improve Python",
        user_id="student-003",
    )

    context_engine = ContextEngine(
        memory_engine=memory
    )

    request = KIERequest(
        user_id="student-003",
        session_id="session-003",
        task="Help me decide what to study next",
    )

    context = context_engine.resolve(request)

    assert "preferences" in context["memory"]
    assert "conversations" in context["memory"]

    assert (
        context["memory"]["preferences"][0]["content"]
        == "Prefer hands-on learning"
    )


def test_context_contains_memory_source():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Learn React",
        user_id="student-004",
    )

    context_engine = ContextEngine(
        memory_engine=memory
    )

    request = KIERequest(
        user_id="student-004",
        session_id="session-004",
        task="Create my weekly plan",
        planning_horizon="weekly",
    )

    context = context_engine.resolve(request)

    assert (
        context["sources"]["memory"]
        == "memory_engine"
    )


def test_context_contains_memory_categories():
    memory = MemoryEngine()

    context_engine = ContextEngine(
        memory_engine=memory
    )

    request = KIERequest(
        user_id="student-005",
        session_id="session-005",
        task="Create my semester roadmap",
        planning_horizon="semester",
    )

    context = context_engine.resolve(request)

    assert context["memory_categories"] == [
        "goals",
        "learning_history",
        "projects",
        "achievements",
    ]
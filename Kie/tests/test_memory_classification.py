from app.core.memory import MemoryEngine


def test_preference_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Save my learning preference",
        intent="GENERAL",
    )

    assert category == "preferences"


def test_project_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Remember this project",
        intent="BUILD",
    )

    assert category == "projects"


def test_goal_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Save my career goal",
        intent="LAUNCH",
    )

    assert category == "goals"


def test_achievement_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Save my achievement",
        intent="GENERAL",
    )

    assert category == "achievements"


def test_friction_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="I am struggling with Python",
        intent="LEARN",
    )

    assert category == "friction_context"


def test_learning_memory_classification():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Learn Python decorators",
        intent="LEARN",
    )

    assert category == "learning_history"


def test_normal_build_request_stays_learning_history():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Create my project plan",
        intent="BUILD",
    )

    assert category == "learning_history"


def test_normal_general_request_stays_learning_history():
    memory = MemoryEngine()

    category = memory.resolve_update_category(
        task="Help me plan my day",
        intent="GENERAL",
    )

    assert category == "learning_history"
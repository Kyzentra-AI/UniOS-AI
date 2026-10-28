from app.core.memory import MemoryEngine


def test_update_adds_learning_history():
    memory = MemoryEngine()

    memory.update(
        category="learning_history",
        content={
            "topic": "Python",
            "status": "completed",
        },
        source="learner_activity",
    )

    history = memory.retrieve(
        category="learning_history"
    )

    assert len(history) == 1

    assert history[0].content["topic"] == "Python"

    assert history[0].content["status"] == "completed"

    assert history[0].source == "learner_activity"


def test_update_adds_goal():
    memory = MemoryEngine()

    memory.update(
        category="goals",
        content={
            "goal": "Become a Full Stack Developer",
            "status": "active",
        },
        source="learner_activity",
    )

    goals = memory.retrieve(
        category="goals"
    )

    assert len(goals) == 1

    assert (
        goals[0].content["goal"]
        == "Become a Full Stack Developer"
    )


def test_multiple_updates_preserve_history():
    memory = MemoryEngine()

    memory.update(
        category="learning_history",
        content="Completed Python basics",
        source="learner_activity",
    )

    memory.update(
        category="learning_history",
        content="Completed Python OOP",
        source="learner_activity",
    )

    memory.update(
        category="learning_history",
        content="Completed Python APIs",
        source="learner_activity",
    )

    history = memory.retrieve(
        category="learning_history"
    )

    assert len(history) == 3

    assert history[0].content == (
        "Completed Python basics"
    )

    assert history[1].content == (
        "Completed Python OOP"
    )

    assert history[2].content == (
        "Completed Python APIs"
    )


def test_update_invalid_category():
    memory = MemoryEngine()

    try:
        memory.update(
            category="unknown",
            content="test",
        )
        assert False
    except ValueError as error:
        assert "Unsupported memory category" in str(
            error
        )


def test_updated_memory_can_be_retrieved_as_relevant_memory():
    memory = MemoryEngine()

    memory.update(
        category="goals",
        content="Learn React",
        source="learner_activity",
    )

    memory.update(
        category="projects",
        content="Build a React application",
        source="learner_activity",
    )

    relevant = memory.retrieve_relevant(
        categories=[
            "goals",
            "projects",
        ]
    )

    assert len(relevant["goals"]) == 1

    assert len(relevant["projects"]) == 1

    assert (
        relevant["goals"][0].content
        == "Learn React"
    )

    assert (
        relevant["projects"][0].content
        == "Build a React application"
    )
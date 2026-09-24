import pytest

from app.core.memory import MemoryEngine


def test_store_memory():
    memory = MemoryEngine()

    item = memory.store(
        category="goals",
        content={
            "goal": "Become a Software Engineer",
            "target": "Full Stack Development",
        },
    )

    assert item.category == "goals"

    assert item.content["goal"] == (
        "Become a Software Engineer"
    )

    assert item.source == "kie"


def test_retrieve_memory_by_category():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Learn React",
    )

    memory.store(
        category="goals",
        content="Improve DSA",
    )

    goals = memory.retrieve(
        category="goals"
    )

    assert len(goals) == 2

    assert goals[0].content == "Learn React"

    assert goals[1].content == "Improve DSA"


def test_retrieve_all_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Learn Python",
    )

    memory.store(
        category="preferences",
        content={
            "learning_style": "practical"
        },
    )

    memories = memory.retrieve()

    assert len(memories) == 2

    categories = {
        item.category
        for item in memories
    }

    assert "goals" in categories
    assert "preferences" in categories


def test_retrieve_relevant_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Become a Software Engineer",
    )

    memory.store(
        category="projects",
        content="Build a React project",
    )

    memory.store(
        category="preferences",
        content="Prefer practical learning",
    )

    relevant = memory.retrieve_relevant(
        categories=[
            "goals",
            "projects",
        ]
    )

    assert "goals" in relevant

    assert "projects" in relevant

    assert "preferences" not in relevant

    assert len(relevant["goals"]) == 1

    assert len(relevant["projects"]) == 1


def test_invalid_memory_category():
    memory = MemoryEngine()

    with pytest.raises(ValueError):
        memory.store(
            category="invalid_category",
            content="test",
        )


def test_invalid_retrieval_category():
    memory = MemoryEngine()

    with pytest.raises(ValueError):
        memory.retrieve(
            category="invalid_category"
        )


def test_clear_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Learn Python",
    )

    memory.store(
        category="projects",
        content="Build KIE",
    )

    assert len(memory.retrieve()) == 2

    memory.clear()

    assert len(memory.retrieve()) == 0


def test_memory_categories():
    memory = MemoryEngine()

    categories = memory.list_categories()

    assert len(categories) == 7

    assert "preferences" in categories
    assert "conversations" in categories
    assert "learning_history" in categories
    assert "projects" in categories
    assert "goals" in categories
    assert "achievements" in categories
    assert "friction_context" in categories
from app.core.memory import MemoryEngine


def test_users_have_isolated_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Become a Software Engineer",
        user_id="student-001",
    )

    memory.store(
        category="goals",
        content="Become a Data Scientist",
        user_id="student-002",
    )

    student_one_goals = memory.retrieve(
        category="goals",
        user_id="student-001",
    )

    student_two_goals = memory.retrieve(
        category="goals",
        user_id="student-002",
    )

    assert len(student_one_goals) == 1
    assert len(student_two_goals) == 1

    assert (
        student_one_goals[0].content
        == "Become a Software Engineer"
    )

    assert (
        student_two_goals[0].content
        == "Become a Data Scientist"
    )


def test_user_cannot_retrieve_another_users_memory():
    memory = MemoryEngine()

    memory.store(
        category="projects",
        content="Student 1 Project",
        user_id="student-001",
    )

    student_two_projects = memory.retrieve(
        category="projects",
        user_id="student-002",
    )

    assert len(student_two_projects) == 0


def test_relevant_memory_is_user_specific():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Learn React",
        user_id="student-001",
    )

    memory.store(
        category="goals",
        content="Learn Python",
        user_id="student-002",
    )

    relevant = memory.retrieve_relevant(
        categories=["goals"],
        user_id="student-001",
    )

    assert len(relevant["goals"]) == 1

    assert (
        relevant["goals"][0].content
        == "Learn React"
    )


def test_clear_only_removes_selected_user_memory():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Student 1 Goal",
        user_id="student-001",
    )

    memory.store(
        category="goals",
        content="Student 2 Goal",
        user_id="student-002",
    )

    memory.clear(
        user_id="student-001"
    )

    student_one = memory.retrieve(
        category="goals",
        user_id="student-001",
    )

    student_two = memory.retrieve(
        category="goals",
        user_id="student-002",
    )

    assert len(student_one) == 0

    assert len(student_two) == 1

    assert (
        student_two[0].content
        == "Student 2 Goal"
    )


def test_list_users():
    memory = MemoryEngine()

    memory.store(
        category="goals",
        content="Goal 1",
        user_id="student-001",
    )

    memory.store(
        category="goals",
        content="Goal 2",
        user_id="student-002",
    )

    users = memory.list_users()

    assert "student-001" in users
    assert "student-002" in users

    assert len(users) == 2
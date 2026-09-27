from app.core.service import KIEService
from app.schemas.request import KIERequest


def test_memory_persists_across_kie_requests():
    service = KIEService()

    first_request = KIERequest(
        user_id="student-001",
        session_id="session-001",
        task="Learn Python",
        planning_horizon="daily",
    )

    first_response = service.execute(
        first_request
    )

    assert first_response.status == "success"

    history = service.memory_engine.retrieve(
        category="learning_history",
        user_id="student-001",
    )

    assert len(history) == 1

    assert (
        history[0].content["task"]
        == "Learn Python"
    )

    assert (
        history[0].content["status"]
        == "completed"
    )


def test_second_request_retrieves_previous_memory():
    service = KIEService()

    first_request = KIERequest(
        user_id="student-001",
        session_id="session-001",
        task="Learn Python",
        planning_horizon="daily",
    )

    service.execute(first_request)

    second_request = KIERequest(
        user_id="student-001",
        session_id="session-002",
        task="Create my weekly learning plan",
        planning_horizon="weekly",
    )

    second_response = service.execute(
        second_request
    )

    assert second_response.status == "success"

    context = second_response.context.model_dump()

    memory = context["memory"]

    assert "learning_history" in memory

    assert len(
        memory["learning_history"]
    ) == 1

    assert (
        memory["learning_history"][0]["content"]["task"]
        == "Learn Python"
    )


def test_memory_update_metadata_is_returned():
    service = KIEService()

    request = KIERequest(
        user_id="student-002",
        session_id="session-003",
        task="Create my career roadmap",
        planning_horizon="career",
    )

    response = service.execute(request)

    assert response.status == "success"

    memory_metadata = response.metadata[
        "memory"
    ]

    assert memory_metadata["updated"] is True

    assert (
        memory_metadata["updated_category"]
        == "learning_history"
    )


def test_multiple_kie_executions_build_memory_history():
    service = KIEService()

    user_id = "student-003"

    tasks = [
        "Learn Python",
        "Build a React project",
        "Practice SQL",
    ]

    for index, task in enumerate(
        tasks,
        start=1,
    ):
        request = KIERequest(
            user_id=user_id,
            session_id=f"session-{index}",
            task=task,
            planning_horizon="daily",
        )

        response = service.execute(request)

        assert response.status == "success"

    history = service.memory_engine.retrieve(
        category="learning_history",
        user_id=user_id,
    )

    assert len(history) == 3

    stored_tasks = [
        item.content["task"]
        for item in history
    ]

    assert "Learn Python" in stored_tasks

    assert "Build a React project" in stored_tasks

    assert "Practice SQL" in stored_tasks
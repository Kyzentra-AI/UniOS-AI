from app.core.service import KIEService
from app.schemas.request import KIERequest


def test_kie_service_uses_agent_orchestrator():
    service = KIEService()

    request = KIERequest(
        user_id="orchestration-user",
        session_id="orchestration-session",
        role="student",
        task="Learn Python",
        learner_stage="final-year",
    )

    original_prepare_plan = (
        service.agent_orchestrator.prepare_plan
    )

    calls = []

    def tracked_prepare_plan(plan):
        calls.append(plan)
        return original_prepare_plan(plan)

    service.agent_orchestrator.prepare_plan = (
        tracked_prepare_plan
    )

    response = service.execute(request)

    assert response.status == "success"
    assert len(calls) == 1
    assert len(calls[0]) == len(response.plan)


def test_orchestrated_plan_reaches_execution_engine():
    service = KIEService()

    request = KIERequest(
        user_id="execution-user",
        session_id="execution-session",
        role="student",
        task="Build a Python project",
        learner_stage="final-year",
    )

    response = service.execute(request)

    assert response.status == "success"
    assert response.result["executed_steps"] > 0

    execution_details = response.result[
        "execution_details"
    ]

    assert len(execution_details) > 0

    for step in execution_details:
        assert "step_id" in step
        assert "agent" in step
        assert "result" in step
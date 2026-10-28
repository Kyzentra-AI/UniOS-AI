
from app.core.service import KIEService
from app.schemas.request import KIERequest


def test_build_action_and_artifact_type_reach_execution_plan():
    service = KIEService()

    request = KIERequest(
        user_id="build-metadata-user",
        session_id="build-metadata-session",
        role="student",
        task="Build a Python project",
        learner_stage="final-year",
        context={"artifact_type": "CODING"},
    )

    captured = {}
    original_prepare_plan = service.agent_orchestrator.prepare_plan

    def capture_plan(plan):
        captured["plan"] = plan
        return original_prepare_plan(plan)

    service.agent_orchestrator.prepare_plan = capture_plan

    response = service.execute(request)

    assert response.status == "success"
    assert "plan" in captured
    assert len(captured["plan"]) > 0

    for step in captured["plan"]:
        assert step.get("build_action") is not None
        assert step.get("artifact_type") == "CODING"

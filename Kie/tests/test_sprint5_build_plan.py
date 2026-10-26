
from app.core.build_plan import BuildPlanGenerationEngine
from app.schemas.build_plan import BuildPlanRequest


def make_request(artifact_type="CODING"):
    return BuildPlanRequest(
        project_id="project-1",
        title="Student Project",
        description="Build a student project",
        type=artifact_type,
        domain="software",
        goal="Create a working project",
        skills=["Python", "FastAPI"],
    )


def test_coding_plan_has_three_ordered_milestones():
    engine = BuildPlanGenerationEngine()

    response = engine.generate(make_request("CODING"))

    assert len(response.milestones) == 3
    assert [m.order_idx for m in response.milestones] == [1, 2, 3]
    assert all(m.tasks for m in response.milestones)


def test_research_plan_has_three_ordered_milestones():
    engine = BuildPlanGenerationEngine()

    response = engine.generate(make_request("RESEARCH"))

    assert len(response.milestones) == 3
    assert [m.order_idx for m in response.milestones] == [1, 2, 3]
    assert all(m.tasks for m in response.milestones)


def test_artifact_alias_is_supported():
    engine = BuildPlanGenerationEngine()

    response = engine.generate(make_request("SOFTWARE"))

    assert len(response.milestones) == 3
    assert "Setup" in response.milestones[0].title


def test_skills_are_included_in_coding_plan():
    engine = BuildPlanGenerationEngine()

    response = engine.generate(make_request("CODING"))

    all_task_text = " ".join(
        task.title + " " + task.description
        for milestone in response.milestones
        for task in milestone.tasks
    )

    assert "Python" in all_task_text or "FastAPI" in all_task_text


def test_empty_skills_are_supported():
    engine = BuildPlanGenerationEngine()
    request = make_request("CODING")
    request.skills = []

    response = engine.generate(request)

    assert len(response.milestones) == 3

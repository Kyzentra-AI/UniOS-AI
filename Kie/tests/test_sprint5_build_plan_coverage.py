
import pytest

from app.core.build_plan import BuildPlanGenerationEngine
from app.schemas.build_plan import BuildPlanRequest


def make_request(artifact_type):
    return BuildPlanRequest(
        project_id="project-coverage",
        title="Student Project",
        description="Build a student project",
        type=artifact_type,
        domain="software",
        goal="Create a working project",
        skills=["Python", "FastAPI"],
    )


@pytest.mark.parametrize(
    ("artifact_type", "expected_title"),
    [
        ("CODING", "Phase 1: Project Setup"),
        ("RESEARCH", "Phase 1: Research Definition"),
        ("BUSINESS", "Phase 1: Problem and Market Definition"),
        ("ANALYSIS", "Phase 1: Requirements and Data"),
        ("DESIGN", "Phase 1: Design Requirements"),
        ("UNKNOWN_TYPE", "Phase 1: Project Definition"),
    ],
)
def test_plan_uses_correct_artifact_specific_template(
    artifact_type,
    expected_title,
):
    response = BuildPlanGenerationEngine().generate(
        make_request(artifact_type)
    )

    assert response.milestones[0].title == expected_title
    assert len(response.milestones) == 3


@pytest.mark.parametrize(
    ("alias", "expected_title"),
    [
        ("CODE", "Phase 1: Project Setup"),
        ("SOFTWARE", "Phase 1: Project Setup"),
        ("DEVELOPMENT", "Phase 1: Project Setup"),
        ("BUSINESS_CASE", "Phase 1: Problem and Market Definition"),
        ("BUSINESS-CASE", "Phase 1: Problem and Market Definition"),
        ("DATA_ANALYSIS", "Phase 1: Requirements and Data"),
        ("DATA-ANALYSIS", "Phase 1: Requirements and Data"),
        ("UX", "Phase 1: Design Requirements"),
        ("UI", "Phase 1: Design Requirements"),
    ],
)
def test_artifact_aliases_use_the_expected_template(
    alias,
    expected_title,
):
    response = BuildPlanGenerationEngine().generate(
        make_request(alias)
    )

    assert response.milestones[0].title == expected_title


@pytest.mark.parametrize(
    "artifact_type",
    [
        "CODING",
        "RESEARCH",
        "BUSINESS",
        "ANALYSIS",
        "DESIGN",
        "UNKNOWN_TYPE",
    ],
)
def test_all_plans_have_ordered_milestones_and_tasks(artifact_type):
    response = BuildPlanGenerationEngine().generate(
        make_request(artifact_type)
    )

    assert [m.order_idx for m in response.milestones] == [1, 2, 3]
    assert all(m.tasks for m in response.milestones)

    for milestone in response.milestones:
        assert [task.order_idx for task in milestone.tasks] == list(
            range(1, len(milestone.tasks) + 1)
        )


@pytest.mark.parametrize(
    "artifact_type",
    [
        "CODING",
        "RESEARCH",
        "BUSINESS",
        "ANALYSIS",
        "DESIGN",
    ],
)
def test_artifact_specific_plans_include_the_project_goal(artifact_type):
    request = make_request(artifact_type)
    response = BuildPlanGenerationEngine().generate(request)

    plan_text = " ".join(
        milestone.title
        + " "
        + milestone.description
        + " "
        + " ".join(
            task.title + " " + task.description
            for task in milestone.tasks
        )
        for milestone in response.milestones
    )

    assert request.goal in plan_text


def test_skills_are_trimmed_and_duplicates_are_removed():
    request = make_request("CODING")
    request.skills = [" Python ", "FastAPI", "Python", "", "  "]

    response = BuildPlanGenerationEngine().generate(request)

    plan_text = " ".join(
        task.title + " " + task.description
        for milestone in response.milestones
        for task in milestone.tasks
    )

    assert "Python" in plan_text
    assert "FastAPI" in plan_text

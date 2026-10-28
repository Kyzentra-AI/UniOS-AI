
from app.core.collaboration import CollaborationOrchestrationEngine
from app.schemas.collaboration import CollaborationRequest


def test_collaboration_assigns_tasks_to_supplied_members():
    request = CollaborationRequest(
        challenge_title="Green Tech Challenge",
        challenge_statement="Build a prototype and present a demo.",
        challenge_type="hackathon",
        team_members=["Priya", "Alex"],
    )

    result = CollaborationOrchestrationEngine().generate(request)

    assert len(result.tasks) == 4
    assert result.tasks[0].suggested_owner == "Priya"
    assert result.tasks[1].suggested_owner == "Alex"
    assert result.tasks[1].depends_on == ["Understand requirements"]
    assert "version_control" in result.suggested_tool_categories
    assert result.coordination_checkpoints


def test_research_collaboration_suggests_research_tools():
    request = CollaborationRequest(
        challenge_title="Research Challenge",
        challenge_statement="Analyze data and evaluate evidence.",
        challenge_type="research",
        team_members=["Sam"],
    )

    result = CollaborationOrchestrationEngine().generate(request)

    assert result.tasks[2].title == "Gather and analyze evidence"
    assert "research_sources" in result.suggested_tool_categories
    assert "data_analysis" in result.suggested_tool_categories


def test_collaboration_without_members_does_not_assign_owners():
    request = CollaborationRequest(
        challenge_title="Community Challenge",
        challenge_statement="Propose a solution for a community problem.",
        challenge_type="general",
    )

    result = CollaborationOrchestrationEngine().generate(request)

    assert all(task.suggested_owner is None for task in result.tasks)
    assert any(
        "no team members" in item.lower()
        for item in result.assumptions
    )


def test_collaboration_deduplicates_members():
    request = CollaborationRequest(
        challenge_title="Design Challenge",
        challenge_statement="Create and review a design.",
        challenge_type="design",
        team_members=["Alex", "Alex", "Sam"],
    )

    result = CollaborationOrchestrationEngine().generate(request)

    assert result.tasks[0].suggested_owner == "Alex"
    assert result.tasks[1].suggested_owner == "Sam"
    assert "prototyping" in result.suggested_tool_categories

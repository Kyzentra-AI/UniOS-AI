
from app.core.competition_planning import CompetitionPlanningEngine
from app.schemas.competition_planning import CompetitionPlanningRequest


def test_hackathon_plan_contains_ordered_tasks():
    request = CompetitionPlanningRequest(
        challenge_title="Green Tech Hackathon",
        challenge_statement="Build and demonstrate a solution.",
        challenge_type="hackathon",
        deadline_days=4,
    )

    result = CompetitionPlanningEngine().generate(request)

    assert result.challenge_title == "Green Tech Hackathon"
    assert len(result.preparation_plan) == 4
    assert result.preparation_plan[0].title == "Understand the problem"
    assert result.preparation_plan[-1].title == "Prepare the demonstration"
    assert result.success_checklist


def test_research_challenge_does_not_use_coding_plan():
    request = CompetitionPlanningRequest(
        challenge_title="Research Challenge",
        challenge_statement="Analyze data and present evidence.",
        challenge_type="research",
    )

    result = CompetitionPlanningEngine().generate(request)

    assert result.preparation_plan[0].title == "Define the research question"
    assert any("evidence" in item.lower() for item in result.success_checklist)


def test_general_challenge_and_team_guidance():
    request = CompetitionPlanningRequest(
        challenge_title="Community Challenge",
        challenge_statement="Propose a solution for a community problem.",
        challenge_type="community",
        team_members=["Alex", "Sam"],
        learner_context={"skills": ["research", "communication"]},
    )

    result = CompetitionPlanningEngine().generate(request)

    assert len(result.preparation_plan) == 4
    assert any("task owners" in item.lower() for item in result.collaboration_guidance)
    assert any("general challenge workflow" in item.lower() for item in result.assumptions)


def test_deadline_must_be_positive():
    try:
        CompetitionPlanningRequest(
            challenge_title="Test",
            challenge_statement="Complete the challenge.",
            deadline_days=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected zero-day deadline to be rejected")

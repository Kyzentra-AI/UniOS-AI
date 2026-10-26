
from app.core.build_coach import BuildCoachEngine
from app.schemas.build_coach import (
    BuildCoachRequest,
    BuildCoachResponse,
)


def test_build_coach_help_stuck_returns_troubleshooting_guidance():
    request = BuildCoachRequest(
        intent="help_stuck",
        message="My API request is failing",
        context={"current_file": "App.jsx"},
        project_context={"title": "Task Manager"},
    )

    response = BuildCoachEngine().generate(request)

    assert isinstance(response, BuildCoachResponse)
    assert "Task Manager" in response.reply
    assert "App.jsx" in response.reply
    assert "Network tab" in response.reply
    assert response.suggestions
    assert response.action_items


def test_build_coach_general_intent_returns_general_guidance():
    request = BuildCoachRequest(
        intent="continue",
        message="What should I do next?",
        project_context={"title": "Portfolio Website"},
    )

    response = BuildCoachEngine().generate(request)

    assert "Portfolio Website" in response.reply
    assert response.suggestions
    assert response.action_items


def test_build_coach_includes_project_skills_in_suggestions():
    request = BuildCoachRequest(
        intent="help_stuck",
        message="I need help",
        project_context={
            "title": "Task Manager",
            "skills": ["Python", "FastAPI"],
        },
    )

    response = BuildCoachEngine().generate(request)

    assert any(
        "Python" in suggestion and "FastAPI" in suggestion
        for suggestion in response.suggestions
    )


def test_build_coach_uses_default_project_title_when_missing():
    request = BuildCoachRequest(
        intent="help_stuck",
        message="I am stuck",
    )

    response = BuildCoachEngine().generate(request)

    assert "your project" in response.reply

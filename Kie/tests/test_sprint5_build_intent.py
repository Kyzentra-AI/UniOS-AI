
import pytest

from app.core.intent import IntentEngine


@pytest.mark.parametrize(
    ("task", "expected_action"),
    [
        ("Create a project for my portfolio", "create"),
        ("Plan my project milestones", "plan"),
        ("Review my project", "review"),
        ("Debug my application", "debug"),
        ("Improve my project", "improve"),
        ("Write documentation for my project", "document"),
        ("Prepare a presentation for my project", "present"),
    ],
)
def test_build_actions_are_recognized(task, expected_action):
    result = IntentEngine().recognize(task)

    assert result.name == "BUILD"
    assert result.build_action == expected_action
    assert result.confidence > 0


@pytest.mark.parametrize(
    ("task", "expected_action"),
    [
        ("Prepare slides about my project", "present"),
        ("Generate a README for my application", "document"),
        ("Find the bug in my application", "debug"),
        ("Refactor my project", "improve"),
    ],
)
def test_common_build_phrasings_are_recognized(task, expected_action):
    result = IntentEngine().recognize(task)

    assert result.name == "BUILD"
    assert result.build_action == expected_action

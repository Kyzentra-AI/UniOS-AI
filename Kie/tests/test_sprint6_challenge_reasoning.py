
from app.core.challenge_reasoning import analyze_challenge
from app.schemas.challenge_reasoning import ChallengeReasoningRequest


def test_analyze_challenge_extracts_requirements_and_deliverables():
    request = ChallengeReasoningRequest(
        challenge_title="Clean Water Challenge",
        challenge_statement=(
            "Develop a prototype to monitor water quality. "
            "Present the findings. Submit the final solution."
        ),
        challenge_type="general",
    )

    result = analyze_challenge(request)

    assert result.challenge_title == "Clean Water Challenge"
    assert result.challenge_type == "general"
    assert len(result.requirements) == 3
    assert any("prototype" in item.lower() for item in result.suggested_deliverables)
    assert any("presentation" in item.lower() for item in result.suggested_deliverables)
    assert any("submission" in item.lower() for item in result.suggested_deliverables)


def test_analysis_supports_non_coding_challenge_types():
    request = ChallengeReasoningRequest(
        challenge_title="Research Challenge",
        challenge_statement="Investigate the problem and summarize the evidence.",
        challenge_type="research",
    )

    result = analyze_challenge(request)

    assert result.challenge_type == "research"
    assert any("findings" in item.lower() for item in result.suggested_deliverables)
    assert any("research" in item.lower() for item in result.assumptions)


def test_analysis_handles_empty_learner_context():
    request = ChallengeReasoningRequest(
        challenge_title="General Challenge",
        challenge_statement="Solve the stated problem.",
    )

    result = analyze_challenge(request)

    assert result.requirements
    assert result.suggested_deliverables
    assert any("learner-specific context" in item.lower() for item in result.assumptions)

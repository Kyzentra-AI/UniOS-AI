
from app.schemas.challenge_reasoning import (
    ChallengeReasoningRequest,
    ChallengeReasoningResponse,
    ChallengeRequirement,
)


def analyze_challenge(
    request: ChallengeReasoningRequest,
) -> ChallengeReasoningResponse:
    title = request.challenge_title.strip()
    statement = request.challenge_statement.strip()
    challenge_type = request.challenge_type.strip().lower()

    text = statement.lower()
    context = request.learner_context or {}

    requirements = []
    assumptions = []
    deliverables = []

    # Extract actionable requirements from the challenge statement.
    sentences = [
        part.strip(" \t\r\n.-")
        for part in statement.replace("\n", ".").split(".")
        if part.strip(" \t\r\n.-")
    ]

    for sentence in sentences:
        requirements.append(
            ChallengeRequirement(
                requirement=sentence,
                priority="high" if any(
                    keyword in sentence.lower()
                    for keyword in ("must", "required", "ensure", "need to")
                ) else "medium",
            )
        )

    if not requirements:
        requirements.append(
            ChallengeRequirement(
                requirement="Clarify the challenge objectives and success criteria.",
                priority="high",
            )
        )

    # Keep recommendations universal rather than assuming every challenge
    # is a coding hackathon.
    if any(word in text for word in ("prototype", "build", "develop", "implement", "application")):
        deliverables.append("A working solution or prototype that addresses the stated problem.")

    if any(word in text for word in ("presentation", "pitch", "demo", "present")):
        deliverables.append("A presentation or demonstration explaining the solution.")

    if any(word in text for word in ("research", "analyse", "analyze", "investigate", "study")):
        deliverables.append("A summary of findings, evidence, and conclusions.")

    if any(word in text for word in ("submit", "submission", "deadline", "deliver")):
        deliverables.append("A final submission prepared according to the stated requirements and deadline.")

    if not deliverables:
        deliverables.append("A completed outcome that directly addresses the challenge requirements.")

    if challenge_type in {"hackathon", "coding", "software"}:
        assumptions.append("A technical solution may be appropriate; confirm the challenge rules before choosing an approach.")
    elif challenge_type in {"research", "academic"}:
        assumptions.append("Evidence and clear reasoning may be important; confirm the expected research format.")
    elif challenge_type in {"business", "startup", "entrepreneurship"}:
        assumptions.append("Feasibility and impact may be relevant; confirm the judging criteria.")
    else:
        assumptions.append("The challenge format and judging criteria were not fully specified.")

    if not context:
        assumptions.append("No learner-specific context was provided; the analysis is based on the challenge statement alone.")
    else:
        assumptions.append("Learner context was supplied but should be validated before personalizing the preparation plan.")

    return ChallengeReasoningResponse(
        challenge_title=title,
        challenge_type=challenge_type,
        problem_summary=statement,
        requirements=requirements,
        suggested_deliverables=deliverables,
        assumptions=assumptions,
    )

from app.core.context import ContextEngine
from app.core.identity import IdentityEngine
from app.schemas.request import KIERequest


def test_identity_engine_resolves_identity():
    request = KIERequest(
        user_id="user-100",
        session_id="session-100",
        role="student",
        task="Learn Python",
    )

    engine = IdentityEngine()

    identity = engine.resolve(request)

    assert identity == {
        "user_id": "user-100",
        "session_id": "session-100",
        "role": "student",
    }


def test_context_engine_resolves_context():
    request = KIERequest(
        user_id="user-100",
        session_id="session-100",
        role="student",
        task="Learn Python",
        context={
            "topic": "Python",
            "current_goal": "Learn programming",
        },
        learner_stage="beginner",
        learner_profile={
            "education_level": "Bachelor's",
            "career_goal": "Software Engineer",
            "skills": ["Python", "JavaScript"],
            "learning_style": "visual",
        },
    )

    engine = ContextEngine()

    context = engine.resolve(request)

    assert context["current_context"]["topic"] == "Python"
    assert context["current_context"]["current_goal"] == "Learn programming"

    assert context["learner_stage"] == "beginner"

    assert context["learner_profile"]["education_level"] == "Bachelor's"
    assert context["learner_profile"]["career_goal"] == "Software Engineer"
    assert context["learner_profile"]["skills"] == [
        "Python",
        "JavaScript",
    ]
    assert context["learner_profile"]["learning_style"] == "visual"

    assert context["task"] == "Learn Python"

    assert context["sources"]["current_context"] == "request"
    assert context["sources"]["learner_stage"] == "request"
    assert context["sources"]["learner_profile"] == "request"
    assert context["sources"]["task"] == "request"
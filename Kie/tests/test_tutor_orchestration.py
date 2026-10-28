from app.core.tutor import TutorOrchestrator


def test_explain_routes_to_tutor_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="explain",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "tutor"
    assert result["agent"] == "TutorAgent"


def test_teach_routes_to_tutor_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="teach",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "tutor"
    assert result["agent"] == "TutorAgent"


def test_practice_routes_to_practice_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="practice",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "practice"
    assert result["agent"] == "PracticeAgent"


def test_assess_routes_to_assessment_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="assess",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "assessment"
    assert result["agent"] == "AssessmentAgent"


def test_revise_routes_to_tutor_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="revise",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "tutor"
    assert result["agent"] == "TutorAgent"


def test_summarize_routes_to_tutor_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="summarize",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "tutor"
    assert result["agent"] == "TutorAgent"


def test_continue_learning_routes_to_tutor_agent():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="continue-learning",
    )

    assert result["status"] == "routed"
    assert result["capability"] == "tutor"
    assert result["agent"] == "TutorAgent"


def test_tutor_receives_current_topic():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="explain",
        learner_context={
            "current_topic": "Recursion",
        },
    )

    assert (
        result["context"]["current_topic"]
        == "Recursion"
    )


def test_tutor_receives_current_lesson():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="teach",
        learner_context={
            "current_lesson": "Data Structures",
        },
    )

    assert (
        result["context"]["current_lesson"]
        == "Data Structures"
    )


def test_tutor_receives_learner_profile():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="explain",
        learner_profile={
            "knowledge_level": "beginner",
            "learning_style": "visual",
            "career_goal": "Software Engineer",
        },
    )

    assert (
        result["context"]["knowledge_level"]
        == "beginner"
    )

    assert (
        result["context"]["learning_style"]
        == "visual"
    )

    assert (
        result["context"]["career_goal"]
        == "Software Engineer"
    )


def test_tutor_context_combines_learning_context():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="teach",
        learner_context={
            "current_lesson": "Python Basics",
            "current_topic": "Functions",
            "learning_session_id": "session-123",
        },
        learner_profile={
            "knowledge_level": "beginner",
            "learning_style": "example-first",
        },
    )

    context = result["context"]

    assert context["current_lesson"] == "Python Basics"
    assert context["current_topic"] == "Functions"
    assert (
        context["learning_session_id"]
        == "session-123"
    )
    assert context["knowledge_level"] == "beginner"
    assert (
        context["learning_style"]
        == "example-first"
    )


def test_unknown_learning_action_is_not_routed():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action="unknown-action",
    )

    assert result["status"] == "unsupported"
    assert result["capability"] is None
    assert result["agent"] is None


def test_missing_learning_action_is_unresolved():
    orchestrator = TutorOrchestrator()

    result = orchestrator.route(
        learning_action=None,
    )

    assert result["status"] == "unresolved"
    assert result["capability"] is None
    assert result["agent"] is None
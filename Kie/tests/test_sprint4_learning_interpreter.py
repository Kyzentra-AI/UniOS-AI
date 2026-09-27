from app.core.intent import IntentEngine


def test_explain_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Explain recursion to me"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "explain"


def test_teach_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Teach me Python decorators"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "teach"


def test_practice_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Give me recursion problems to practice"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "practice"


def test_revise_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Help me revise DBMS"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "revise"


def test_assess_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Quiz me on Python"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "assess"


def test_summarize_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Summarize operating systems"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "summarize"


def test_continue_learning_request():
    engine = IntentEngine()

    result = engine.recognize(
        "Continue my previous lesson"
    )

    assert result.name == "LEARN"
    assert result.learning_action == "continue-learning"


def test_general_learning_request():
    engine = IntentEngine()

    result = engine.recognize(
        "I want to learn Python"
    )

    assert result.name == "LEARN"
    assert result.learning_action is None


def test_existing_build_intent_is_preserved():
    engine = IntentEngine()

    result = engine.recognize(
        "Build a React project"
    )

    assert result.name == "BUILD"


def test_existing_compete_intent_is_preserved():
    engine = IntentEngine()

    result = engine.recognize(
        "Help me prepare for a hackathon"
    )

    assert result.name == "COMPETE"


def test_existing_launch_intent_is_preserved():
    engine = IntentEngine()

    result = engine.recognize(
        "Help me prepare my resume"
    )

    assert result.name == "LAUNCH"


def test_existing_general_intent_is_preserved():
    engine = IntentEngine()

    result = engine.recognize(
        "What is the weather?"
    )

    assert result.name == "GENERAL"
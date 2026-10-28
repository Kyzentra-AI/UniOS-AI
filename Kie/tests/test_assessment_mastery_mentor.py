
import pytest
from pydantic import ValidationError

from app.core.assessment import AssessmentGenerationEngine
from app.core.mastery import MasteryEvaluationEngine
from app.core.mentor import MentorChatEngine
from app.schemas.assessment import AssessmentGenerateRequest
from app.schemas.mastery import MasteryEvaluateRequest
from app.schemas.mentor import MentorChatRequest


def assessment_request(**overrides):
    data = {
        "learner_id": "learner-101",
        "session_id": "session-101",
        "lesson_id": "lesson-101",
        "topic": "Python functions",
        "preferred_type": "mcq",
        "question_count": 5,
        "difficulty": "DEVELOPING",
    }
    data.update(overrides)
    return AssessmentGenerateRequest(**data)


def test_assessment_generates_requested_number_of_questions():
    result = AssessmentGenerationEngine().generate(
        assessment_request(question_count=3)
    )

    assert len(result.questions) == 3
    assert result.rubric.total_points == 3.0


def test_assessment_question_and_option_ids_are_stable():
    engine = AssessmentGenerationEngine()
    request = assessment_request(question_count=2)

    first = engine.generate(request)
    second = engine.generate(request)

    assert [q.id for q in first.questions] == ["q1", "q2"]
    assert [q.id for q in first.questions] == [
        q.id for q in second.questions
    ]
    for question in first.questions:
        assert question.correct_option_id in {
            option.id for option in question.options
        }


def test_assessment_rejects_question_count_above_limit():
    with pytest.raises(ValidationError):
        assessment_request(question_count=31)


def test_assessment_rejects_blank_topic():
    with pytest.raises(ValidationError):
        assessment_request(topic="   ")


def test_mastery_without_answer_keys_does_not_claim_correctness():
    request = MasteryEvaluateRequest(
        learner_id="learner-101",
        assessment_id="assessment-101",
        topic="Python",
        answers=[
            {
                "question_id": "q1",
                "answer": "A",
            }
        ],
    )

    result = MasteryEvaluationEngine().evaluate(request)

    assert result.score == 0.0
    assert len(result.question_evaluations) == 1
    assert "answer key" in result.question_evaluations[0].feedback.lower()
    assert "rubric" in result.feedback.lower()


def test_mastery_rejects_empty_answers():
    with pytest.raises(ValidationError):
        MasteryEvaluateRequest(
            learner_id="learner-101",
            assessment_id="assessment-101",
            topic="Python",
            answers=[],
        )


@pytest.mark.parametrize(
    "mode",
    ["tutor", "study-coach", "accountability", "motivation"],
)
def test_mentor_supports_all_modes(mode):
    request = MentorChatRequest(
        learner_id="learner-101",
        mode=mode,
        message="Help me learn Python functions",
        context={"topic": "Python functions"},
    )

    result = MentorChatEngine().generate(request)

    assert result.reply.strip()
    assert "Python functions" in result.reply


def test_mentor_rejects_unknown_mode():
    with pytest.raises(ValidationError):
        MentorChatRequest(
            learner_id="learner-101",
            mode="unknown",
            message="Help me study",
        )

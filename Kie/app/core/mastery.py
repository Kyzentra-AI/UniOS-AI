
from app.schemas.mastery import (
    MasteryEvaluateRequest,
    MasteryEvaluateResponse,
    QuestionEvaluation,
    MasteryTopicUpdate,
)


class MasteryEvaluationEngine:
    """Contract-compatible baseline evaluator.

    Production integration must evaluate answers against the assessment's
    persisted answer keys and grading rubrics supplied by the backend.
    """

    def evaluate(
        self,
        request: MasteryEvaluateRequest,
    ) -> MasteryEvaluateResponse:
        evaluations = []

        for answer in request.answers:
            # Without answer keys/rubrics, correctness cannot be established.
            evaluations.append(
                QuestionEvaluation(
                    question_id=answer.question_id,
                    is_correct=False,
                    score=0.0,
                    feedback=(
                        "Evaluation requires the saved answer key or grading "
                        "rubric for this question. No correctness was assumed."
                    ),
                )
            )

        return MasteryEvaluateResponse(
            score=0.0,
            feedback=(
                "Answers were received, but a verified mastery score requires "
                "the assessment answer keys and grading rubrics."
            ),
            question_evaluations=evaluations,
            mastery_updates={
                request.topic: {
                    "Pending evaluation": MasteryTopicUpdate(
                        score=0.0,
                        status="NOVICE",
                        delta=0.0,
                        reason=(
                            "No answer key or rubric was provided to verify "
                            "the submitted answers."
                        ),
                    )
                }
            },
        )

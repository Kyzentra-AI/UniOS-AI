
from app.schemas.assessment import (
    AssessmentGenerateRequest,
    AssessmentGenerateResponse,
    AssessmentQuestion,
    AssessmentOption,
    AssessmentRubric,
)


class AssessmentGenerationEngine:
    """Generate deterministic assessments with server-side answer keys."""

    def generate(
        self,
        request: AssessmentGenerateRequest,
    ) -> AssessmentGenerateResponse:
        questions = []

        for index in range(1, request.question_count + 1):
            question_id = f"q{index}"

            if request.preferred_type == "mcq":
                question = AssessmentQuestion(
                    id=question_id,
                    type="mcq",
                    question=(
                        f"{request.topic}: practice question {index}. "
                        "Which option best describes the key concept?"
                    ),
                    options=[
                        AssessmentOption(
                            id=f"{question_id}-opt-1",
                            text=f"Correct concept for {request.topic}",
                        ),
                        AssessmentOption(
                            id=f"{question_id}-opt-2",
                            text="An unrelated concept",
                        ),
                        AssessmentOption(
                            id=f"{question_id}-opt-3",
                            text="An incorrect interpretation",
                        ),
                        AssessmentOption(
                            id=f"{question_id}-opt-4",
                            text="None of these explanations",
                        ),
                    ],
                    correct_option_id=f"{question_id}-opt-1",
                    explanation=(
                        "Option 1 is the configured answer for this "
                        "deterministic fallback question."
                    ),
                )
            else:
                question = AssessmentQuestion(
                    id=question_id,
                    type=request.preferred_type,
                    question=(
                        f"Explain or demonstrate a key concept in "
                        f"{request.topic}. Include reasoning and an example."
                    ),
                    rubric={
                        "required_criteria": [
                            "Conceptual correctness",
                            "Clear explanation",
                            "Relevant example",
                        ],
                        "ideal_solution": (
                            f"A correct explanation of {request.topic} "
                            "with reasoning and a relevant example."
                        ),
                    },
                    code=(
                        f"# Practice task for {request.topic}\n"
                        "# Write your solution here."
                        if request.preferred_type == "coding"
                        else None
                    ),
                    language=(
                        "python"
                        if request.preferred_type == "coding"
                        else None
                    ),
                )

            questions.append(question)

        return AssessmentGenerateResponse(
            title=f"{request.topic} Assessment",
            type=request.preferred_type,
            instructions="Answer all questions.",
            questions=questions,
            rubric=AssessmentRubric(
                total_points=float(request.question_count),
                passing_threshold=0.70,
            ),
        )

from app.schemas.response import IntentResult


class IntentEngine:
    """
    KIE Intent Engine.

    Identifies the primary intent of a learner request
    so the Planning Engine and Agent Orchestrator can
    select the appropriate execution path.
    """

    def recognize(self, task: str) -> IntentResult:
        task_lower = task.lower()

        if any(
            word in task_lower
            for word in [
                "learn",
                "explain",
                "teach",
            ]
        ):
            intent = "LEARN"

        elif any(
            word in task_lower
            for word in [
                "build",
                "code",
                "debug",
                "develop",
                "project",
            ]
        ):
            intent = "BUILD"

        elif any(
            word in task_lower
            for word in [
                "competition",
                "hackathon",
            ]
        ):
            intent = "COMPETE"

        elif any(
            word in task_lower
            for word in [
                "resume",
                "interview",
                "job",
                "career",
                "placement",
                "career roadmap",
            ]
        ):
            intent = "LAUNCH"

        else:
            intent = "GENERAL"

        return IntentResult(
            name=intent,
            confidence=0.80,
        )
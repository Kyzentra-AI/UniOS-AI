from app.schemas.response import IntentResult


class IntentEngine:
    """
    Basic intent recognition engine for Sprint 1.

    This is the initial KIE foundation.
    A model-based intent classifier can replace this
    implementation in a later sprint.
    """

    def recognize(self, task: str) -> IntentResult:
        task_lower = task.lower()

        if any(word in task_lower for word in ["learn", "explain", "teach"]):
            intent = "LEARN"

        elif any(word in task_lower for word in ["build", "code", "debug"]):
            intent = "BUILD"

        elif any(word in task_lower for word in ["competition", "hackathon"]):
            intent = "COMPETE"

        elif any(word in task_lower for word in ["resume", "interview", "job"]):
            intent = "LAUNCH"

        else:
            intent = "GENERAL"

        return IntentResult(
            name=intent,
            confidence=0.80,
        )
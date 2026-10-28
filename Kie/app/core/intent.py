from app.schemas.response import IntentResult


class IntentEngine:
    """
    KIE Intent Engine.

    Identifies the primary capability required for a
    learner request and, for learning requests, identifies
    the requested learning action.

    Sprint 4 learning actions:
    - explain
    - teach
    - practice
    - revise
    - assess
    - summarize
    - continue-learning
    """

    LEARNING_ACTIONS = {
        "explain",
        "teach",
        "practice",
        "revise",
        "assess",
        "summarize",
        "continue-learning",
    }

    def recognize(
        self,
        task: str,
    ) -> IntentResult:
        task_lower = task.lower().strip()

        learning_action = self._detect_learning_action(
            task_lower
        )

        if learning_action is not None:
            return IntentResult(
                name="LEARN",
                confidence=0.90,
                learning_action=learning_action,
            )

        if any(
            word in task_lower
            for word in [
                "learn",
                "learning",
                "study",
            ]
        ):
            return IntentResult(
                name="LEARN",
                confidence=0.80,
                learning_action=None,
            )

        if any(
            word in task_lower
            for word in [
                "build",
                "code",
                "debug",
                "develop",
                "project",
            ]
        ):
            return IntentResult(
                name="BUILD",
                confidence=0.80,
            )

        if any(
            word in task_lower
            for word in [
                "competition",
                "hackathon",
            ]
        ):
            return IntentResult(
                name="COMPETE",
                confidence=0.80,
            )

        if any(
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
            return IntentResult(
                name="LAUNCH",
                confidence=0.80,
            )

        return IntentResult(
            name="GENERAL",
            confidence=0.80,
        )

    def _detect_learning_action(
        self,
        task: str,
    ) -> str | None:
        """
        Detect the specific Sprint 4 learning action.
        """

        # --------------------------------------------------
        # CONTINUE LEARNING
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "continue learning",
                "continue where i left off",
                "continue from where i left off",
                "continue my previous lesson",
                "continue my previous learning",
                "continue my lesson",
                "continue my learning",
                "pick up where i left off",
                "resume learning",
                "resume my lesson",
                "resume my previous lesson",
            ]
        ):
            return "continue-learning"

        # --------------------------------------------------
        # PRACTICE
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "practice",
                "give me exercises",
                "give me problems",
                "give me questions",
                "let me practice",
            ]
        ):
            return "practice"

        # --------------------------------------------------
        # ASSESS
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "assess me",
                "test me",
                "quiz me",
                "evaluate me",
                "assessment",
                "take a test",
            ]
        ):
            return "assess"

        # --------------------------------------------------
        # REVISE
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "revise",
                "revision",
                "review",
                "help me revise",
                "help me review",
            ]
        ):
            return "revise"

        # --------------------------------------------------
        # SUMMARIZE
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "summarize",
                "summary",
                "give me a summary",
                "summarise",
                "summarisation",
            ]
        ):
            return "summarize"

        # --------------------------------------------------
        # EXPLAIN
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "explain",
                "explain to me",
                "how does",
                "how do",
                "why does",
                "why do",
            ]
        ):
            return "explain"

        # --------------------------------------------------
        # TEACH
        # --------------------------------------------------

        if any(
            phrase in task
            for phrase in [
                "teach me",
                "teach",
                "learn about",
                "help me learn",
            ]
        ):
            return "teach"

        return None
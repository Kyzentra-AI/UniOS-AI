
from app.schemas.response import IntentResult


class IntentEngine:
    """Recognize learning, build, competition, career, and general intents."""

    LEARNING_ACTIONS = {
        "explain", "teach", "practice", "revise",
        "assess", "summarize", "continue-learning",
    }

    BUILD_ACTIONS = {
        "create", "plan", "review", "debug",
        "improve", "document", "present",
    }

    def recognize(self, task: str) -> IntentResult:
        task_lower = task.lower().strip()

        # Preserve existing Sprint 3 roadmap behavior.
        if "roadmap" in task_lower:
            if any(
                word in task_lower
                for word in ["learning", "learn", "study", "weekly"]
            ):
                return IntentResult(
                    name="LEARN",
                    confidence=0.80,
                    learning_action=None,
                )

            if (
                "career" in task_lower
                and "create a roadmap for becoming" not in task_lower
            ):
                return IntentResult(
                    name="LAUNCH",
                    confidence=0.80,
                )

            return IntentResult(
                name="GENERAL",
                confidence=0.80,
            )

        # Handle explicit career planning requests.
        if any(
            phrase in task_lower
            for phrase in [
                "career plan",
                "plan my career",
                "career planning",
            ]
        ):
            return IntentResult(
                name="LAUNCH",
                confidence=0.80,
            )

        # Career and resume requests must route to LAUNCH.
        # Projects created for a portfolio remain BUILD.
        if (
            any(
                word in task_lower
                for word in [
                    "resume",
                    "interview",
                    "job",
                    "career",
                    "placement",
                ]
            )
            or (
                "portfolio" in task_lower
                and "project" not in task_lower
            )
        ):
            return IntentResult(
                name="LAUNCH",
                confidence=0.90,
            )

        # Detect Build actions.
        build_action = self._detect_build_action(task_lower)

        if build_action is not None:
            return IntentResult(
                name="BUILD",
                confidence=0.90,
                build_action=build_action,
            )

        # Detect learning actions.
        learning_action = self._detect_learning_action(task_lower)

        if learning_action is not None:
            return IntentResult(
                name="LEARN",
                confidence=0.90,
                learning_action=learning_action,
            )

        if any(
            word in task_lower
            for word in ["learn", "learning", "study"]
        ):
            return IntentResult(
                name="LEARN",
                confidence=0.80,
                learning_action=None,
            )

        if any(
            word in task_lower
            for word in [
                "build", "code", "debug", "develop",
                "project", "application", "implement", "program",
            ]
        ):
            return IntentResult(
                name="BUILD",
                confidence=0.80,
            )

        if any(
            word in task_lower
            for word in ["competition", "hackathon"]
        ):
            return IntentResult(
                name="COMPETE",
                confidence=0.80,
            )

        return IntentResult(
            name="GENERAL",
            confidence=0.80,
        )

    def _detect_build_action(self, task: str) -> str | None:

        # DEBUG
        if any(
            phrase in task
            for phrase in [
                "debug", "debugging", "fix my code",
                "fix this code", "find the bug", "find bugs",
                "solve this error", "fix this error", "troubleshoot",
            ]
        ):
            return "debug"

        # REVIEW
        if any(
            phrase in task
            for phrase in [
                "review my project", "review this project",
                "review the project", "review my code",
                "review this code", "review the code",
                "review my application", "review this application",
                "review the application", "code review",
            ]
        ):
            return "review"

        # IMPROVE
        if any(
            phrase in task
            for phrase in [
                "improve my project", "improve this project",
                "improve the project", "improve my code",
                "improve this code", "improve my application",
                "optimize my project", "optimize my code",
                "optimize this", "refactor my code",
                "refactor this", "refactor my project",
                "refactor the project", "refactor my application",
                "refactor the application",
            ]
        ):
            return "improve"

        # DOCUMENT
        if any(
            phrase in task
            for phrase in [
                "document my project", "document this project",
                "document my code", "write documentation",
                "create documentation", "generate documentation",
                "write a readme", "create a readme",
                "generate a readme", "make a readme",
                "write readme", "create readme", "generate readme",
                "documentation for my project",
                "documentation for my application",
            ]
        ):
            return "document"

        # PRESENT
        if any(
            phrase in task
            for phrase in [
                "present my project", "present this project",
                "present my application", "prepare my presentation",
                "prepare a presentation", "create a presentation",
                "make a presentation", "demo my project",
                "prepare a demo", "prepare slides", "create slides",
                "make slides", "generate slides",
                "presentation for my project",
                "presentation for my application",
            ]
        ):
            return "present"

        # PLAN a software project.
        if any(
            phrase in task
            for phrase in [
                "plan my project", "plan this project",
                "plan the project", "plan my application",
                "create a project plan", "make a project plan",
                "project plan", "plan the work",
                "plan my milestones", "plan project milestones",
            ]
        ):
            return "plan"

        # CREATE a software project.
        if any(
            phrase in task
            for phrase in [
                "create a project", "create my project",
                "build a project", "build my project",
                "build a python project", "build a coding project",
                "start a project", "start my project",
                "develop a project", "develop my project",
                "create an application", "build an application",
                "develop an application",
            ]
        ):
            return "create"

        return None

    def _detect_learning_action(self, task: str) -> str | None:

        if any(
            phrase in task
            for phrase in [
                "continue learning", "continue where i left off",
                "continue from where i left off",
                "continue my previous lesson",
                "continue my previous learning", "continue my lesson",
                "continue my learning", "pick up where i left off",
                "resume learning", "resume my lesson",
                "resume my previous lesson",
            ]
        ):
            return "continue-learning"

        if any(
            phrase in task
            for phrase in [
                "practice", "give me exercises", "give me problems",
                "give me questions", "let me practice",
            ]
        ):
            return "practice"

        if any(
            phrase in task
            for phrase in [
                "assess me", "test me", "quiz me",
                "evaluate me", "assessment", "take a test",
            ]
        ):
            return "assess"

        if any(
            phrase in task
            for phrase in [
                "revise", "revision", "help me revise", "help me review",
            ]
        ):
            return "revise"

        if any(
            phrase in task
            for phrase in [
                "summarize", "summary", "give me a summary",
                "summarise", "summarisation",
            ]
        ):
            return "summarize"

        if any(
            phrase in task
            for phrase in [
                "explain", "explain to me", "how does",
                "how do", "why does", "why do",
            ]
        ):
            return "explain"

        if any(
            phrase in task
            for phrase in [
                "teach me", "teach", "learn about", "help me learn",
            ]
        ):
            return "teach"

        return None

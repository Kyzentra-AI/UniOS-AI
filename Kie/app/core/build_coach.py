from app.schemas.build_coach import (
    BuildCoachActionItem,
    BuildCoachRequest,
    BuildCoachResponse,
)


class BuildCoachEngine:
    """
    Sprint 5 — Build Coach.

    Provides structured guidance for a learner who is
    working on a project and needs help progressing.

    Backend remains responsible for persistence and
    project state.
    """

    def generate(
        self,
        request: BuildCoachRequest,
    ) -> BuildCoachResponse:

        message = request.message.strip()
        intent = request.intent.strip().lower()

        if intent == "help_stuck":
            reply = self._build_stuck_reply(request)
        else:
            reply = self._build_general_reply(request)

        suggestions = self._build_suggestions(request)

        action_items = [
            BuildCoachActionItem(
                type="DOCUMENTATION_LINK",
                label="Review the relevant project documentation",
                url=None,
            )
        ]

        return BuildCoachResponse(
            reply=reply,
            suggestions=suggestions,
            action_items=action_items,
        )

    def _build_stuck_reply(
        self,
        request: BuildCoachRequest,
    ) -> str:

        project_title = request.project_context.get(
            "title",
            "your project",
        )

        current_file = request.context.get(
            "current_file",
        )

        file_text = (
            f" in `{current_file}`"
            if current_file
            else ""
        )

        return (
            f"Let's troubleshoot the issue in {project_title}"
            f"{file_text}. "
            f"First, isolate the failing request and check "
            f"the browser console and Network tab. "
            f"Then verify the API URL, CORS configuration, "
            f"HTTP method, and request headers. "
            f"After fixing the configuration, retry the request "
            f"and confirm the response status."
        )

    def _build_general_reply(
        self,
        request: BuildCoachRequest,
    ) -> str:

        project_title = request.project_context.get(
            "title",
            "your project",
        )

        return (
            f"For {project_title}, break the current task into "
            f"small steps, implement one change at a time, "
            f"and validate the result before moving forward."
        )

    def _build_suggestions(
        self,
        request: BuildCoachRequest,
    ) -> list[str]:

        suggestions = [
            "Check the browser console for the exact error.",
            "Inspect the failing request in the Network tab.",
            "Verify the API endpoint and request headers.",
        ]

        skills = request.project_context.get(
            "skills",
            [],
        )

        if skills:
            suggestions.append(
                "Review the relevant project technology: "
                + ", ".join(str(skill) for skill in skills)
                + "."
            )

        return suggestions
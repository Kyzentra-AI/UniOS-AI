from typing import Any

from app.schemas.request import KIERequest


class ContextEngine:
    """
    Sprint 2 Context Engine.

    Builds a normalized and traceable context for KIE
    from identity, learner information, current context,
    and the active task.
    """

    def resolve(self, request: KIERequest) -> dict[str, Any]:
        current_context = dict(request.context)

        return {
            "current_context": current_context,
            "learner_stage": request.learner_stage,
            "learner_profile": request.learner_profile.model_dump(),
            "task": request.task,
            "sources": {
                "current_context": "request",
                "learner_stage": "request",
                "learner_profile": "request",
                "task": "request",
            },
        }
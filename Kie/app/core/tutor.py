from typing import Any


class TutorOrchestrator:
    """
    Sprint 4 Tutor Orchestration Engine.

    Routes learning requests to the appropriate KIE
    capability/agent based on the detected learning action.

    The orchestrator does not generate learning content.
    It determines which capability should handle the
    request and passes the relevant learner context.
    """

    ACTION_TO_CAPABILITY = {
        "explain": "tutor",
        "teach": "tutor",
        "practice": "practice",
        "revise": "tutor",
        "assess": "assessment",
        "summarize": "tutor",
        "continue-learning": "tutor",
    }

    CAPABILITY_TO_AGENT = {
        "tutor": "TutorAgent",
        "practice": "PracticeAgent",
        "assessment": "AssessmentAgent",
    }

    def route(
        self,
        learning_action: str | None,
        learner_context: dict[str, Any] | None = None,
        learner_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Route a learning request to the appropriate
        KIE capability and agent.

        Returns a structured orchestration decision.
        """

        context = learner_context or {}
        profile = learner_profile or {}

        if learning_action is None:
            return {
                "status": "unresolved",
                "capability": None,
                "agent": None,
                "context": self._build_tutor_context(
                    context,
                    profile,
                ),
            }

        capability = self.ACTION_TO_CAPABILITY.get(
            learning_action
        )

        if capability is None:
            return {
                "status": "unsupported",
                "capability": None,
                "agent": None,
                "learning_action": learning_action,
                "context": self._build_tutor_context(
                    context,
                    profile,
                ),
            }

        agent = self.CAPABILITY_TO_AGENT.get(
            capability
        )

        return {
            "status": "routed",
            "learning_action": learning_action,
            "capability": capability,
            "agent": agent,
            "context": self._build_tutor_context(
                context,
                profile,
            ),
        }

    def _build_tutor_context(
        self,
        learner_context: dict[str, Any],
        learner_profile: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the minimal learner context required
        by the tutor/orchestrated capability.
        """

        return {
            "current_lesson": learner_context.get(
                "current_lesson"
            ),
            "current_topic": learner_context.get(
                "current_topic"
            ),
            "roadmap_id": learner_context.get(
                "roadmap_id"
            ),
            "mission_id": learner_context.get(
                "mission_id"
            ),
            "learning_session_id": learner_context.get(
                "learning_session_id"
            ),
            "current_progress": learner_context.get(
                "current_progress",
                {},
            ),
            "learner_stage": learner_profile.get(
                "learner_stage"
            )
            or learner_context.get(
                "learner_stage"
            ),
            "knowledge_level": learner_profile.get(
                "knowledge_level"
            ),
            "learning_style": learner_profile.get(
                "learning_style"
            ),
            "career_goal": learner_profile.get(
                "career_goal"
            ),
        }
from typing import Any

from app.core.memory import MemoryEngine
from app.schemas.request import (
    AnalyzeContextRequest,
    ContextAnswer,
    KIERequest,
    ResolveContextRequest,
)


class ContextEngine:
    """
    Context Engine.

    Existing KIE execution context:
    - Identity
    - Learner profile
    - Learner stage
    - Current lesson/topic
    - Roadmap/mission
    - Learning session
    - Project/workspace
    - Current progress
    - Active task
    - User-specific long-term memory

    Sprint 2 onboarding context support:
    - Analyze initial onboarding context
    - Identify missing context
    - Generate structured questions
    - Resolve submitted answers
    - Return refined context

    Persistent learner data remains a Backend responsibility.
    """

    def __init__(
        self,
        memory_engine: MemoryEngine | None = None,
    ):
        self.memory_engine = (
            memory_engine or MemoryEngine()
        )

    # ============================================================
    # Existing KIE Context Resolution
    # ============================================================

    def resolve(
        self,
        request: KIERequest,
    ) -> dict[str, Any]:
        """
        Resolve the complete KIE context for a learner.

        Memory retrieval is isolated using request.user_id.
        """

        current_context = dict(
            request.context
        )

        learner_context = (
            request.learner_context.model_dump()
        )

        memory_categories = (
            self._select_memory_categories(
                request
            )
        )

        relevant_memory = (
            self.memory_engine.retrieve_relevant(
                categories=memory_categories,
                user_id=request.user_id,
            )
        )

        return {
            "current_context": current_context,

            "learner_stage": (
                request.learner_stage
            ),

            "learner_profile": (
                request.learner_profile.model_dump()
            ),

            "learner_context": learner_context,

            "task": request.task,

            "memory": {
                category: [
                    {
                        "content": item.content,
                        "source": item.source,
                        "user_id": item.user_id,
                        "created_at": item.created_at,
                    }
                    for item in items
                ]
                for category, items
                in relevant_memory.items()
            },

            "memory_categories": (
                memory_categories
            ),

            "sources": {
                "current_context": "request",
                "learner_stage": "request",
                "learner_profile": "request",
                "learner_context": "request",
                "task": "request",
                "memory": "memory_engine",
            },
        }

    # ============================================================
    # Sprint 2 Onboarding Context Analysis
    # ============================================================

    def analyze_onboarding_context(
        self,
        request: AnalyzeContextRequest,
    ) -> dict[str, Any]:
        """
        Analyze initial onboarding context and identify
        information required to improve learner context.

        This method does not persist anything.

        Backend remains responsible for persistence.
        """

        initial_context = request.initial_context

        questions: list[dict[str, Any]] = []

        # --------------------------------------------------------
        # Programming languages
        # --------------------------------------------------------

        if not self._has_context_value(
            initial_context,
            [
                "skills",
                "programming_languages",
                "primary_languages",
            ],
        ):
            questions.append(
                {
                    "question_id": "q_001",
                    "text": (
                        "Which programming languages "
                        "do you primarily use?"
                    ),
                    "type": "multi_select",
                    "options": [
                        "Python",
                        "JavaScript",
                        "Go",
                        "Java",
                        "Other",
                    ],
                }
            )

        # --------------------------------------------------------
        # Experience / knowledge level
        # --------------------------------------------------------

        if not self._has_context_value(
            initial_context,
            [
                "experience_level",
                "knowledge_level",
                "skill_level",
            ],
        ):
            questions.append(
                {
                    "question_id": "q_002",
                    "text": (
                        "What is your current level "
                        "of experience?"
                    ),
                    "type": "single_select",
                    "options": [
                        "Beginner",
                        "Junior",
                        "Intermediate",
                        "Senior",
                        "Advanced",
                    ],
                }
            )

        # --------------------------------------------------------
        # Career goal
        # --------------------------------------------------------

        if not self._has_context_value(
            initial_context,
            [
                "career_goal",
                "career_goals",
                "goals",
            ],
        ):
            questions.append(
                {
                    "question_id": "q_003",
                    "text": (
                        "What is your current "
                        "career goal?"
                    ),
                    "type": "text",
                    "options": [],
                }
            )

        return {
            "status": "success",
            "requires_more_info": bool(questions),
            "questions": questions,
        }

    # ============================================================
    # Sprint 2 Onboarding Context Resolution
    # ============================================================

    def resolve_onboarding_context(
        self,
        request: ResolveContextRequest,
    ) -> dict[str, Any]:
        """
        Convert onboarding answers into structured
        learner context.

        KIE returns the refined context.

        Backend is responsible for merging this
        context with the existing database record.
        """

        new_context: dict[str, Any] = {}

        for answer in request.answers:
            self._apply_context_answer(
                new_context,
                answer,
            )

        return {
            "status": "success",
            "new_context": new_context,
        }

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _has_context_value(
        context: dict[str, Any],
        keys: list[str],
    ) -> bool:
        """
        Return True when at least one supplied context
        field contains meaningful data.
        """

        for key in keys:
            if key not in context:
                continue

            value = context[key]

            if value is None:
                continue

            if isinstance(value, str):
                if value.strip():
                    return True
                continue

            if isinstance(value, (list, dict, tuple, set)):
                if value:
                    return True
                continue

            return True

        return False

    @staticmethod
    def _apply_context_answer(
        new_context: dict[str, Any],
        answer: ContextAnswer,
    ) -> None:
        """
        Map a question answer to a structured
        context property.

        The question IDs are defined by the onboarding
        contract.
        """

        if answer.question_id == "q_001":
            new_context["primary_languages"] = (
                answer.answer
            )
            return

        if answer.question_id == "q_002":
            new_context["experience_level"] = (
                answer.answer
            )
            return

        if answer.question_id == "q_003":
            new_context["career_goal"] = (
                answer.answer
            )
            return

        # Preserve unknown question IDs instead of
        # silently discarding submitted information.
        new_context[
            answer.question_id
        ] = answer.answer

    # ============================================================
    # Existing Memory Category Selection
    # ============================================================

    def _select_memory_categories(
        self,
        request: KIERequest,
    ) -> list[str]:
        """
        Select memory relevant to the current request.

        Career planning uses goals, achievements,
        projects and preferences.

        Academic planning uses goals, learning history,
        projects and achievements.

        General learner activity uses preferences,
        conversations and learning history.
        """

        horizon = (
            request.planning_horizon or ""
        ).lower().strip()

        task = request.task.lower()

        if horizon == "career":
            return [
                "goals",
                "achievements",
                "projects",
                "preferences",
            ]

        if horizon in {
            "semester",
            "monthly",
            "weekly",
            "daily",
            "mission",
        }:
            return [
                "goals",
                "learning_history",
                "projects",
                "achievements",
            ]

        if any(
            word in task
            for word in [
                "goal",
                "progress",
                "learn",
                "study",
            ]
        ):
            return [
                "preferences",
                "conversations",
                "learning_history",
            ]

        return [
            "preferences",
            "conversations",
        ]
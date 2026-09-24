from typing import Any

from app.schemas.response import PlanStep


class PlanningEngine:
    """
    Sprint 3 Planning Engine.

    Converts learner goals, profile information, current
    learner context, memory, and planning horizons into
    structured execution plans.

    Supported planning horizons:
    - semester
    - career
    - monthly
    - weekly
    - daily
    - mission

    Backend remains responsible for persistent roadmap storage.
    """

    def create_plan(
        self,
        intent: str,
        task: str,
        planning_horizon: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[PlanStep]:
        """
        Create a structured execution plan.
        """

        context = context or {}

        # -------------------------------------------------
        # Sprint 1/2 backward compatibility
        # -------------------------------------------------

        if planning_horizon is None:
            return [
                PlanStep(
                    step_id="step-1",
                    description=f"Process {intent} request",
                    agent=self._select_agent(intent),
                )
            ]

        horizon = planning_horizon.lower().strip()

        if horizon not in {
            "semester",
            "career",
            "monthly",
            "weekly",
            "daily",
            "mission",
        }:
            horizon = "daily"

        return self._build_plan(
            intent=intent,
            task=task,
            planning_horizon=horizon,
            context=context,
        )

    def _build_plan(
        self,
        intent: str,
        task: str,
        planning_horizon: str,
        context: dict[str, Any],
    ) -> list[PlanStep]:
        """
        Build a learner-aware multi-step plan.
        """

        agent = self._select_agent(intent)

        profile = context.get(
            "learner_profile",
            {},
        )

        learner_context = context.get(
            "learner_context",
            {},
        )

        career_goal = profile.get(
            "career_goal"
        )

        skills = profile.get(
            "skills",
            [],
        )

        memory = context.get(
            "memory",
            {},
        )

        learning_history = memory.get(
            "learning_history",
            [],
        )

        goals = memory.get(
            "goals",
            [],
        )

        profile_context = self._build_profile_context(
            career_goal=career_goal,
            skills=skills,
        )

        memory_context = self._build_memory_context(
            learning_history=learning_history,
            goals=goals,
        )

        current_context = (
            self._build_learner_context(
                learner_context
            )
        )

        descriptions = self._build_descriptions(
            planning_horizon=planning_horizon,
            profile_context=profile_context,
            memory_context=memory_context,
            current_context=current_context,
        )

        return [
            PlanStep(
                step_id=f"step-{index}",
                description=description,
                agent=agent,
            )
            for index, description in enumerate(
                descriptions,
                start=1,
            )
        ]

    def _build_descriptions(
        self,
        planning_horizon: str,
        profile_context: str,
        memory_context: str,
        current_context: str,
    ) -> list[str]:
        """
        Build planning steps using learner profile,
        current learner state, and memory.
        """

        if planning_horizon == "semester":
            return [
                (
                    "Analyze semester objectives, "
                    f"learner profile{profile_context}, "
                    f"current learner state{current_context}, "
                    f"and existing progress{memory_context}"
                ),
                (
                    "Break semester objectives into "
                    "major learning goals aligned with "
                    "the learner"
                ),
                (
                    "Organize goals into subjects, "
                    "projects, and measurable milestones"
                ),
                (
                    "Create measurable semester milestones "
                    "and review checkpoints"
                ),
            ]

        if planning_horizon == "career":
            return [
                (
                    "Analyze the learner career goal"
                    f"{profile_context}, current learner "
                    f"state{current_context}, and existing "
                    f"career-related memory{memory_context}"
                ),
                (
                    "Identify required skills and "
                    "competencies relative to the "
                    "learner's current skills"
                ),
                (
                    "Break career preparation into "
                    "achievable learning and project "
                    "milestones"
                ),
                (
                    "Create a structured career "
                    "development plan"
                ),
            ]

        if planning_horizon == "monthly":
            return [
                (
                    "Review monthly objectives, "
                    f"learner profile{profile_context}, "
                    f"current learner state{current_context}, "
                    f"and recent progress{memory_context}"
                ),
                (
                    "Break objectives into monthly "
                    "learning and project goals"
                ),
                (
                    "Organize goals into measurable "
                    "practical milestones"
                ),
            ]

        if planning_horizon == "weekly":
            return [
                (
                    "Review weekly objectives, "
                    f"learner profile{profile_context}, "
                    f"current learner state{current_context}, "
                    f"and recent learning history{memory_context}"
                ),
                (
                    "Break objectives into focused "
                    "weekly learning and project tasks"
                ),
                (
                    "Prioritize tasks according to "
                    "learner goals and current progress"
                ),
            ]

        if planning_horizon == "mission":
            return [
                (
                    "Analyze the learner mission and "
                    f"relevant current state{current_context}"
                    f"{memory_context}"
                ),
                (
                    "Break the mission into "
                    "actionable learner tasks"
                ),
                (
                    "Define completion criteria and "
                    "progress checkpoints"
                ),
            ]

        return [
            (
                "Review today's learner objectives "
                f"and profile{profile_context}"
                f" with current state{current_context}"
            ),
            (
                "Prioritize actionable tasks using "
                f"recent learner progress{memory_context}"
            ),
            (
                "Create a focused daily execution plan"
            ),
        ]

    def _build_profile_context(
        self,
        career_goal: str | None,
        skills: list[str],
    ) -> str:
        """
        Build a concise profile description for planning.
        """

        details = []

        if career_goal:
            details.append(
                f", career goal: {career_goal}"
            )

        if skills:
            details.append(
                f", current skills: {', '.join(skills)}"
            )

        if not details:
            return ""

        return "".join(details)

    def _build_memory_context(
        self,
        learning_history: list[Any],
        goals: list[Any],
    ) -> str:
        """
        Build a concise memory signal for planning.
        """

        details = []

        if goals:
            details.append(
                f", {len(goals)} stored learner goal(s)"
            )

        if learning_history:
            details.append(
                f", {len(learning_history)} learning "
                "history item(s)"
            )

        if not details:
            return ""

        return "".join(details)

    def _build_learner_context(
        self,
        learner_context: dict[str, Any],
    ) -> str:
        """
        Build a concise current-state signal for planning.
        """

        details = []

        current_lesson = learner_context.get(
            "current_lesson"
        )

        current_topic = learner_context.get(
            "current_topic"
        )

        roadmap_id = learner_context.get(
            "roadmap_id"
        )

        mission_id = learner_context.get(
            "mission_id"
        )

        learning_session_id = learner_context.get(
            "learning_session_id"
        )

        project_id = learner_context.get(
            "project_id"
        )

        workspace_id = learner_context.get(
            "workspace_id"
        )

        current_progress = learner_context.get(
            "current_progress",
            {},
        )

        if current_lesson:
            details.append(
                f", current lesson: {current_lesson}"
            )

        if current_topic:
            details.append(
                f", current topic: {current_topic}"
            )

        if roadmap_id:
            details.append(
                f", roadmap: {roadmap_id}"
            )

        if mission_id:
            details.append(
                f", mission: {mission_id}"
            )

        if learning_session_id:
            details.append(
                f", learning session: "
                f"{learning_session_id}"
            )

        if project_id:
            details.append(
                f", project: {project_id}"
            )

        if workspace_id:
            details.append(
                f", workspace: {workspace_id}"
            )

        if current_progress:
            details.append(
                ", progress: "
                f"{current_progress}"
            )

        if not details:
            return ""

        return "".join(details)

    def _select_agent(
        self,
        intent: str,
    ) -> str:
        """
        Select the agent responsible for executing the plan.
        """

        agent_map = {
            "LEARN": "tutor-agent",
            "BUILD": "project-agent",
            "COMPETE": "hackathon-agent",
            "LAUNCH": "career-agent",
            "GENERAL": "general-agent",
        }

        return agent_map.get(
            intent,
            "general-agent",
        )
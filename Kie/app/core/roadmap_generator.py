from typing import Any

from app.agents.registry import AgentRegistry
from app.core.intent import IntentEngine
from app.core.orchestrator import AgentOrchestrator
from app.core.planner import PlanningEngine
from app.schemas.roadmap_generate import (
    AIMLRoadmapResponse,
    MissionType,
    RoadmapCareer,
    RoadmapContextV2Request,
    RoadmapMission,
    RoadmapSemester,
    RoadmapSubject,
)


class RoadmapGenerationEngine:
    """
    KIE roadmap generation engine.

    This adapter connects the new Backend Context V2
    roadmap contract to the existing KIE intelligence:

        Context V2
            ↓
        Intent Engine
            ↓
        Planning Engine
            ↓
        Agent Orchestrator
            ↓
        Backend-ready roadmap response

    Backend remains responsible for persistence.
    """

    def __init__(self):
        self.intent_engine = IntentEngine()

        self.planning_engine = PlanningEngine()

        self.agent_registry = AgentRegistry()

        self.agent_orchestrator = AgentOrchestrator(
            agent_registry=self.agent_registry
        )

    # ============================================================
    # Public API
    # ============================================================

    def generate(
        self,
        request: RoadmapContextV2Request,
    ) -> AIMLRoadmapResponse:

        goals = self._build_goals(request)

        milestones: list[str] = []

        missions: list[RoadmapMission] = []

        # --------------------------------------------------------
        # ACADEMIC planning
        # --------------------------------------------------------

        academic_plan = []

        if request.scope in {
            "ACADEMIC",
            "BOTH",
        }:

            academic_task = self._build_academic_task(
                request
            )

            academic_intent = (
                self.intent_engine.recognize(
                    academic_task
                )
            )

            academic_context = (
                self._build_planning_context(
                    request
                )
            )

            academic_plan = (
                self.planning_engine.create_plan(
                    intent=academic_intent.name,
                    task=academic_task,
                    planning_horizon="semester",
                    context=academic_context,
                )
            )

            academic_plan = (
                self.agent_orchestrator.prepare_plan(
                    [
                        step.model_dump()
                        for step in academic_plan
                    ]
                )
            )

            milestones.extend(
                step["description"]
                for step in academic_plan
            )

            missions.extend(
                self._plan_to_missions(
                    plan=academic_plan,
                    mission_types=[
                        MissionType.LEARNING,
                        MissionType.LEARNING,
                        MissionType.PRACTICAL,
                        MissionType.REVISION,
                    ],
                    subject=self._primary_subject(
                        request
                    ),
                    start_sequence=len(missions) + 1,
                )
            )

        # --------------------------------------------------------
        # CAREER planning
        # --------------------------------------------------------

        career_plan = []

        if request.scope in {
            "CAREER",
            "BOTH",
        }:

            career_task = self._build_career_task(
                request
            )

            career_intent = (
                self.intent_engine.recognize(
                    career_task
                )
            )

            career_context = (
                self._build_planning_context(
                    request
                )
            )

            career_plan = (
                self.planning_engine.create_plan(
                    intent=career_intent.name,
                    task=career_task,
                    planning_horizon="career",
                    context=career_context,
                )
            )

            career_plan = (
                self.agent_orchestrator.prepare_plan(
                    [
                        step.model_dump()
                        for step in career_plan
                    ]
                )
            )

            milestones.extend(
                step["description"]
                for step in career_plan
            )

            missions.extend(
                self._plan_to_missions(
                    plan=career_plan,
                    mission_types=[
                        MissionType.CAREER,
                        MissionType.LEARNING,
                        MissionType.PRACTICAL,
                        MissionType.ARTIFACT,
                    ],
                    subject=None,
                    start_sequence=len(missions) + 1,
                )
            )

        # --------------------------------------------------------
        # Build academic response
        # --------------------------------------------------------

        semesters: list[RoadmapSemester] = []

        if request.scope in {
            "ACADEMIC",
            "BOTH",
        }:
            semesters = self._build_semesters(
                request
            )

        # --------------------------------------------------------
        # Build career response
        # --------------------------------------------------------

        career = None

        if request.scope in {
            "CAREER",
            "BOTH",
        }:
            career = RoadmapCareer(
                goals=self._build_career_goals(
                    request
                )
            )

        # --------------------------------------------------------
        # Fallback
        # --------------------------------------------------------

        if not missions:

            missions.append(
                RoadmapMission(
                    title="Start roadmap",
                    type=MissionType.LEARNING,
                    description=(
                        "Begin working toward "
                        f"{request.learner.primary_goal}."
                    ),
                    priority="HIGH",
                    estimated_minutes=60,
                    subject=None,
                    week=1,
                    sequence=1,
                )
            )

        milestones = self._unique(
            milestones
        )[:20]

        return AIMLRoadmapResponse(
            scope=request.scope,
            semesters=semesters,
            career=career,
            goals=goals,
            milestones=milestones,
            missions=missions,
        )

    # ============================================================
    # Planning Context
    # ============================================================

    def _build_planning_context(
        self,
        request: RoadmapContextV2Request,
    ) -> dict[str, Any]:

        education = request.education

        learner_profile = {
            "career_goal": (
                request.learner.primary_goal
            ),
            "skills": self._unique(
                request.skills
                + request.career.target_skills
            ),
            "learning_style": (
                request.preferences.get(
                    "learning_style"
                )
            ),
            "knowledge_level": (
                request.preferences.get(
                    "knowledge_level"
                )
            ),
            "semester": education.get(
                "semester"
            ),
            "education_level": (
                education.get(
                    "education_level"
                )
                or education.get(
                    "degree"
                )
            ),
        }

        learner_context = {
            "roadmap_id": (
                request.roadmap.get(
                    "id"
                )
                or request.roadmap.get(
                    "roadmap_id"
                )
            ),
            "mission_id": (
                request.roadmap.get(
                    "mission_id"
                )
            ),
            "current_progress": (
                request.roadmap.get(
                    "progress",
                    {}
                )
            ),
        }

        learning_history = (
            request.recent_history
        )

        goals = []

        if request.learner.primary_goal:
            goals.append(
                request.learner.primary_goal
            )

        goals.extend(
            request.career.target_skills
        )

        if request.memory_summary:
            learning_history = (
                list(learning_history)
                + [
                    {
                        "summary": (
                            request.memory_summary
                        )
                    }
                ]
            )

        return {
            "learner_profile": learner_profile,

            "learner_context": learner_context,

            "memory": {
                "learning_history": (
                    learning_history
                ),
                "goals": self._unique(
                    goals
                ),
            },

            "current_context": {
                "education": education,
                "preferences": (
                    request.preferences
                ),
                "syllabus": (
                    request.syllabus
                ),
                "roadmap": (
                    request.roadmap
                ),
            },
        }

    # ============================================================
    # Tasks for Intent Engine
    # ============================================================

    def _build_academic_task(
        self,
        request: RoadmapContextV2Request,
    ) -> str:

        subject_names = self._extract_subject_names(
            request.syllabus
        )

        if subject_names:
            subjects = ", ".join(
                subject_names[:6]
            )

            return (
                "Create an academic semester "
                "roadmap covering the learner's "
                f"subjects: {subjects}"
            )

        return (
            "Create an academic semester "
            "learning roadmap for "
            f"{request.learner.primary_goal}"
        )

    def _build_career_task(
        self,
        request: RoadmapContextV2Request,
    ) -> str:

        skills = self._unique(
            request.career.target_skills
            + request.skills
        )

        if skills:
            return (
                "Create a career roadmap for "
                f"{request.learner.primary_goal} "
                "with target skills: "
                f"{', '.join(skills[:8])}"
            )

        return (
            "Create a career development roadmap "
            f"for {request.learner.primary_goal}"
        )

    # ============================================================
    # Goals
    # ============================================================

    def _build_goals(
        self,
        request: RoadmapContextV2Request,
    ) -> list[str]:

        goals = []

        if request.learner.primary_goal:
            goals.append(
                request.learner.primary_goal
            )

        for skill in request.career.target_skills:

            goals.append(
                f"Develop proficiency in {skill}"
            )

        for skill in request.skills:

            goals.append(
                f"Strengthen {skill}"
            )

        return self._unique(
            goals
        )[:10]

    def _build_career_goals(
        self,
        request: RoadmapContextV2Request,
    ) -> list[str]:

        goals = []

        if request.learner.primary_goal:
            goals.append(
                request.learner.primary_goal
            )

        for skill in request.career.target_skills:

            goals.append(
                f"Build career competency in {skill}"
            )

        return self._unique(
            goals
        )[:10]

    # ============================================================
    # Plan → Missions
    # ============================================================

    def _plan_to_missions(
        self,
        plan: list[dict[str, Any]],
        mission_types: list[MissionType],
        subject: str | None,
        start_sequence: int,
    ) -> list[RoadmapMission]:

        missions = []

        for index, step in enumerate(
            plan,
            start=0,
        ):

            if index < len(mission_types):
                mission_type = (
                    mission_types[index]
                )
            else:
                mission_type = (
                    MissionType.LEARNING
                )

            description = step.get(
                "description",
                "Complete the planned roadmap step.",
            )

            agent = step.get(
                "agent"
            )

            if agent:
                description = (
                    f"{description}. "
                    f"Assigned agent: {agent}."
                )

            priority = (
                "HIGH"
                if index == 0
                else "MEDIUM"
            )

            missions.append(
                RoadmapMission(
                    title=self._mission_title(
                        description
                    ),
                    type=mission_type,
                    description=description,
                    priority=priority,
                    estimated_minutes=(
                        self._estimated_minutes(
                            mission_type
                        )
                    ),
                    subject=subject,
                    week=index + 1,
                    sequence=(
                        start_sequence + index
                    ),
                )
            )

        return missions

    @staticmethod
    def _mission_title(
        description: str,
    ) -> str:

        title = description.strip()

        if len(title) <= 90:
            return title

        return (
            title[:87].rstrip()
            + "..."
        )

    @staticmethod
    def _estimated_minutes(
        mission_type: MissionType,
    ) -> int:

        estimates = {
            MissionType.LEARNING: 60,
            MissionType.REVISION: 45,
            MissionType.ASSIGNMENT: 90,
            MissionType.PRACTICAL: 90,
            MissionType.ARTIFACT: 120,
            MissionType.CAREER: 90,
        }

        return estimates[
            mission_type
        ]

    # ============================================================
    # Academic Subjects
    # ============================================================

    def _build_semesters(
        self,
        request: RoadmapContextV2Request,
    ) -> list[RoadmapSemester]:

        subjects = self._extract_subjects(
            request.syllabus
        )

        if not subjects:

            skills = self._unique(
                request.skills
                + request.career.target_skills
            )

            for skill in skills[:6]:

                subjects.append(
                    RoadmapSubject(
                        name=skill,
                        topics=[
                            f"{skill} fundamentals",
                            f"{skill} practical applications",
                        ],
                    )
                )

        if not subjects:

            subjects.append(
                RoadmapSubject(
                    name="Core Learning",
                    topics=[
                        "Fundamentals",
                        "Practice",
                        "Review",
                    ],
                )
            )

        return [
            RoadmapSemester(
                name="Current Semester",
                subjects=subjects,
            )
        ]

    def _extract_subjects(
        self,
        syllabus: dict[str, Any],
    ) -> list[RoadmapSubject]:

        subjects = []

        raw_subjects = syllabus.get(
            "subjects",
            []
        )

        if isinstance(
            raw_subjects,
            dict,
        ):
            raw_subjects = [
                {
                    "name": name,
                    "topics": topics,
                }
                for name, topics
                in raw_subjects.items()
            ]

        if not isinstance(
            raw_subjects,
            list,
        ):
            return subjects

        for item in raw_subjects:

            if isinstance(
                item,
                str,
            ):
                subjects.append(
                    RoadmapSubject(
                        name=item,
                        topics=[],
                    )
                )
                continue

            if not isinstance(
                item,
                dict,
            ):
                continue

            name = (
                item.get("name")
                or item.get("subject")
            )

            topics = item.get(
                "topics",
                [],
            )

            if not name:
                continue

            if isinstance(
                topics,
                str,
            ):
                topics = [topics]

            if not isinstance(
                topics,
                list,
            ):
                topics = []

            subjects.append(
                RoadmapSubject(
                    name=str(name),
                    topics=[
                        str(topic)
                        for topic in topics
                    ],
                )
            )

        return subjects

    def _extract_subject_names(
        self,
        syllabus: dict[str, Any],
    ) -> list[str]:

        return [
            subject.name
            for subject in self._extract_subjects(
                syllabus
            )
        ]

    def _primary_subject(
        self,
        request: RoadmapContextV2Request,
    ) -> str | None:

        subjects = self._extract_subjects(
            request.syllabus
        )

        if subjects:
            return subjects[0].name

        skills = self._unique(
            request.skills
            + request.career.target_skills
        )

        if skills:
            return skills[0]

        return None

    # ============================================================
    # Utilities
    # ============================================================

    @staticmethod
    def _unique(
        values: list[Any],
    ) -> list[Any]:

        result = []

        for value in values:

            if value is None:
                continue

            if value not in result:
                result.append(value)

        return result
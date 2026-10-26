from app.schemas.build_plan import (
    BuildPlanMilestone,
    BuildPlanRequest,
    BuildPlanResponse,
    BuildPlanTask,
)


class BuildPlanGenerationEngine:
    """
    Sprint 5 — AI/ML-1 Project Planning.

    Generates bounded, structured project plans for different
    artifact types while keeping one universal Build contract.

    Supported artifact types include:
    - CODING
    - RESEARCH
    - BUSINESS
    - ANALYSIS
    - DESIGN

    Backend remains responsible for persistence.
    """

    ARTIFACT_ALIASES = {
        "CODE": "CODING",
        "CODING": "CODING",
        "SOFTWARE": "CODING",
        "DEVELOPMENT": "CODING",
        "RESEARCH": "RESEARCH",
        "BUSINESS": "BUSINESS",
        "BUSINESS_CASE": "BUSINESS",
        "BUSINESS-CASE": "BUSINESS",
        "ANALYSIS": "ANALYSIS",
        "DATA_ANALYSIS": "ANALYSIS",
        "DATA-ANALYSIS": "ANALYSIS",
        "DESIGN": "DESIGN",
        "UX": "DESIGN",
        "UI": "DESIGN",
    }

    def generate(
        self,
        request: BuildPlanRequest,
    ) -> BuildPlanResponse:

        skills = self._normalize_skills(request.skills)
        artifact_type = self._normalize_artifact_type(
            request.type
        )

        if artifact_type == "CODING":
            milestones = self._build_coding_plan(
                request,
                skills,
            )

        elif artifact_type == "RESEARCH":
            milestones = self._build_research_plan(
                request,
                skills,
            )

        elif artifact_type == "BUSINESS":
            milestones = self._build_business_plan(
                request,
                skills,
            )

        elif artifact_type == "ANALYSIS":
            milestones = self._build_analysis_plan(
                request,
                skills,
            )

        elif artifact_type == "DESIGN":
            milestones = self._build_design_plan(
                request,
                skills,
            )

        else:
            milestones = self._build_generic_plan(
                request,
                skills,
            )

        return BuildPlanResponse(
            milestones=milestones,
        )

    # ========================================================
    # CODING
    # ========================================================

    def _build_coding_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        return [
            self._build_coding_setup_milestone(
                request,
                skills,
            ),
            self._build_coding_implementation_milestone(
                request,
                skills,
            ),
            self._build_coding_validation_milestone(
                request,
            ),
        ]

    def _build_coding_setup_milestone(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> BuildPlanMilestone:

        tasks = [
            BuildPlanTask(
                title=f"Define {request.title} requirements",
                description=(
                    f"Break down the project goal into clear "
                    f"requirements for {request.domain}."
                ),
                order_idx=1,
            ),
            BuildPlanTask(
                title="Set up project foundation",
                description=(
                    f"Initialize the technical foundation for "
                    f"this {request.type.lower()} project."
                ),
                order_idx=2,
            ),
        ]

        if skills:
            tasks.append(
                BuildPlanTask(
                    title="Configure required technologies",
                    description=(
                        "Prepare the project stack around the "
                        f"required skills: {', '.join(skills)}."
                    ),
                    order_idx=3,
                )
            )

        return BuildPlanMilestone(
            title="Phase 1: Project Setup",
            description=(
                f"Establish the foundation for {request.title} "
                "and translate the project goal into an "
                "executable plan."
            ),
            order_idx=1,
            tasks=tasks,
        )

    def _build_coding_implementation_milestone(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> BuildPlanMilestone:

        primary_skill = (
            skills[0]
            if skills
            else request.domain
        )

        return BuildPlanMilestone(
            title="Phase 2: Core Implementation",
            description=(
                f"Implement the core functionality required "
                f"to achieve the project goal: {request.goal}."
            ),
            order_idx=2,
            tasks=[
                BuildPlanTask(
                    title=f"Implement {primary_skill} functionality",
                    description=(
                        f"Build the main project functionality "
                        f"using {primary_skill}."
                    ),
                    order_idx=1,
                ),
                BuildPlanTask(
                    title="Integrate project components",
                    description=(
                        "Connect the major project components "
                        "and verify the end-to-end workflow."
                    ),
                    order_idx=2,
                ),
            ],
        )

    def _build_coding_validation_milestone(
        self,
        request: BuildPlanRequest,
    ) -> BuildPlanMilestone:

        return BuildPlanMilestone(
            title="Phase 3: Testing and Review",
            description=(
                f"Validate {request.title} against its "
                "requirements and prepare it for delivery."
            ),
            order_idx=3,
            tasks=[
                BuildPlanTask(
                    title="Test core functionality",
                    description=(
                        "Run functional tests and verify "
                        "the main project workflow."
                    ),
                    order_idx=1,
                ),
                BuildPlanTask(
                    title="Review and refine the implementation",
                    description=(
                        "Identify issues, improve the implementation, "
                        "and confirm that the project goal is satisfied."
                    ),
                    order_idx=2,
                ),
            ],
        )

    # ========================================================
    # RESEARCH
    # ========================================================

    def _build_research_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        return [
            BuildPlanMilestone(
                title="Phase 1: Research Definition",
                description=(
                    f"Define the research objective, scope, "
                    f"and key questions for {request.title}."
                ),
                order_idx=1,
                tasks=[
                    BuildPlanTask(
                        title="Define research questions",
                        description=(
                            f"Translate the project goal into "
                            f"focused research questions: {request.goal}."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Define research scope",
                        description=(
                            f"Establish the boundaries and domain "
                            f"of the research: {request.domain}."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 2: Investigation",
                description=(
                    "Collect and organize relevant evidence "
                    "to answer the research questions."
                ),
                order_idx=2,
                tasks=[
                    BuildPlanTask(
                        title="Collect relevant sources",
                        description=(
                            "Identify reliable sources and "
                            "collect evidence relevant to the study."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Analyze collected evidence",
                        description=(
                            "Compare and organize the evidence "
                            "to identify meaningful findings."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 3: Findings and Presentation",
                description=(
                    "Synthesize the research findings and "
                    "prepare them for communication."
                ),
                order_idx=3,
                tasks=[
                    BuildPlanTask(
                        title="Document research findings",
                        description=(
                            "Summarize the main findings and "
                            "their relationship to the research goal."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Prepare final presentation",
                        description=(
                            "Organize the findings into a clear "
                            "deliverable for the intended audience."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
        ]

    # ========================================================
    # BUSINESS
    # ========================================================

    def _build_business_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        return [
            BuildPlanMilestone(
                title="Phase 1: Problem and Market Definition",
                description=(
                    f"Define the business problem, target users, "
                    f"and market context for {request.title}."
                ),
                order_idx=1,
                tasks=[
                    BuildPlanTask(
                        title="Define the business problem",
                        description=(
                            f"Clarify the problem addressed by "
                            f"the project: {request.goal}."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Identify target users",
                        description=(
                            "Define the primary users, stakeholders, "
                            "and relevant market segment."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 2: Business Analysis",
                description=(
                    "Analyze the proposed solution, market context, "
                    "and business feasibility."
                ),
                order_idx=2,
                tasks=[
                    BuildPlanTask(
                        title="Analyze the proposed solution",
                        description=(
                            "Evaluate how the proposed solution "
                            "addresses the identified problem."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Evaluate feasibility",
                        description=(
                            "Assess practical, technical, and "
                            "business considerations."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 3: Proposal and Validation",
                description=(
                    "Prepare the business case and validate "
                    "the proposed direction."
                ),
                order_idx=3,
                tasks=[
                    BuildPlanTask(
                        title="Prepare business proposal",
                        description=(
                            "Organize the problem, solution, "
                            "value, and feasibility into a proposal."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Review business assumptions",
                        description=(
                            "Identify assumptions and verify the "
                            "most important risks and dependencies."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
        ]

    # ========================================================
    # ANALYSIS
    # ========================================================

    def _build_analysis_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        return [
            BuildPlanMilestone(
                title="Phase 1: Requirements and Data",
                description=(
                    f"Define the analysis objective and identify "
                    f"the information required for {request.title}."
                ),
                order_idx=1,
                tasks=[
                    BuildPlanTask(
                        title="Define analysis objective",
                        description=(
                            f"Translate the project goal into "
                            f"a measurable analysis objective: {request.goal}."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Identify required data",
                        description=(
                            "Identify the datasets, evidence, "
                            "or inputs required for the analysis."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 2: Analysis",
                description=(
                    "Process and analyze the available information "
                    "to identify meaningful patterns and results."
                ),
                order_idx=2,
                tasks=[
                    BuildPlanTask(
                        title="Prepare analysis inputs",
                        description=(
                            "Clean, organize, and validate the "
                            "information required for analysis."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Perform analysis",
                        description=(
                            "Apply appropriate analysis methods "
                            "to answer the defined objective."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 3: Findings and Recommendations",
                description=(
                    "Interpret the analysis results and prepare "
                    "actionable conclusions."
                ),
                order_idx=3,
                tasks=[
                    BuildPlanTask(
                        title="Interpret findings",
                        description=(
                            "Explain the important results and "
                            "their relationship to the objective."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Prepare recommendations",
                        description=(
                            "Convert the findings into clear "
                            "recommendations or next actions."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
        ]

    # ========================================================
    # DESIGN
    # ========================================================

    def _build_design_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        return [
            BuildPlanMilestone(
                title="Phase 1: Design Requirements",
                description=(
                    f"Define the goals, users, requirements, "
                    f"and constraints for {request.title}."
                ),
                order_idx=1,
                tasks=[
                    BuildPlanTask(
                        title="Define design requirements",
                        description=(
                            f"Translate the project goal into "
                            f"clear design requirements: {request.goal}."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Identify users and constraints",
                        description=(
                            "Identify target users, important "
                            "constraints, and expected outcomes."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 2: Design Development",
                description=(
                    "Develop and organize the proposed design "
                    "solution based on the requirements."
                ),
                order_idx=2,
                tasks=[
                    BuildPlanTask(
                        title="Create design concepts",
                        description=(
                            "Develop candidate design concepts "
                            "that address the project requirements."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Develop selected design",
                        description=(
                            "Refine the selected concept into "
                            "a structured design deliverable."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 3: Review and Presentation",
                description=(
                    "Evaluate the design and prepare the final "
                    "deliverable for presentation."
                ),
                order_idx=3,
                tasks=[
                    BuildPlanTask(
                        title="Review design",
                        description=(
                            "Evaluate the design against the "
                            "defined requirements and constraints."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Prepare final presentation",
                        description=(
                            "Organize the final design and "
                            "supporting explanation for delivery."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
        ]

    # ========================================================
    # GENERIC
    # ========================================================

    def _build_generic_plan(
        self,
        request: BuildPlanRequest,
        skills: list[str],
    ) -> list[BuildPlanMilestone]:

        setup_tasks = [
            BuildPlanTask(
                title=f"Define {request.title} requirements",
                description=(
                    f"Translate the project goal into clear "
                    f"requirements for {request.domain}."
                ),
                order_idx=1,
            ),
            BuildPlanTask(
                title="Prepare project foundation",
                description=(
                    "Identify the resources, inputs, and "
                    "dependencies required to begin the project."
                ),
                order_idx=2,
            ),
        ]

        if skills:
            setup_tasks.append(
                BuildPlanTask(
                    title="Identify relevant skills",
                    description=(
                        "Align the project plan with the required "
                        f"skills: {', '.join(skills)}."
                    ),
                    order_idx=3,
                )
            )

        return [
            BuildPlanMilestone(
                title="Phase 1: Project Definition",
                description=(
                    f"Define the scope and foundation for "
                    f"{request.title}."
                ),
                order_idx=1,
                tasks=setup_tasks,
            ),
            BuildPlanMilestone(
                title="Phase 2: Core Work",
                description=(
                    f"Execute the core work required to achieve "
                    f"the project goal: {request.goal}."
                ),
                order_idx=2,
                tasks=[
                    BuildPlanTask(
                        title="Execute core project work",
                        description=(
                            "Complete the primary activities "
                            "required by the project."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Integrate project outputs",
                        description=(
                            "Combine the major outputs into "
                            "a coherent project result."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
            BuildPlanMilestone(
                title="Phase 3: Review and Delivery",
                description=(
                    f"Review {request.title} and prepare "
                    "the final deliverable."
                ),
                order_idx=3,
                tasks=[
                    BuildPlanTask(
                        title="Review project outcome",
                        description=(
                            "Verify that the project satisfies "
                            "its requirements and goal."
                        ),
                        order_idx=1,
                    ),
                    BuildPlanTask(
                        title="Prepare final deliverable",
                        description=(
                            "Organize the completed work for "
                            "submission or presentation."
                        ),
                        order_idx=2,
                    ),
                ],
            ),
        ]

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @classmethod
    def _normalize_artifact_type(
        cls,
        artifact_type: str,
    ) -> str:

        normalized = str(
            artifact_type
        ).strip().upper()

        return cls.ARTIFACT_ALIASES.get(
            normalized,
            normalized,
        )

    @staticmethod
    def _normalize_skills(
        skills: list[str],
    ) -> list[str]:

        normalized: list[str] = []

        for skill in skills:
            value = str(skill).strip()

            if value and value not in normalized:
                normalized.append(value)

        return normalized

from app.schemas.collaboration import (
    CollaborationRequest,
    CollaborationResponse,
    CollaborationTask,
)


class CollaborationOrchestrationEngine:
    """Suggest team task coordination without persisting business state."""

    def generate(
        self,
        request: CollaborationRequest,
    ) -> CollaborationResponse:
        title = request.challenge_title.strip()
        challenge_type = request.challenge_type.strip().lower()
        statement = request.challenge_statement.strip().lower()

        members = list(
            dict.fromkeys(
                member.strip()
                for member in request.team_members
                if member.strip()
            )
        )

        task_templates = [
            (
                "Understand requirements",
                "Review the challenge statement, rules, constraints, and judging criteria.",
                "high",
                [],
            ),
            (
                "Plan the approach",
                "Choose an appropriate solution strategy and divide the work into manageable tasks.",
                "high",
                ["Understand requirements"],
            ),
            (
                "Complete the main work",
                "Develop the required outcome, gather evidence, or prepare the proposed solution.",
                "high",
                ["Plan the approach"],
            ),
            (
                "Review and prepare delivery",
                "Validate the outcome against the requirements and prepare the final deliverable.",
                "medium",
                ["Complete the main work"],
            ),
        ]

        if challenge_type in {"research", "academic"}:
            task_templates[2] = (
                "Gather and analyze evidence",
                "Collect relevant evidence, evaluate sources, and document findings.",
                "high",
                ["Plan the approach"],
            )
        elif challenge_type in {"business", "startup", "entrepreneurship"}:
            task_templates[2] = (
                "Validate the proposal",
                "Assess feasibility, user value, risks, and expected impact.",
                "high",
                ["Plan the approach"],
            )
        elif challenge_type == "design":
            task_templates[2] = (
                "Develop and review concepts",
                "Create candidate designs and evaluate them against user needs.",
                "high",
                ["Plan the approach"],
            )

        tasks = []
        for index, (task_title, description, priority, dependencies) in enumerate(
            task_templates
        ):
            owner = members[index % len(members)] if members else None

            tasks.append(
                CollaborationTask(
                    title=task_title,
                    description=description,
                    suggested_owner=owner,
                    depends_on=dependencies,
                    priority=priority,
                )
            )

        tool_categories = ["task_tracking", "document_sharing", "team_communication"]

        if challenge_type in {"hackathon", "coding", "software"}:
            tool_categories.extend(["version_control", "testing"])
        elif challenge_type in {"research", "academic"}:
            tool_categories.extend(["research_sources", "data_analysis"])
        elif challenge_type in {"business", "startup", "entrepreneurship"}:
            tool_categories.extend(["market_research", "presentation"])
        elif challenge_type == "design":
            tool_categories.extend(["prototyping", "design_review"])
        elif any(
            word in statement
            for word in ("presentation", "pitch", "demo")
        ):
            tool_categories.append("presentation")

        checkpoints = [
            "Kickoff: agree on the objective, scope, owners, and deadline.",
            "Midpoint: review progress, dependencies, and blockers.",
            "Final review: validate the deliverable against the challenge requirements.",
        ]

        assumptions = [
            "Task assignments are suggestions only; team members should confirm ownership.",
            "KIE does not store team membership, competition state, or task completion.",
        ]

        if not members:
            assumptions.append(
                "No team members were supplied; tasks have no assigned owners."
            )
        else:
            assumptions.append(
                "Owners are assigned in rotation from the supplied team-member list; skills and availability were not verified."
            )

        return CollaborationResponse(
            challenge_title=title,
            challenge_type=challenge_type,
            tasks=tasks,
            coordination_checkpoints=checkpoints,
            suggested_tool_categories=list(dict.fromkeys(tool_categories)),
            assumptions=assumptions,
        )

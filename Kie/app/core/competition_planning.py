
from app.schemas.competition_planning import (
    CompetitionPlanTask,
    CompetitionPlanningRequest,
    CompetitionPlanningResponse,
)


class CompetitionPlanningEngine:
    """Generate challenge-specific plans without persisting business state."""

    def generate(
        self,
        request: CompetitionPlanningRequest,
    ) -> CompetitionPlanningResponse:
        title = request.challenge_title.strip()
        statement = request.challenge_statement.strip()
        challenge_type = request.challenge_type.strip().lower()
        statement_lower = statement.lower()

        plan_templates = {
            "hackathon": [
                ("Understand the problem", "Identify users, constraints, judging criteria, and the core problem."),
                ("Design the solution", "Choose an approach, define the scope, and plan a feasible prototype."),
                ("Build and validate", "Implement the essential features and test the solution."),
                ("Prepare the demonstration", "Prepare a demo, explain the impact, and verify submission requirements."),
            ],
            "coding": [
                ("Clarify requirements", "Identify functional requirements, constraints, and acceptance criteria."),
                ("Design the implementation", "Choose data structures, architecture, and an implementation approach."),
                ("Implement and test", "Build the solution and test normal and edge cases."),
                ("Review and submit", "Check correctness, document the approach, and prepare the required submission."),
            ],
            "research": [
                ("Define the research question", "Clarify the question, scope, and expected research output."),
                ("Gather evidence", "Identify reliable sources or data and document the methodology."),
                ("Analyze findings", "Compare evidence, validate conclusions, and note limitations."),
                ("Prepare the report", "Present findings, supporting evidence, conclusions, and references."),
            ],
            "business": [
                ("Understand the market problem", "Identify the target users, problem, and available evidence."),
                ("Develop the business approach", "Define the value proposition, feasibility, and key assumptions."),
                ("Validate the proposal", "Evaluate risks, costs, impact, and potential alternatives."),
                ("Prepare the pitch", "Present the problem, proposed solution, evidence, and expected impact."),
            ],
            "startup": [
                ("Define the user problem", "Identify the target audience and validate the problem."),
                ("Shape the value proposition", "Describe the solution, differentiation, and business model."),
                ("Validate feasibility", "Assess resources, risks, assumptions, and early validation options."),
                ("Prepare the pitch", "Explain the opportunity, solution, feasibility, and impact."),
            ],
            "design": [
                ("Research users and constraints", "Identify user needs, context, and design requirements."),
                ("Explore concepts", "Develop alternative concepts and compare their strengths."),
                ("Create and validate", "Produce a prototype or design artifact and gather feedback where possible."),
                ("Present the design", "Explain design decisions, usability, and the expected user benefit."),
            ],
        }

        selected = plan_templates.get(
            challenge_type,
            [
                ("Understand the challenge", "Clarify the objective, constraints, rules, and judging criteria."),
                ("Plan the approach", "Break the work into manageable tasks and choose an approach appropriate to the challenge."),
                ("Develop the outcome", "Complete the required work and validate it against the challenge requirements."),
                ("Review and participate", "Prepare the final deliverable and confirm the participation or submission process."),
            ],
        )

        total_days = request.deadline_days
        if total_days is None:
            day_ranges = ["Day 1", "Days 2–3", "Days 4–5", "Final day"]
            assumptions = [
                "No deadline was supplied; the plan uses a suggested four-stage sequence rather than a fixed schedule."
            ]
        else:
            # Divide the available days across four ordered stages.
            day_ranges = []
            for index in range(4):
                start = (index * total_days) // 4 + 1
                end = ((index + 1) * total_days) // 4
                if end < start:
                    end = start
                day_ranges.append(
                    f"Day {start}" if start == end else f"Days {start}–{end}"
                )
            assumptions = [
                f"The plan is organized within the supplied {total_days}-day preparation window."
            ]

        tasks = [
            CompetitionPlanTask(
                title=task_title,
                description=description,
                priority="high" if index in (0, 3) else "medium",
                day_range=day_ranges[index],
            )
            for index, (task_title, description) in enumerate(selected)
        ]

        checklist = [
            "Understand the challenge rules, eligibility, and judging criteria.",
            "Confirm the expected deliverables and submission format.",
            "Review the completed work against the stated requirements.",
            "Verify the deadline and submission or participation instructions.",
        ]

        if any(word in statement_lower for word in ("presentation", "pitch", "demo")):
            checklist.append("Rehearse the presentation, pitch, or demonstration.")

        if any(word in statement_lower for word in ("research", "evidence", "data")):
            checklist.append("Verify the evidence, sources, and conclusions.")

        members = [
            member.strip()
            for member in request.team_members
            if member.strip()
        ]

        if members:
            collaboration = [
                "Agree on the shared objective, deadline, and acceptance criteria.",
                "Assign task owners based on skills and availability.",
                "Set checkpoints to review progress and resolve dependencies.",
                "Review the final deliverable together before submission.",
            ]
        else:
            collaboration = [
                "If participating as a team, agree on task ownership and checkpoints.",
                "If working individually, break the plan into manageable tasks and review progress regularly.",
            ]

        if request.learner_context:
            assumptions.append(
                "Learner context was supplied; tailor task ownership and effort to the learner's actual skills and availability."
            )
        else:
            assumptions.append(
                "No learner-specific context was supplied; adjust the plan to available skills, resources, and time."
            )

        if challenge_type not in plan_templates:
            assumptions.append(
                "A general challenge workflow was selected because no specialized plan template matched the challenge type."
            )

        return CompetitionPlanningResponse(
            challenge_title=title,
            challenge_type=challenge_type,
            objective=statement,
            preparation_plan=tasks,
            success_checklist=checklist,
            collaboration_guidance=collaboration,
            assumptions=assumptions,
        )

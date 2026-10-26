
from typing import Any

from app.schemas.competition_recommend import (
    CompetitionRecommendation,
    CompetitionRecommendationRequest,
    CompetitionRecommendationResponse,
)


class CompetitionRecommendationEngine:
    """Recommend challenge types using supplied learner context."""

    CHALLENGES = [
        {
            "title": "Build for Good Hackathon",
            "challenge_type": "hackathon",
            "description": "Design and demonstrate a practical solution to a real-world problem.",
            "skills": ["python", "programming", "software", "problem solving", "teamwork"],
            "interests": ["technology", "coding", "innovation", "software"],
        },
        {
            "title": "Research and Discovery Challenge",
            "challenge_type": "research",
            "description": "Investigate a question, analyze evidence, and present supported findings.",
            "skills": ["research", "analysis", "data analysis", "writing", "statistics"],
            "interests": ["research", "science", "data", "academics"],
        },
        {
            "title": "Startup Innovation Challenge",
            "challenge_type": "business",
            "description": "Develop and validate a business idea that addresses a user problem.",
            "skills": ["business", "communication", "market research", "planning", "presentation"],
            "interests": ["entrepreneurship", "business", "startups", "innovation"],
        },
        {
            "title": "Creative Design Challenge",
            "challenge_type": "design",
            "description": "Explore user needs and create a design concept or prototype.",
            "skills": ["design", "figma", "creativity", "user research", "prototyping"],
            "interests": ["design", "creativity", "user experience", "art"],
        },
        {
            "title": "Community Impact Challenge",
            "challenge_type": "community",
            "description": "Propose a feasible initiative that addresses a community need.",
            "skills": ["communication", "planning", "research", "teamwork", "leadership"],
            "interests": ["community", "social impact", "environment", "volunteering"],
        },
    ]

    @staticmethod
    def _normalise_values(value: Any) -> list[str]:
        if isinstance(value, str):
            return [part.strip().lower() for part in value.split(",") if part.strip()]

        if isinstance(value, list):
            return [
                str(item).strip().lower()
                for item in value
                if str(item).strip()
            ]

        return []

    def generate(
        self,
        request: CompetitionRecommendationRequest,
    ) -> CompetitionRecommendationResponse:
        context = request.learner_context or {}

        skills = set(self._normalise_values(context.get("skills", [])))
        interests = set(self._normalise_values(context.get("interests", [])))
        goals = set(self._normalise_values(context.get("goals", [])))

        # Goals may provide additional signals when they mention a
        # challenge domain or relevant skill.
        goal_text = " ".join(goals)

        results = []

        for challenge in self.CHALLENGES:
            skill_matches = [
                skill for skill in challenge["skills"]
                if any(
                    skill == learner_skill
                    or skill in learner_skill
                    or learner_skill in skill
                    for learner_skill in skills
                )
            ]

            interest_matches = [
                interest for interest in challenge["interests"]
                if any(
                    interest in learner_interest
                    or learner_interest in interest
                    for learner_interest in interests
                )
            ]

            goal_matches = [
                keyword for keyword in challenge["skills"] + challenge["interests"]
                if keyword in goal_text
            ]

            # Deterministic relevance score based on the provided context.
            score = min(
                100,
                len(skill_matches) * 20
                + len(interest_matches) * 25
                + len(goal_matches) * 10,
            )

            if not context:
                reason = (
                    "No learner context was provided; this is a general "
                    "challenge suggestion."
                )
            elif skill_matches or interest_matches or goal_matches:
                signals = []
                if skill_matches:
                    signals.append("skills: " + ", ".join(skill_matches))
                if interest_matches:
                    signals.append("interests: " + ", ".join(interest_matches))
                if goal_matches:
                    signals.append("goals: " + ", ".join(sorted(set(goal_matches))))
                reason = "Relevant to your " + "; ".join(signals) + "."
            else:
                reason = (
                    "This provides an opportunity to explore a different "
                    "challenge area based on the context supplied."
                )

            results.append(
                CompetitionRecommendation(
                    title=challenge["title"],
                    challenge_type=challenge["challenge_type"],
                    description=challenge["description"],
                    matched_skills=skill_matches,
                    reason=reason,
                    relevance_score=score,
                )
            )

        # Prefer context-relevant challenges, with stable ordering for ties.
        results.sort(key=lambda item: item.relevance_score, reverse=True)

        return CompetitionRecommendationResponse(
            recommendations=results[:request.limit]
        )

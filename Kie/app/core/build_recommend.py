from app.schemas.build_recommend import (
    BuildRecommendation,
    BuildRecommendationResponse,
)


class BuildRecommendationEngine:
    """
    Sprint 5 — Build Recommendations.

    Provides project recommendations that can help a learner
    strengthen relevant technical and project-building skills.

    Backend remains responsible for learner state and persistence.
    """

    def generate(
        self,
        learner_id: str,
    ) -> BuildRecommendationResponse:

        return BuildRecommendationResponse(
            recommendations=[
                BuildRecommendation(
                    title="Task Management API",
                    description=(
                        "Build a REST API to manage tasks and users "
                        "to strengthen backend development skills."
                    ),
                    type="CODING",
                    skills=[
                        "Python",
                        "FastAPI",
                        "SQLAlchemy",
                    ],
                ),
                BuildRecommendation(
                    title="UX Research Study: E-Commerce",
                    description=(
                        "Conduct a usability study on existing "
                        "e-commerce cart flows."
                    ),
                    type="RESEARCH",
                    skills=[
                        "User Testing",
                        "Figma",
                        "Data Analysis",
                    ],
                ),
            ]
        )
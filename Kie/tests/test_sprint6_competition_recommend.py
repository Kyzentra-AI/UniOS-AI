
from app.core.competition_recommend import CompetitionRecommendationEngine
from app.schemas.competition_recommend import CompetitionRecommendationRequest


def test_recommendations_use_learner_skills():
    engine = CompetitionRecommendationEngine()

    result = engine.generate(
        CompetitionRecommendationRequest(
            learner_id="learner-1",
            learner_context={
                "skills": ["Python", "programming"],
                "interests": ["coding", "technology"],
            },
        )
    )

    assert result.recommendations
    assert result.recommendations[0].challenge_type == "hackathon"
    assert result.recommendations[0].relevance_score > 0
    assert result.recommendations[0].matched_skills


def test_different_context_changes_recommendation_ranking():
    engine = CompetitionRecommendationEngine()

    coding_result = engine.generate(
        CompetitionRecommendationRequest(
            learner_id="learner-1",
            learner_context={
                "skills": ["Python", "programming"],
                "interests": ["coding", "technology"],
            },
        )
    )

    research_result = engine.generate(
        CompetitionRecommendationRequest(
            learner_id="learner-2",
            learner_context={
                "skills": ["research", "statistics", "data analysis"],
                "interests": ["science", "research", "data"],
            },
        )
    )

    assert (
        coding_result.recommendations[0].challenge_type
        != research_result.recommendations[0].challenge_type
    )
    assert research_result.recommendations[0].challenge_type == "research"


def test_empty_context_returns_general_suggestions():
    result = CompetitionRecommendationEngine().generate(
        CompetitionRecommendationRequest(learner_id="learner-3")
    )

    assert len(result.recommendations) == 3
    assert all(item.relevance_score == 0 for item in result.recommendations)
    assert all("general challenge suggestion" in item.reason for item in result.recommendations)


def test_recommendation_limit_is_respected():
    result = CompetitionRecommendationEngine().generate(
        CompetitionRecommendationRequest(
            learner_id="learner-4",
            limit=2,
        )
    )

    assert len(result.recommendations) == 2

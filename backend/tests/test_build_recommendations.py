import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.schemas.build import (
    ProjectType,
    RecommendedProject,
    ProjectRecommendationResponse,
    normalize_project_type,
    CreateProjectInput,
)
from app.api.v1.endpoints.build import get_recommendations

def test_normalize_project_type():
    assert normalize_project_type("code_project") == ProjectType.CODING
    assert normalize_project_type("CODING") == ProjectType.CODING
    assert normalize_project_type("research_report") == ProjectType.RESEARCH
    assert normalize_project_type("case_analysis") == ProjectType.ANALYSIS
    assert normalize_project_type("business_plan") == ProjectType.BUSINESS
    assert normalize_project_type("design_artifact") == ProjectType.DESIGN
    assert normalize_project_type("oral_viva") == ProjectType.OTHER
    assert normalize_project_type("unknown_type") == ProjectType.OTHER

def test_recommended_project_schema_validation():
    # Test normalization of KIE wire format
    kie_wire_item = {
        "title": "AI Recommendation Project",
        "description": "A deep dive into system programming.",
        "type": "code_project",
        "skills": ["Python", "Algorithms"]
    }
    rec = RecommendedProject(**kie_wire_item)
    assert rec.type == ProjectType.CODING
    assert rec.title == "AI Recommendation Project"

    # Test ProjectRecommendationResponse
    response = ProjectRecommendationResponse(recommendations=[kie_wire_item])
    assert len(response.recommendations) == 1
    assert response.recommendations[0].type == ProjectType.CODING

def test_create_project_input_type_normalization():
    input_data = {
        "title": "New Project from Recommendation",
        "type": "code_project",
        "skills": ["TypeScript"]
    }
    project_input = CreateProjectInput(**input_data)
    assert project_input.type == ProjectType.CODING

def test_get_recommendations_with_kie_wire_types():
    # Mock KIE returning code_project and business_plan
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "learner_id": "learner-123",
        "recommendations": [
            {
                "recommendation_id": "rec_001",
                "title": "Distributed Task Queue",
                "type": "code_project",
                "description": "Build an asynchronous worker engine.",
                "skills": ["Concurrency", "Redis"]
            },
            {
                "recommendation_id": "rec_002",
                "title": "Market Landscape Analysis",
                "type": "business_plan",
                "description": "Evaluate market dynamics and competitors.",
                "skills": ["Strategy", "Financial Modeling"]
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    async def run():
        with patch("app.api.v1.endpoints.build._get_learner_id", return_value="learner-123"), \
             patch("app.services.build.build_kie.httpx.AsyncClient") as mock_client_cls:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.get.return_value = mock_response
            mock_client_cls.return_value = mock_instance

            result = await get_recommendations(current_user={"user_id": "user-123"})
            assert len(result.recommendations) == 2
            assert result.recommendations[0].type == ProjectType.CODING
            assert result.recommendations[1].type == ProjectType.BUSINESS

    asyncio.run(run())

def test_get_recommendations_fallback_on_network_error():
    # Mock network failure communicating with KIE
    async def run():
        with patch("app.api.v1.endpoints.build._get_learner_id", return_value="learner-123"), \
             patch("app.services.build.build_kie.httpx.AsyncClient") as mock_client_cls:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.get.side_effect = Exception("Connection refused")
            mock_client_cls.return_value = mock_instance

            result = await get_recommendations(current_user={"user_id": "user-123"})
            assert len(result.recommendations) >= 3
            for item in result.recommendations:
                assert isinstance(item.type, ProjectType)

    asyncio.run(run())

def test_get_recommendations_fallback_on_missing_learner_profile():
    # If learner profile is not found in Supabase, fallback is still returned
    from fastapi import HTTPException
    async def run():
        with patch("app.api.v1.endpoints.build._get_learner_id", side_effect=HTTPException(status_code=404, detail="Not found")), \
             patch("app.services.build.build_kie.httpx.AsyncClient") as mock_client_cls:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_instance.get.side_effect = Exception("Connection refused")
            mock_client_cls.return_value = mock_instance

            result = await get_recommendations(current_user={"user_id": "user-123"})
            assert len(result.recommendations) >= 3

    asyncio.run(run())

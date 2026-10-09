import httpx
import logging
from typing import Dict, Any, List
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.build import (
    ProjectRecommendationResponse,
    BuildCoachRequest,
    BuildCoachResponse,
    CreateMilestoneInput,
    CreateTaskInput
)
from app.services.build.build_workspace import build_workspace_service

logger = logging.getLogger(__name__)

class BuildKIEClient:
    @staticmethod
    async def get_recommendations(learner_id: str) -> ProjectRecommendationResponse:
        """
        Calls KIE /api/v1/kie/build/recommend to fetch AI recommendations based on learner profile.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/build/recommend",
                    params={"learner_id": learner_id},
                    timeout=30.0
                )
                response.raise_for_status()
                return ProjectRecommendationResponse(**response.json())
            except Exception as exc:
                logger.error(f"Failed to fetch project recommendations: {exc}")
                raise HTTPException(status_code=503, detail="Failed to fetch recommendations from AI engine")

    @staticmethod
    async def generate_plan(project_id: str) -> Dict[str, Any]:
        """
        Calls KIE /api/v1/kie/build/plan and auto-inserts milestones and tasks for a project.
        """
        project = build_workspace_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        payload = {
            "project_id": project_id,
            "title": project.title,
            "description": project.description,
            "type": project.type.value if hasattr(project.type, "value") else project.type,
            "domain": project.domain,
            "goal": project.goal,
            "skills": project.skills
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/build/plan",
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                plan_data = response.json()
            except Exception as exc:
                logger.error(f"Failed to generate project plan: {exc}")
                raise HTTPException(status_code=503, detail="Failed to generate plan from AI engine")
                
        # Auto-insert milestones and tasks
        milestones = plan_data.get("milestones", [])
        for m_data in milestones:
            m_input = CreateMilestoneInput(
                title=m_data.get("title", "Milestone"),
                description=m_data.get("description"),
                order_idx=m_data.get("order_idx", 0)
            )
            milestone = build_workspace_service.create_milestone(project_id, m_input)
            
            tasks = m_data.get("tasks", [])
            for t_data in tasks:
                t_input = CreateTaskInput(
                    milestone_id=milestone.id,
                    title=t_data.get("title", "Task"),
                    description=t_data.get("description"),
                    order_idx=t_data.get("order_idx", 0)
                )
                build_workspace_service.create_task(project_id, t_input)
                
        return {"status": "success", "message": "Plan generated and applied successfully"}

    @staticmethod
    async def ask_coach(project_id: str, request: BuildCoachRequest) -> BuildCoachResponse:
        """
        Sends project context and returns guidance from KIE.
        """
        project = build_workspace_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        payload = request.model_dump()
        payload["project_context"] = {
            "id": str(project.id),
            "title": project.title,
            "type": project.type.value if hasattr(project.type, "value") else project.type,
            "status": project.status.value if hasattr(project.status, "value") else project.status,
            "skills": project.skills
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/build/coach",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return BuildCoachResponse(**response.json())
            except Exception as exc:
                logger.error(f"Failed to get guidance from coach: {exc}")
                raise HTTPException(status_code=503, detail="Failed to communicate with AI coach")

build_kie_client = BuildKIEClient()

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body

from app.core.deps import get_current_user
from app.core.supabase import supabase_admin
from app.schemas.build import (
    Project, CreateProjectInput, UpdateProjectInput,
    Milestone, CreateMilestoneInput, UpdateMilestoneInput,
    Task, CreateTaskInput, UpdateTaskInput,
    Artifact, CreateArtifactInput, ArtifactVersionResponse,
    Evidence, CreateEvidenceInput,
    BuildCoachRequest, BuildCoachResponse, ProjectRecommendationResponse
)
from app.services.build.build_workspace import build_workspace_service
from app.services.build.build_kie import build_kie_client

router = APIRouter(prefix="/api/v1/build", tags=["Build"])

def _get_learner_id(user_id: str) -> str:
    res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Learner profile not found")
    return res.data[0]["id"]

@router.get("/recommendations", response_model=ProjectRecommendationResponse)
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    return await build_kie_client.get_recommendations(learner_id)

@router.get("/projects", response_model=List[Project])
async def list_projects(current_user: dict = Depends(get_current_user)):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.list_projects(learner_id)

@router.post("/projects", response_model=Project)
async def create_project(
    input_data: CreateProjectInput, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.create_project(learner_id, input_data)

@router.get("/projects/{id}", response_model=Project)
async def get_project(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    project = build_workspace_service.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects/{id}/milestones", response_model=List[Milestone])
async def get_project_milestones(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.get_milestones(id, learner_id)

@router.get("/projects/{id}/tasks", response_model=List[Task])
async def get_project_tasks(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.get_tasks(id, learner_id)

@router.get("/projects/{id}/artifacts", response_model=List[Artifact])
async def get_project_artifacts(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.get_artifacts(id, learner_id)

@router.get("/projects/{id}/evidence", response_model=List[Evidence])
async def get_project_evidence(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.get_evidence(id, learner_id)

@router.patch("/projects/{id}", response_model=Project)
async def update_project(
    id: str, 
    input_data: UpdateProjectInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.update_project(id, input_data)

@router.post("/projects/{id}/plan-generate")
async def generate_plan(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    return await build_kie_client.generate_plan(id)

@router.post("/projects/{id}/milestones", response_model=Milestone)
async def create_milestone(
    id: str, 
    input_data: CreateMilestoneInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.create_milestone(id, input_data)

@router.patch("/milestones/{milestone_id}", response_model=Milestone)
async def update_milestone(
    milestone_id: str, 
    input_data: UpdateMilestoneInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.update_milestone(milestone_id, input_data)

@router.post("/projects/{id}/tasks", response_model=Task)
async def create_task(
    id: str, 
    input_data: CreateTaskInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.create_task(id, input_data)

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str, 
    input_data: UpdateTaskInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.update_task(task_id, input_data)

@router.post("/projects/{id}/artifacts", response_model=Artifact)
async def create_artifact(
    id: str, 
    input_data: CreateArtifactInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.create_artifact(id, input_data)

@router.post("/artifacts/{artifact_id}/versions", response_model=ArtifactVersionResponse)
async def create_artifact_version(
    artifact_id: str, 
    file_name: Optional[str] = Body(None),
    file_size: Optional[int] = Body(None),
    storage_key: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.create_artifact_version(
        artifact_id, file_name, file_size, storage_key
    )

@router.post("/projects/{id}/evidence", response_model=Evidence)
async def create_evidence(
    id: str, 
    input_data: CreateEvidenceInput, 
    current_user: dict = Depends(get_current_user)
):
    return build_workspace_service.create_evidence(id, input_data)

@router.post("/projects/{id}/coach", response_model=BuildCoachResponse)
async def ask_coach(
    id: str, 
    request: BuildCoachRequest, 
    current_user: dict = Depends(get_current_user)
):
    return await build_kie_client.ask_coach(id, request)

@router.post("/projects/{id}/complete", response_model=Project)
async def complete_project(
    id: str, 
    current_user: dict = Depends(get_current_user)
):
    learner_id = _get_learner_id(current_user["user_id"])
    return build_workspace_service.complete_project(id, learner_id)

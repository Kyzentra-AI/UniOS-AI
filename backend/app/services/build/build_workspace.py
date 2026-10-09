from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.supabase import supabase_admin
from app.schemas.build import (
    CreateProjectInput, UpdateProjectInput, Project,
    CreateMilestoneInput, UpdateMilestoneInput, Milestone,
    CreateTaskInput, UpdateTaskInput, Task,
    CreateArtifactInput, Artifact, ArtifactVersionResponse,
    CreateEvidenceInput, Evidence, ProjectStatus, TaskStatus
)
from app.services.event_service import EventService

class BuildWorkspaceService:
    @staticmethod
    def get_project(project_id: str) -> Optional[Project]:
        res = supabase_admin.table("build_projects").select("*").eq("id", project_id).execute()
        if not res.data:
            return None
        return Project(**res.data[0])

    @staticmethod
    def list_projects(learner_id: str) -> List[Project]:
        res = supabase_admin.table("build_projects").select("*").eq("learner_id", learner_id).execute()
        return [Project(**item) for item in res.data]

    @staticmethod
    def create_project(learner_id: str, input_data: CreateProjectInput) -> Project:
        data = input_data.model_dump(exclude_unset=True)
        data["learner_id"] = learner_id
        # Convert enums to string values
        if "type" in data and hasattr(data["type"], "value"):
            data["type"] = data["type"].value
        res = supabase_admin.table("build_projects").insert(data).execute()
        return Project(**res.data[0])

    @staticmethod
    def update_project(project_id: str, input_data: UpdateProjectInput) -> Project:
        data = input_data.model_dump(exclude_unset=True)
        if "type" in data and hasattr(data["type"], "value"):
            data["type"] = data["type"].value
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
            
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = supabase_admin.table("build_projects").update(data).eq("id", project_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project(**res.data[0])

    @staticmethod
    def complete_project(project_id: str, learner_id: str) -> Project:
        # Enforce logic ensuring all tasks are COMPLETED or BLOCKED before a project can move to COMPLETED
        tasks_res = supabase_admin.table("build_tasks").select("status").eq("project_id", project_id).execute()
        incomplete_tasks = [t for t in tasks_res.data if t["status"] not in [TaskStatus.COMPLETED.value, TaskStatus.BLOCKED.value]]
        if incomplete_tasks:
            raise HTTPException(status_code=400, detail="Cannot complete project with pending or in-progress tasks.")
        
        data = {
            "status": ProjectStatus.COMPLETED.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        res = supabase_admin.table("build_projects").update(data).eq("id", project_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Project not found")
            
        EventService.record_event(learner_id, "PROJECT_COMPLETED", "PROJECT", project_id)
        return Project(**res.data[0])

    @staticmethod
    def create_milestone(project_id: str, input_data: CreateMilestoneInput) -> Milestone:
        data = input_data.model_dump(exclude_unset=True)
        data["project_id"] = project_id
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        res = supabase_admin.table("build_milestones").insert(data).execute()
        return Milestone(**res.data[0])

    @staticmethod
    def update_milestone(milestone_id: str, input_data: UpdateMilestoneInput) -> Milestone:
        data = input_data.model_dump(exclude_unset=True)
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        res = supabase_admin.table("build_milestones").update(data).eq("id", milestone_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Milestone not found")
        return Milestone(**res.data[0])

    @staticmethod
    def create_task(project_id: str, input_data: CreateTaskInput) -> Task:
        data = input_data.model_dump(exclude_unset=True)
        data["project_id"] = project_id
        if data.get("milestone_id"):
            data["milestone_id"] = str(data["milestone_id"])
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        res = supabase_admin.table("build_tasks").insert(data).execute()
        return Task(**res.data[0])

    @staticmethod
    def update_task(task_id: str, input_data: UpdateTaskInput) -> Task:
        data = input_data.model_dump(exclude_unset=True)
        if data.get("milestone_id"):
            data["milestone_id"] = str(data["milestone_id"])
        if "status" in data and hasattr(data["status"], "value"):
            data["status"] = data["status"].value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = supabase_admin.table("build_tasks").update(data).eq("id", task_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Task not found")
        return Task(**res.data[0])

    @staticmethod
    def create_artifact(project_id: str, input_data: CreateArtifactInput) -> Artifact:
        artifact_data = {
            "project_id": project_id,
            "title": input_data.title,
            "description": input_data.description,
            "type": input_data.type.value if hasattr(input_data.type, "value") else input_data.type
        }
        res = supabase_admin.table("build_artifacts").insert(artifact_data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create artifact")
            
        artifact_id = res.data[0]["id"]
        
        # create first version
        version_data = {
            "artifact_id": artifact_id,
            "version": 1,
            "file_name": input_data.file_name,
            "file_size": input_data.file_size,
            "storage_key": input_data.storage_key
        }
        v_res = supabase_admin.table("build_artifact_versions").insert(version_data).execute()
        
        artifact_model = Artifact(**res.data[0])
        artifact_model.versions = [ArtifactVersionResponse(**v_res.data[0])]
        return artifact_model
        
    @staticmethod
    def create_artifact_version(artifact_id: str, file_name: Optional[str] = None, file_size: Optional[int] = None, storage_key: Optional[str] = None) -> ArtifactVersionResponse:
        # Get latest version
        res = supabase_admin.table("build_artifact_versions").select("version").eq("artifact_id", artifact_id).order("version", desc=True).limit(1).execute()
        next_version = 1
        if res.data:
            next_version = res.data[0]["version"] + 1
            
        version_data = {
            "artifact_id": artifact_id,
            "version": next_version,
            "file_name": file_name,
            "file_size": file_size,
            "storage_key": storage_key
        }
        v_res = supabase_admin.table("build_artifact_versions").insert(version_data).execute()
        
        # update artifact updated_at
        supabase_admin.table("build_artifacts").update({"updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", artifact_id).execute()
        
        return ArtifactVersionResponse(**v_res.data[0])

    @staticmethod
    def create_evidence(project_id: str, input_data: CreateEvidenceInput) -> Evidence:
        data = input_data.model_dump(exclude_unset=True)
        data["project_id"] = project_id
        if data.get("artifact_id"):
            data["artifact_id"] = str(data["artifact_id"])
        res = supabase_admin.table("build_evidence").insert(data).execute()
        return Evidence(**res.data[0])

build_workspace_service = BuildWorkspaceService()

import httpx
import logging
from typing import Dict, Any, List
from fastapi import HTTPException
from app.core.config import settings
from app.core.context_v2_assembler import ContextV2Assembler
from app.schemas.billing import CreditOperation
from app.schemas.build import (
    ProjectRecommendationResponse,
    RecommendedProject,
    ProjectType,
    BuildCoachRequest,
    BuildCoachResponse,
    CreateMilestoneInput,
    CreateTaskInput
)
from app.services.billing.billing_guard import billing_guard
from app.services.build.build_workspace import build_workspace_service

logger = logging.getLogger(__name__)


def _extract_syllabus_context(syllabus: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """Extract subject names and topic strings from ContextV2 syllabus payload."""
    subjects: List[str] = []
    topics: List[str] = []
    if not isinstance(syllabus, dict):
        return subjects, topics

    for subj in syllabus.get("subjects") or []:
        if not isinstance(subj, dict):
            continue
        name = (subj.get("name") or "").strip()
        if name and name not in subjects:
            subjects.append(name)
        for t in subj.get("topics") or []:
            t_str = (t.get("name") or t.get("title") if isinstance(t, dict) else str(t)).strip()
            if t_str and t_str not in topics:
                topics.append(t_str)
        for ch in subj.get("chapters") or []:
            if isinstance(ch, dict):
                for t in ch.get("topics") or []:
                    t_str = (t.get("name") or t.get("title") if isinstance(t, dict) else str(t)).strip()
                    if t_str and t_str not in topics:
                        topics.append(t_str)
    return subjects, topics


def _is_non_cs_profile(degree_program: str | None, academic_domain: str | None, subjects: List[str]) -> bool:
    combined = f"{degree_program or ''} {academic_domain or ''} {' '.join(subjects)}".lower()
    non_cs_markers = ("bba", "mba", "bcom", "commerce", "management", "accounting", "finance", "economics", "humanities", "arts")
    return any(m in combined for m in non_cs_markers)


class BuildKIEClient:
    @staticmethod
    async def get_recommendations(learner_id: str) -> ProjectRecommendationResponse:
        """
        Assembles ContextV2 (academic_profiles + active syllabus_documents) and calls
        POST /api/v1/kie/build/recommend for syllabus-grounded recommendations.
        Falls back to domain-aware starter recommendations if KIE is unavailable.
        """
        degree_program = None
        academic_domain = None
        target_role = None
        syllabus_subjects: List[str] = []
        syllabus_topics: List[str] = []

        try:
            ctx = await ContextV2Assembler.assemble(learner_id, scope="build")
            edu = ctx.get("education") or {}
            learner_info = ctx.get("learner") or {}
            degree_program = edu.get("degree_program")
            academic_domain = edu.get("domain")
            target_role = learner_info.get("primary_goal")
            syllabus_subjects, syllabus_topics = _extract_syllabus_context(ctx.get("syllabus") or {})
        except Exception as ctx_exc:
            logger.warning(f"Failed to assemble build context for {learner_id}: {ctx_exc}")

        payload = {
            "learner_id": learner_id,
            "degree_program": degree_program,
            "academic_domain": academic_domain,
            "domain": academic_domain,
            "syllabus_subjects": syllabus_subjects,
            "syllabus_topics": syllabus_topics[:50],
            "target_role": target_role,
            "count": 3,
        }

        timeout = httpx.Timeout(20.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/build/recommend",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                recs = data.get("recommendations", [])
                if isinstance(recs, list) and len(recs) > 0:
                    return ProjectRecommendationResponse(recommendations=recs)
            except Exception as exc:
                logger.warning(f"Could not fetch AI recommendations from KIE ({exc}), serving domain-aware defaults")

        if _is_non_cs_profile(degree_program, academic_domain, syllabus_subjects):
            domain_label = academic_domain or degree_program or "Business & Management"
            return ProjectRecommendationResponse(
                recommendations=[
                    RecommendedProject(
                        title="Small Venture Business Plan & PESTLE Analysis",
                        description="Evaluate macro-environmental factors (PESTLE) and design a practical PODC management plan for a local venture.",
                        type=ProjectType.BUSINESS,
                        domain=domain_label,
                        skills=["PESTLE Analysis", "Management Planning", "Business Strategy", "Market Assessment"],
                    ),
                    RecommendedProject(
                        title="Retail Financial Ledger & Trial Balance Workbook",
                        description="Record journal entries, post to ledgers, and prepare a balanced trial balance and income statement for a sample enterprise.",
                        type=ProjectType.ANALYSIS,
                        domain=domain_label,
                        skills=["Journal Entries", "Trial Balance", "Financial Accounting", "Spreadsheet Modeling"],
                    ),
                    RecommendedProject(
                        title="Local Product Demand & Pricing Study",
                        description="Analyze consumer demand elasticity, competitor pricing, and breakeven volume for a regional consumer product.",
                        type=ProjectType.RESEARCH,
                        domain=domain_label,
                        skills=["Demand Analysis", "Pricing Strategy", "Business Economics", "Primary Research"],
                    ),
                ]
            )

        return ProjectRecommendationResponse(
            recommendations=[
                RecommendedProject(
                    title="End-to-End Web Application",
                    description="Design, build, and deploy a responsive full-stack application with authentication, API endpoints, and database persistence.",
                    type=ProjectType.CODING,
                    domain=academic_domain or "Software Engineering",
                    skills=["React", "TypeScript", "FastAPI", "Database Design", "REST APIs"]
                ),
                RecommendedProject(
                    title="Data Analysis & Performance Dashboard",
                    description="Collect, clean, and visualize complex metrics and operational KPIs with interactive charts and automated reporting.",
                    type=ProjectType.ANALYSIS,
                    domain=academic_domain or "Data Analytics",
                    skills=["Data Analysis", "Python", "Visualization", "Metrics", "SQL"]
                ),
                RecommendedProject(
                    title="System Architecture & Scalability Review",
                    description="Benchmark performance, identify latency bottlenecks, and design a resilient microservices architecture blueprint.",
                    type=ProjectType.RESEARCH,
                    domain=academic_domain or "Systems Architecture",
                    skills=["System Design", "Cloud Architecture", "Performance Tuning", "Benchmarking"]
                )
            ]
        )

    @staticmethod
    async def generate_plan(project_id: str) -> Dict[str, Any]:
        """
        Calls KIE /api/v1/kie/build/plan and auto-inserts milestones and tasks for a project.
        """
        project = build_workspace_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        ledger_id = billing_guard.authorize_and_consume(
            learner_id=str(project.learner_id),
            operation=CreditOperation.ADVANCED_PROJECT_GUIDANCE,
            reference_id=project_id,
        ) if getattr(project, "learner_id", None) else None

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
                billing_guard.refund(ledger_id)
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

        is_debug = "debug" in (request.intent or "").lower()
        learner_id = str(project.learner_id) if getattr(project, "learner_id", None) else None
        ledger_id: Optional[str] = None
        if learner_id:
            if is_debug:
                billing_guard.require_capability(learner_id, "debugging")
                ledger_id = billing_guard.authorize_and_consume(
                    learner_id=learner_id,
                    operation=CreditOperation.ADVANCED_DEBUGGING,
                    reference_id=project_id,
                )
            else:
                ledger_id = billing_guard.authorize_and_consume(
                    learner_id=learner_id,
                    operation=CreditOperation.ADVANCED_PROJECT_GUIDANCE,
                    reference_id=project_id,
                )
            
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
                billing_guard.refund(ledger_id)
                logger.error(f"Failed to get guidance from coach: {exc}")
                raise HTTPException(status_code=503, detail="Failed to communicate with AI coach")

build_kie_client = BuildKIEClient()

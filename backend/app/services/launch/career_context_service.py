"""
Career Context and Evidence Aggregation Service (BE-S7-01 & BE-S7-04).
Provides read-only profile-to-resume mapping and context assembly for KIE grounding.
Strictly ensures source profile tables are never mutated.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Set
import uuid

from fastapi import HTTPException, status
from app.core.supabase import supabase_admin
from app.core.context_v2_assembler import ContextV2Assembler
from app.schemas.launch import (
    ProfileResumePreviewResponse,
    ResumeDraft,
    ResumeContact,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeAchievement,
)

logger = logging.getLogger(__name__)


class CareerContextService:
    """Service to aggregate learner profile and career evidence into resume drafts and KIE context."""

    @staticmethod
    def get_profile_resume_preview(user_id: str) -> ProfileResumePreviewResponse:
        """
        Generates a read-only resume draft preview from the learner's existing profile,
        academic background, mastery records, and build projects/evidence.
        Identifies and returns missing fields to guide user completion.
        Guarantees zero mutations on source profile tables.
        """
        # 1. Fetch user account data
        try:
            user_res = supabase_admin.table("users").select("full_name, email").eq("user_id", user_id).execute()
            user_data = user_res.data[0] if user_res.data else {}
        except Exception as e:
            logger.warning(f"Failed to fetch user row for user_id={user_id}: {e}")
            user_data = {}

        # 2. Fetch learner profile
        learner_res = supabase_admin.table("learner_profiles").select("*").eq("user_id", user_id).execute()
        if not learner_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner profile not found for authenticated user"
            )
        learner = learner_res.data[0]
        learner_id = learner["id"]

        # 3. Fetch academic profile
        try:
            academic_res = supabase_admin.table("academic_profiles").select("*").eq("learner_profile_id", learner_id).execute()
            academic = academic_res.data[0] if academic_res.data else {}
        except Exception as e:
            logger.warning(f"Failed to fetch academic_profiles for learner_id={learner_id}: {e}")
            academic = {}

        # 4. Fetch build projects (status in ACTIVE, COMPLETED)
        try:
            projects_res = (
                supabase_admin.table("build_projects")
                .select("*")
                .eq("learner_id", learner_id)
                .in_("status", ["ACTIVE", "COMPLETED"])
                .order("created_at", desc=True)
                .execute()
            )
            build_projects = projects_res.data if projects_res.data else []
        except Exception as e:
            logger.warning(f"Failed to fetch build_projects for learner_id={learner_id}: {e}")
            build_projects = []

        # 5. Fetch build evidence linked to projects
        build_evidence: List[Dict[str, Any]] = []
        if build_projects:
            project_ids = [p["id"] for p in build_projects if "id" in p]
            if project_ids:
                try:
                    evidence_res = (
                        supabase_admin.table("build_evidence")
                        .select("*")
                        .in_("project_id", project_ids)
                        .order("created_at", desc=True)
                        .execute()
                    )
                    build_evidence = evidence_res.data if evidence_res.data else []
                except Exception as e:
                    logger.warning(f"Failed to fetch build_evidence for learner_id={learner_id}: {e}")
                    build_evidence = []

        # 6. Fetch learner mastery records (status in PROFICIENT, MASTERED)
        try:
            mastery_res = (
                supabase_admin.table("learner_mastery")
                .select("topic, mastery_score, status")
                .eq("learner_id", learner_id)
                .in_("status", ["PROFICIENT", "MASTERED"])
                .execute()
            )
            mastery_rows = mastery_res.data if mastery_res.data else []
        except Exception as e:
            logger.warning(f"Failed to fetch learner_mastery for learner_id={learner_id}: {e}")
            mastery_rows = []

        missing_fields: List[str] = []

        # A. Map Contact
        full_name = user_data.get("full_name") or learner.get("full_name") or "Learner"
        email = user_data.get("email") or learner.get("email") or "learner@unios.ai"
        contact = ResumeContact(
            full_name=full_name,
            email=email,
            phone="",
            location="",
            linked_in_url=None,
            github_url=None,
            portfolio_url=None,
        )
        missing_fields.extend([
            "contact.phone",
            "contact.location",
            "contact.linkedInUrl",
            "contact.githubUrl"
        ])

        # B. Derive Headline
        headline = ""
        degree_prog = academic.get("degree_program")
        acad_status = academic.get("academic_status")
        primary_goal = learner.get("primary_goal")

        if degree_prog and acad_status:
            headline = f"{degree_prog} Student" if acad_status.upper() in ["PURSUING", "ENROLLED"] else f"{degree_prog} Graduate"
        elif degree_prog:
            headline = f"{degree_prog} Specialist"
        elif primary_goal:
            headline = f"Aspiring {primary_goal}"
        else:
            headline = "Technology & Software Professional"

        # C. Derive Summary
        domain = academic.get("domain") or "computer science & engineering"
        if primary_goal:
            summary = (
                f"Dedicated and goal-oriented individual with a focus on {primary_goal}. "
                f"Possesses a strong academic foundation in {domain} and demonstrated practical experience through "
                f"hands-on projects, evidence-backed builds, and continuous mastery development."
            )
        else:
            summary = (
                f"Proactive learner and problem solver specializing in {domain}. "
                "Proven track record of building technical deliverables, applying modern software practices, "
                "and mastering high-impact technologies."
            )

        # D. Aggregate & Deduplicate Skills
        skills_set: Set[str] = set()
        ordered_skills: List[str] = []

        def add_skill(s: Any):
            if not s:
                return
            if isinstance(s, str):
                cleaned = s.strip()
                if cleaned and cleaned.lower() not in skills_set:
                    skills_set.add(cleaned.lower())
                    ordered_skills.append(cleaned)
            elif isinstance(s, dict):
                val = s.get("name") or s.get("title") or s.get("skill")
                if val:
                    add_skill(val)

        # 1. From learner_profiles.skills
        learner_skills = learner.get("skills")
        if isinstance(learner_skills, list):
            for sk in learner_skills:
                add_skill(sk)
        elif isinstance(learner_skills, dict):
            for k, val in learner_skills.items():
                if isinstance(val, list):
                    for sk in val:
                        add_skill(sk)
                else:
                    add_skill(k)

        # 2. From learner_mastery topics
        for row in mastery_rows:
            topic = row.get("topic")
            if topic:
                add_skill(topic)

        # 3. From build_projects skills
        for proj in build_projects:
            proj_skills = proj.get("skills")
            if isinstance(proj_skills, list):
                for sk in proj_skills:
                    add_skill(sk)

        # 4. From learner_profiles.target_skills
        target_skills = learner.get("target_skills")
        if isinstance(target_skills, list):
            for sk in target_skills:
                add_skill(sk)

        if not ordered_skills:
            missing_fields.append("skills")

        # E. Map Education
        education_list: List[ResumeEducation] = []
        if academic and (academic.get("university") or academic.get("degree_program")):
            start_yr = str(academic.get("current_year")) if academic.get("current_year") else None
            end_yr = str(academic.get("graduation_year")) if academic.get("graduation_year") else None
            education_list.append(
                ResumeEducation(
                    id=str(uuid.uuid4()),
                    institution=academic.get("university") or "",
                    degree=academic.get("degree_program") or "",
                    field_of_study=academic.get("domain") or "",
                    start_date=start_yr,
                    end_date=end_yr,
                    grade=None,
                )
            )
            missing_fields.append("education[0].grade")
        else:
            missing_fields.append("education")

        # F. Map Experience
        experience_list: List[ResumeExperience] = []
        exp_raw = learner.get("experience")
        if exp_raw and str(exp_raw).strip():
            experience_list.append(
                ResumeExperience(
                    id=str(uuid.uuid4()),
                    company="",
                    role="",
                    location="",
                    start_date=None,
                    end_date=None,
                    is_current=False,
                    description=str(exp_raw).strip(),
                )
            )
            missing_fields.extend(["experience[0].company", "experience[0].role"])
        else:
            missing_fields.append("experience")

        # G. Map Projects
        projects_list: List[ResumeProject] = []
        if build_projects:
            for bp in build_projects:
                techs = bp.get("skills") if isinstance(bp.get("skills"), list) else []
                projects_list.append(
                    ResumeProject(
                        id=str(bp.get("id", uuid.uuid4())),
                        name=bp.get("title") or "Project",
                        description=bp.get("description") or "",
                        technologies=techs,
                        project_url=None,
                        start_date=None,
                        end_date=None,
                    )
                )
        else:
            # Fallback to learner_profiles.projects
            learner_projects = learner.get("projects")
            if isinstance(learner_projects, list) and learner_projects:
                for lp in learner_projects:
                    if isinstance(lp, dict):
                        projects_list.append(
                            ResumeProject(
                                id=str(uuid.uuid4()),
                                name=lp.get("title") or lp.get("name") or "Project",
                                description=lp.get("description") or "",
                                technologies=lp.get("technologies") or lp.get("skills") or [],
                                project_url=lp.get("project_url") or lp.get("url"),
                                start_date=None,
                                end_date=None,
                            )
                        )
                    elif isinstance(lp, str) and lp.strip():
                        projects_list.append(
                            ResumeProject(
                                id=str(uuid.uuid4()),
                                name=lp.strip(),
                                description="",
                                technologies=[],
                            )
                        )

        if not projects_list:
            missing_fields.append("projects")

        # H. Map Achievements
        achievements_list: List[ResumeAchievement] = []
        for ev in build_evidence:
            achievements_list.append(
                ResumeAchievement(
                    id=str(ev.get("id", uuid.uuid4())),
                    title=ev.get("title") or "Project Deliverable & Evidence",
                    description=ev.get("description") or "",
                    date=ev.get("created_at")[:10] if ev.get("created_at") else None,
                )
            )

        draft = ResumeDraft(
            contact=contact,
            headline=headline,
            summary=summary,
            skills=ordered_skills,
            education=education_list,
            experience=experience_list,
            projects=projects_list,
            achievements=achievements_list,
        )

        return ProfileResumePreviewResponse(
            content=draft,
            missing_fields=missing_fields,
        )

    @staticmethod
    async def assemble_career_context(learner_id: str) -> Dict[str, Any]:
        """
        Assembles holistic learner context via ContextV2Assembler and enriches it
        with build projects, evidence, and mastery records for KIE grounding.
        """
        # Call base context assembler with CAREER scope
        base_context = await ContextV2Assembler.assemble(learner_id, scope="CAREER")

        # Fetch projects
        try:
            projects_res = (
                supabase_admin.table("build_projects")
                .select("id, title, description, type, domain, goal, skills, status")
                .eq("learner_id", learner_id)
                .execute()
            )
            build_projects = projects_res.data if projects_res.data else []
        except Exception as e:
            logger.warning(f"Error fetching build_projects for context: {e}")
            build_projects = []

        # Fetch evidence
        build_evidence = []
        if build_projects:
            project_ids = [p["id"] for p in build_projects if "id" in p]
            if project_ids:
                try:
                    evidence_res = (
                        supabase_admin.table("build_evidence")
                        .select("id, project_id, title, description, skills, created_at")
                        .in_("project_id", project_ids)
                        .execute()
                    )
                    build_evidence = evidence_res.data if evidence_res.data else []
                except Exception as e:
                    logger.warning(f"Error fetching build_evidence for context: {e}")
                    build_evidence = []

        # Fetch mastery records
        try:
            mastery_res = (
                supabase_admin.table("learner_mastery")
                .select("subject, topic, mastery_score, status, last_assessed_at")
                .eq("learner_id", learner_id)
                .execute()
            )
            mastery_records = mastery_res.data if mastery_res.data else []
        except Exception as e:
            logger.warning(f"Error fetching learner_mastery for context: {e}")
            mastery_records = []

        base_context["career_readiness"] = {
            "projects": build_projects,
            "evidence": build_evidence,
            "mastery": mastery_records,
        }

        return base_context


career_context_service = CareerContextService()

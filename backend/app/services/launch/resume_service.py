"""
Resume Service for Sprint 7 Launch (BE-S7-01).
Handles Resume CRUD, KIE-assisted resume generation with anti-hallucination guardrails,
strict learner ownership, and ATS-friendly PDF export via ReportLab.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from io import BytesIO
import logging
from typing import Any, Dict, List, Optional, Set
import uuid

from fastapi import HTTPException, status
import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.core.supabase import supabase_admin
from app.schemas.launch import (
    APIError,
    CreateResumeRequest,
    GenerateResumeRequest,
    GenerateResumeResponse,
    ResumeDetailResponse,
    ResumeDraft,
    ResumeListResponse,
    ResumeRecord,
    ResumeSource,
    ResumeStatus,
    UpdateResumeRequest,
)
from app.services.event_service import event_service
from app.services.launch.career_context_service import career_context_service

logger = logging.getLogger(__name__)


class ResumeService:
    """Core service for managing, generating, and exporting user resumes."""

    @staticmethod
    def _map_row_to_record(row: Dict[str, Any]) -> ResumeRecord:
        """Converts a database row into a validated ResumeRecord schema."""
        raw_content = row.get("content") or {}
        if isinstance(raw_content, str):
            import json
            raw_content = json.loads(raw_content)

        raw_prefs = row.get("preferences")
        if isinstance(raw_prefs, str):
            import json
            raw_prefs = json.loads(raw_prefs)

        draft = ResumeDraft(**raw_content)
        return ResumeRecord(
            id=str(row["id"]),
            learner_id=str(row.get("learner_id")),
            title=row.get("title", "Untitled Resume"),
            source=ResumeSource(row.get("source", "manual")),
            status=ResumeStatus(row.get("status", "draft")),
            content=draft,
            preferences=raw_prefs if raw_prefs else None,
            provider=row.get("provider", "template"),
            created_at=str(row.get("created_at")),
            updated_at=str(row.get("updated_at")),
        )

    def list_resumes(self, learner_id: str) -> ResumeListResponse:
        """Lists all resumes owned by the specified learner."""
        try:
            res = (
                supabase_admin.table("launch_resumes")
                .select("*")
                .eq("learner_id", learner_id)
                .order("created_at", desc=True)
                .execute()
            )
            rows = res.data if res.data else []
            items = [self._map_row_to_record(r) for r in rows]
            return ResumeListResponse(items=items)
        except Exception as e:
            logger.error(f"Failed to list resumes for learner {learner_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="RESUME_LIST_FAILED",
                    message="Failed to retrieve resumes from database.",
                    details={"error": str(e)},
                ).model_dump(by_alias=True),
            )

    def create_resume(self, learner_id: str, req: CreateResumeRequest) -> ResumeDetailResponse:
        """Creates a new resume draft owned by the learner."""
        resume_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        content_dict = req.content.model_dump(by_alias=True)

        data = {
            "id": resume_id,
            "learner_id": learner_id,
            "title": req.title,
            "source": req.source.value if hasattr(req.source, "value") else str(req.source),
            "status": "draft",
            "content": content_dict,
            "preferences": {},
            "provider": "template",
            "created_at": now_str,
            "updated_at": now_str,
        }

        try:
            res = supabase_admin.table("launch_resumes").insert(data).execute()
            created_row = res.data[0] if res.data else data
        except Exception as e:
            logger.error(f"Failed to create resume for learner {learner_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="RESUME_CREATE_FAILED",
                    message="Failed to persist resume draft.",
                    details={"error": str(e)},
                ).model_dump(by_alias=True),
            )

        event_service.record_event(
            learner_id=learner_id,
            event_type="RESUME_CREATED",
            entity_type="LAUNCH_RESUME",
            entity_id=resume_id,
            payload={"title": req.title, "source": data["source"]},
        )

        return ResumeDetailResponse(resume=self._map_row_to_record(created_row))

    def get_resume(self, learner_id: str, resume_id: str) -> ResumeDetailResponse:
        """Retrieves a single resume with strict ownership verification."""
        try:
            res = (
                supabase_admin.table("launch_resumes")
                .select("*")
                .eq("id", resume_id)
                .execute()
            )
            if not res.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=APIError(
                        code="RESUME_NOT_FOUND",
                        message=f"Resume '{resume_id}' not found.",
                    ).model_dump(by_alias=True),
                )
            row = res.data[0]
            if str(row.get("learner_id")) != str(learner_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=APIError(
                        code="UNAUTHORIZED_RESUME_ACCESS",
                        message="You do not have permission to access this resume.",
                    ).model_dump(by_alias=True),
                )
            return ResumeDetailResponse(resume=self._map_row_to_record(row))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get resume {resume_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="RESUME_FETCH_FAILED",
                    message="Error retrieving resume.",
                    details={"error": str(e)},
                ).model_dump(by_alias=True),
            )

    def update_resume(self, learner_id: str, resume_id: str, req: UpdateResumeRequest) -> ResumeDetailResponse:
        """Updates an existing resume draft owned by the learner."""
        # Check ownership first
        self.get_resume(learner_id, resume_id)

        update_payload: Dict[str, Any] = {
            "content": req.content.model_dump(by_alias=True),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if req.title:
            update_payload["title"] = req.title

        try:
            res = (
                supabase_admin.table("launch_resumes")
                .update(update_payload)
                .eq("id", resume_id)
                .execute()
            )
            updated_row = res.data[0] if res.data else None
            if not updated_row:
                raise RuntimeError("Update returned no data")
        except Exception as e:
            logger.error(f"Failed to update resume {resume_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="RESUME_UPDATE_FAILED",
                    message="Failed to update resume.",
                    details={"error": str(e)},
                ).model_dump(by_alias=True),
            )

        event_service.record_event(
            learner_id=learner_id,
            event_type="RESUME_UPDATED",
            entity_type="LAUNCH_RESUME",
            entity_id=resume_id,
            payload={"title": update_payload.get("title")},
        )

        return ResumeDetailResponse(resume=self._map_row_to_record(updated_row))

    async def generate_resume(
        self, learner_id: str, req: GenerateResumeRequest, request_id: str
    ) -> GenerateResumeResponse:
        """
        Generates a tailored resume via KIE with career context grounding and anti-hallucination checks.
        If KIE is unavailable after retries, raises HTTP 502 with structured APIError.
        """
        # 1. Assemble grounding career context
        career_context = await career_context_service.assemble_career_context(learner_id)

        # 2. Build KIE generation payload
        payload = {
            "request_id": request_id,
            "learner_id": learner_id,
            "title": req.title,
            "source": req.source.value if hasattr(req.source, "value") else str(req.source),
            "content": req.content.model_dump(by_alias=True),
            "preferences": req.preferences.model_dump(by_alias=True) if req.preferences else {},
            "career_context": career_context,
        }

        # 3. Call KIE with 3 retries and 30s timeout
        kie_url = f"{settings.KIE_BASE_URL}/api/v1/kie/career/resume/generate"
        kie_response_data: Optional[Dict[str, Any]] = None
        last_error: Optional[Exception] = None

        async with httpx.AsyncClient() as client:
            for attempt in range(1, 4):
                try:
                    logger.info(f"Calling KIE Resume Generate (attempt {attempt}/3, requestId={request_id})")
                    resp = await client.post(
                        kie_url,
                        json=payload,
                        headers={"X-Request-ID": request_id, "Content-Type": "application/json"},
                        timeout=30.0,
                    )
                    resp.raise_for_status()
                    kie_response_data = resp.json()
                    break
                except Exception as exc:
                    last_error = exc
                    logger.warning(f"KIE Resume Generate attempt {attempt} failed: {exc}")
                    if attempt < 3:
                        await asyncio.sleep(1.0 * (2 ** (attempt - 1)))

        if not kie_response_data:
            # Raise HTTP 502 without touching/corrupting any existing drafts
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=APIError(
                    code="GENERATION_PROVIDER_UNAVAILABLE",
                    message="KIE Resume Generation service is currently unavailable. Please try again later.",
                    details={"error": str(last_error)},
                    request_id=request_id,
                ).model_dump(by_alias=True),
            )

        # 4. Anti-Hallucination Guardrails
        generated_content = kie_response_data.get("content") or kie_response_data
        sanitized_content = self._enforce_anti_hallucination(
            user_content=req.content,
            generated_content_dict=generated_content,
            career_context=career_context,
        )

        # 5. Persist the generated resume
        resume_id = str(uuid.uuid4())
        now_str = datetime.now(timezone.utc).isoformat()
        insert_data = {
            "id": resume_id,
            "learner_id": learner_id,
            "title": req.title,
            "source": req.source.value if hasattr(req.source, "value") else str(req.source),
            "status": "generated",
            "content": sanitized_content.model_dump(by_alias=True),
            "preferences": req.preferences.model_dump(by_alias=True) if req.preferences else {},
            "provider": "hybrid",
            "created_at": now_str,
            "updated_at": now_str,
        }

        try:
            res = supabase_admin.table("launch_resumes").insert(insert_data).execute()
            saved_row = res.data[0] if res.data else insert_data
        except Exception as e:
            logger.error(f"Failed to persist generated resume for learner {learner_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="RESUME_SAVE_FAILED",
                    message="Failed to persist generated resume.",
                    details={"error": str(e)},
                    request_id=request_id,
                ).model_dump(by_alias=True),
            )

        event_service.record_event(
            learner_id=learner_id,
            event_type="RESUME_GENERATED",
            entity_type="LAUNCH_RESUME",
            entity_id=resume_id,
            payload={"title": req.title, "provider": "hybrid"},
        )

        return GenerateResumeResponse(
            resume=self._map_row_to_record(saved_row),
            provider="hybrid",
        )

    def _enforce_anti_hallucination(
        self,
        user_content: ResumeDraft,
        generated_content_dict: Dict[str, Any],
        career_context: Dict[str, Any],
    ) -> ResumeDraft:
        """
        Anti-Hallucination verification: ensures generated institutions, companies,
        and project names do not invent entities outside user inputs and career context.
        Sanitizes or rolls back any ungrounded entities.
        """
        # Grounding sets (case-insensitive)
        valid_institutions: Set[str] = {
            edu.institution.strip().lower()
            for edu in user_content.education
            if edu.institution and edu.institution.strip()
        }
        acad = career_context.get("education") or {}
        if acad.get("university"):
            valid_institutions.add(acad["university"].strip().lower())

        valid_companies: Set[str] = {
            exp.company.strip().lower()
            for exp in user_content.experience
            if exp.company and exp.company.strip()
        }

        valid_projects: Set[str] = {
            proj.name.strip().lower()
            for proj in user_content.projects
            if proj.name and proj.name.strip()
        }
        for bp in career_context.get("career_readiness", {}).get("projects", []):
            if bp.get("title"):
                valid_projects.add(bp["title"].strip().lower())

        # Attempt to parse into draft
        try:
            draft = ResumeDraft(**generated_content_dict)
        except Exception as e:
            logger.warning(f"Failed to parse generated resume content: {e}. Fallback to user content.")
            return user_content

        # Verify education institutions
        sanitized_education = []
        for i, edu in enumerate(draft.education):
            inst_clean = edu.institution.strip().lower() if edu.institution else ""
            if inst_clean and valid_institutions:
                # Check if matches any valid institution or substring
                if not any(v in inst_clean or inst_clean in v for v in valid_institutions):
                    logger.warning(f"Anti-hallucination: Reverting hallucinated institution '{edu.institution}'")
                    fallback_inst = (
                        user_content.education[i].institution
                        if i < len(user_content.education)
                        else next(iter(valid_institutions), edu.institution)
                    )
                    edu = edu.model_copy(update={"institution": fallback_inst})
            sanitized_education.append(edu)

        # Verify experience companies
        sanitized_experience = []
        for i, exp in enumerate(draft.experience):
            comp_clean = exp.company.strip().lower() if exp.company else ""
            if comp_clean and valid_companies:
                if not any(v in comp_clean or comp_clean in v for v in valid_companies):
                    logger.warning(f"Anti-hallucination: Reverting hallucinated company '{exp.company}'")
                    fallback_comp = (
                        user_content.experience[i].company
                        if i < len(user_content.experience)
                        else next(iter(valid_companies), exp.company)
                    )
                    exp = exp.model_copy(update={"company": fallback_comp})
            sanitized_experience.append(exp)

        # Verify project names
        sanitized_projects = []
        for i, proj in enumerate(draft.projects):
            name_clean = proj.name.strip().lower() if proj.name else ""
            if name_clean and valid_projects:
                if not any(v in name_clean or name_clean in v for v in valid_projects):
                    logger.warning(f"Anti-hallucination: Reverting hallucinated project name '{proj.name}'")
                    fallback_proj = (
                        user_content.projects[i].name
                        if i < len(user_content.projects)
                        else next(iter(valid_projects), proj.name)
                    )
                    proj = proj.model_copy(update={"name": fallback_proj})
            sanitized_projects.append(proj)

        return draft.model_copy(
            update={
                "education": sanitized_education,
                "experience": sanitized_experience,
                "projects": sanitized_projects,
            }
        )

    def export_resume_pdf(self, learner_id: str, resume_id: str) -> bytes:
        """
        Renders an owned resume into a clean, ATS-friendly PDF stream using ReportLab.
        Guarantees that rendering errors raise HTTP 500 without corrupting the saved resume.
        """
        # Fetch resume & verify ownership
        resume_resp = self.get_resume(learner_id, resume_id)
        draft = resume_resp.resume.content

        buffer = BytesIO()
        try:
            # ATS Best Practice: standard letter size, 0.5-0.75in margins, single-column flow
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                leftMargin=40,
                rightMargin=40,
                topMargin=40,
                bottomMargin=40,
            )

            styles = getSampleStyleSheet()

            # Custom ATS-compliant typography styles
            name_style = ParagraphStyle(
                "ATSName",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#0f172a"),
                alignment=1,  # Centered
            )

            contact_style = ParagraphStyle(
                "ATSContact",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#475569"),
                alignment=1,  # Centered
            )

            section_heading_style = ParagraphStyle(
                "ATSSectionHeading",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#1e293b"),
                spaceBefore=10,
                spaceAfter=3,
                keepWithNext=True,
            )

            subheading_style = ParagraphStyle(
                "ATSSubHeading",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#1e293b"),
            )

            date_style = ParagraphStyle(
                "ATSDate",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor("#64748b"),
                alignment=2,  # Right aligned
            )

            body_style = ParagraphStyle(
                "ATSBody",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#334155"),
            )

            bullet_style = ParagraphStyle(
                "ATSBullet",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#334155"),
                leftIndent=14,
                firstLineIndent=-10,
            )

            story = []

            # 1. Header (Full Name + Contact Details)
            full_name = draft.contact.full_name or "Resume"
            story.append(Paragraph(full_name, name_style))
            story.append(Spacer(1, 4))

            contact_parts = []
            if draft.contact.email:
                contact_parts.append(draft.contact.email)
            if draft.contact.phone:
                contact_parts.append(draft.contact.phone)
            if draft.contact.location:
                contact_parts.append(draft.contact.location)
            if draft.contact.linked_in_url:
                contact_parts.append(draft.contact.linked_in_url)
            if draft.contact.github_url:
                contact_parts.append(draft.contact.github_url)
            if draft.contact.portfolio_url:
                contact_parts.append(draft.contact.portfolio_url)

            if contact_parts:
                story.append(Paragraph(" | ".join(contact_parts), contact_style))
                story.append(Spacer(1, 8))

            # Helper for section dividers
            def add_section_header(title: str):
                story.append(Paragraph(title.upper(), section_heading_style))
                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.75,
                        color=colors.HexColor("#cbd5e1"),
                        spaceBefore=1,
                        spaceAfter=6,
                    )
                )

            # 2. Professional Summary
            if draft.summary or draft.headline:
                add_section_header("Professional Summary")
                if draft.headline and draft.headline != draft.summary:
                    story.append(Paragraph(f"<b>{draft.headline}</b>", subheading_style))
                    story.append(Spacer(1, 2))
                if draft.summary:
                    story.append(Paragraph(draft.summary, body_style))
                story.append(Spacer(1, 6))

            # 3. Technical & Core Skills
            if draft.skills:
                add_section_header("Technical Skills")
                skills_text = ", ".join(draft.skills)
                story.append(Paragraph(skills_text, body_style))
                story.append(Spacer(1, 6))

            # 4. Work Experience
            if draft.experience:
                add_section_header("Experience")
                for exp in draft.experience:
                    role_text = f"<b>{exp.role}</b>" if exp.role else "Role"
                    company_text = f" | {exp.company}" if exp.company else ""
                    title_cell = Paragraph(f"{role_text}{company_text}", subheading_style)

                    dates = []
                    if exp.start_date:
                        dates.append(exp.start_date)
                    if exp.is_current:
                        dates.append("Present")
                    elif exp.end_date:
                        dates.append(exp.end_date)
                    date_cell = Paragraph(" – ".join(dates) if dates else "", date_style)

                    row_table = Table([[title_cell, date_cell]], colWidths=[400, 130])
                    row_table.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(row_table)

                    if exp.description:
                        lines = [l.strip() for l in exp.description.split("\n") if l.strip()]
                        for l in lines:
                            bullet_text = f"• {l.lstrip('•-* ')}"
                            story.append(Paragraph(bullet_text, bullet_style))
                    story.append(Spacer(1, 6))

            # 5. Projects
            if draft.projects:
                add_section_header("Projects")
                for proj in draft.projects:
                    proj_name = f"<b>{proj.name}</b>"
                    tech_str = f" <i>({', '.join(proj.technologies)})</i>" if proj.technologies else ""
                    name_cell = Paragraph(f"{proj_name}{tech_str}", subheading_style)

                    p_dates = []
                    if proj.start_date:
                        p_dates.append(proj.start_date)
                    if proj.end_date:
                        p_dates.append(proj.end_date)
                    date_cell = Paragraph(" – ".join(p_dates) if p_dates else "", date_style)

                    p_table = Table([[name_cell, date_cell]], colWidths=[400, 130])
                    p_table.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(p_table)

                    if proj.description:
                        lines = [l.strip() for l in proj.description.split("\n") if l.strip()]
                        for l in lines:
                            story.append(Paragraph(f"• {l.lstrip('•-* ')}", bullet_style))
                    if proj.project_url:
                        story.append(Paragraph(f"Link: {proj.project_url}", contact_style))
                    story.append(Spacer(1, 6))

            # 6. Education
            if draft.education:
                add_section_header("Education")
                for edu in draft.education:
                    degree_major = []
                    if edu.degree:
                        degree_major.append(edu.degree)
                    if edu.field_of_study:
                        degree_major.append(edu.field_of_study)
                    title_text = f"<b>{', '.join(degree_major)}</b>" if degree_major else "<b>Degree</b>"
                    inst_text = f" | {edu.institution}" if edu.institution else ""
                    edu_cell = Paragraph(f"{title_text}{inst_text}", subheading_style)

                    dates = []
                    if edu.start_date:
                        dates.append(edu.start_date)
                    if edu.end_date:
                        dates.append(edu.end_date)
                    date_cell = Paragraph(" – ".join(dates) if dates else "", date_style)

                    edu_table = Table([[edu_cell, date_cell]], colWidths=[400, 130])
                    edu_table.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(edu_table)

                    if edu.grade:
                        story.append(Paragraph(f"Grade / GPA: {edu.grade}", body_style))
                    story.append(Spacer(1, 4))

            # 7. Achievements & Certifications
            if draft.achievements:
                add_section_header("Achievements & Evidence")
                for ach in draft.achievements:
                    title_cell = Paragraph(f"<b>{ach.title}</b>", subheading_style)
                    date_cell = Paragraph(ach.date or "", date_style)

                    ach_table = Table([[title_cell, date_cell]], colWidths=[420, 110])
                    ach_table.setStyle(
                        TableStyle([
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ])
                    )
                    story.append(ach_table)
                    if ach.description:
                        story.append(Paragraph(f"• {ach.description.lstrip('•-* ')}", bullet_style))
                    story.append(Spacer(1, 4))

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            return pdf_bytes

        except Exception as e:
            logger.error(f"Failed to generate resume PDF for resume_id={resume_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIError(
                    code="EXPORT_FAILED",
                    message="Failed to render ATS resume PDF.",
                    details={"error": str(e)},
                ).model_dump(by_alias=True),
            )
        finally:
            buffer.close()


resume_service = ResumeService()

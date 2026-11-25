import uuid
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from app.core.config import settings
from app.core.supabase import supabase_admin
from app.core.context_v2_assembler import ContextV2Assembler
from app.services.content_reference_service import content_reference_service
from app.services.learning_session_service import learning_session_service
from app.schemas.learning import Lesson, ContentReferenceQuery, LearningSessionCreate, LearningSessionUpdate

logger = logging.getLogger(__name__)

_BANNED_CS_FALLBACK_PHRASES = (
    "foundational software engineer",
    "core conceptual architecture",
    "guided engineering practice",
    "system topology & data flow map",
    "structural invariants",
    "asymptotic complexity",
    "production-grade implementation",
    "state invariants",
)

_CS_KEYWORDS = (
    "computer science",
    "software engineering",
    "information technology",
    "data structures",
    "algorithms",
    "python",
    "java",
    "javascript",
    "typescript",
    "database",
    "dbms",
    "sql",
    "operating system",
    "computer network",
    "machine learning",
    "artificial intelligence",
    "compiler",
    "web development",
    "programming",
    "coding",
    "b.tech",
    "bca",
    "mca",
)

_NON_CS_OFFICE_IT_KEYWORDS = (
    "computer applications in business",
    "computer application in business",
    "office automation",
    "business computing",
)


def _is_cs_context(subject: Optional[str], degree_program: Optional[str], academic_domain: Optional[str]) -> bool:
    """Return True only when the subject/program indicates an actual CS/coding course."""
    subj_l = (subject or "").lower()
    if any(k in subj_l for k in _NON_CS_OFFICE_IT_KEYWORDS):
        return False
    combined = f"{subject or ''} {degree_program or ''} {academic_domain or ''}".lower()
    return any(kw in combined for kw in _CS_KEYWORDS)


def _violates_non_cs_guard(
    lesson_resp: Dict[str, Any],
    subject: Optional[str],
    degree_program: Optional[str],
    academic_domain: Optional[str],
) -> Optional[str]:
    """Check whether a non-CS lesson response contains CODE blocks or banned CS fallback strings."""
    if _is_cs_context(subject, degree_program, academic_domain):
        return None
    blocks = lesson_resp.get("blocks") or []
    for blk in blocks:
        if not isinstance(blk, dict):
            continue
        blk_type = str(blk.get("type", "")).strip().upper()
        if blk_type == "CODE":
            return f"block '{blk.get('id') or blk.get('title')}' has type CODE"
        text_blob = f"{blk.get('title') or ''} {blk.get('content') or ''}".lower()
        for phrase in _BANNED_CS_FALLBACK_PHRASES:
            if phrase in text_blob:
                return f"banned CS fallback phrase '{phrase}'"
    return None


class KIEGatewayService:
    @staticmethod
    async def _request_with_retry(client: httpx.AsyncClient, url: str, payload: dict, max_retries: int = 3) -> dict:
        base_delay = 1.0
        timeout_config = httpx.Timeout(60.0, connect=10.0)
        for attempt in range(max_retries):
            try:
                response = await client.post(url, json=payload, timeout=timeout_config)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                if attempt == max_retries - 1:
                    raise HTTPException(status_code=502, detail=f"KIE Service Error after retries: {str(e)}")
                await asyncio.sleep(base_delay * (2 ** attempt))
        raise HTTPException(status_code=502, detail="KIE Service Error")

    @staticmethod
    def _resolve_session_metadata(
        learner_id: str,
        session: Dict[str, Any],
        payload: Dict[str, Any],
    ) -> tuple[Optional[str], Optional[str]]:
        """Resolve syllabus_id and subject from payload, session, mission/roadmap, or confirmed syllabus."""
        syllabus_id = payload.get("syllabus_id") or session.get("syllabus_id")
        subject = payload.get("subject") or session.get("subject")

        if not subject and session.get("mission_id"):
            try:
                m_res = supabase_admin.table("missions").select("subject").eq("id", str(session["mission_id"])).limit(1).execute()
                if m_res and m_res.data:
                    subject = m_res.data[0].get("subject")
            except Exception:
                pass

        if not syllabus_id and session.get("roadmap_id"):
            try:
                r_res = supabase_admin.table("roadmaps").select("syllabus_id, subject").eq("id", str(session["roadmap_id"])).limit(1).execute()
                if r_res and r_res.data:
                    syllabus_id = syllabus_id or r_res.data[0].get("syllabus_id")
                    subject = subject or r_res.data[0].get("subject")
            except Exception:
                pass

        if not syllabus_id:
            try:
                s_res = (
                    supabase_admin.table("syllabus_documents")
                    .select("id")
                    .eq("learner_id", learner_id)
                    .eq("status", "CONFIRMED")
                    .order("confirmed_at", desc=True)
                    .limit(1)
                    .execute()
                )
                if s_res and s_res.data:
                    syllabus_id = s_res.data[0].get("id")
            except Exception:
                pass

        return (str(syllabus_id) if syllabus_id else None, subject)

    @staticmethod
    async def generate_lesson(
        learner_id: str, 
        session_id: str, 
        request_id: str, 
        payload: Dict[str, Any]
    ) -> Lesson:
        """
        Orchestrates the KIE learning gateway pipeline.
        """
        # Fetch the session
        session = learning_session_service.get_session(session_id, learner_id)
        
        # If already generated, return cached lesson to resume unless explicitly asked to force regenerate
        if session.get("lesson_data") and not payload.get("force_regenerate"):
            try:
                return Lesson(**session["lesson_data"])
            except Exception:
                pass

        # Resolve syllabus_id and subject from session / roadmap / mission / confirmed syllabus
        syllabus_id, subject = KIEGatewayService._resolve_session_metadata(learner_id, session, payload)

        # Assemble context with target_subject and syllabus
        context = await ContextV2Assembler.assemble(
            learner_id,
            syllabus_id=syllabus_id,
            target_subject=subject,
        )
        education = context.get("education") or {}
        degree_program = payload.get("degree_program") or education.get("degree_program")
        academic_domain = payload.get("academic_domain") or payload.get("domain") or education.get("domain")

        # Grounding references
        references: List[Dict[str, Any]] = []
        if syllabus_id:
            query = ContentReferenceQuery(
                syllabus_id=syllabus_id,
                topic=session.get("topic", ""),
                keywords=payload.get("keywords", [])
            )
            ref_resp = content_reference_service.get_references(query)
            references = ref_resp.references
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            # Step 1: Call AI-1 Interpret
            interpret_payload = {
                "request_id": request_id,
                "learner_id": learner_id,
                "context": context,
                "topic": session.get("topic"),
                "subject": subject,
                "degree_program": degree_program,
                "academic_domain": academic_domain,
                "references": references,
                "user_intent": payload.get("user_intent", "")
            }
            interpret_resp = await KIEGatewayService._request_with_retry(
                client,
                f"{settings.KIE_BASE_URL}/api/v1/kie/learn/interpret",
                interpret_payload
            )
            
            # Step 2: Call AI-2 Generate
            generate_payload = {
                "request_id": request_id,
                "learner_id": learner_id,
                "interpreted_data": interpret_resp,
                "context": context,
                "references": references,
                "topic": session.get("topic"),
                "subject": subject,
                "degree_program": degree_program,
                "academic_domain": academic_domain,
                "lesson_id": session.get("lesson_id")
            }
            ai2_base_url = settings.KIE_AI2_BASE_URL or settings.KIE_BASE_URL
            generate_resp = await KIEGatewayService._request_with_retry(
                client,
                f"{ai2_base_url}/api/v1/kie/lesson/generate",
                generate_payload
            )

            # Pre-Persist Domain Guard: retry once with strict domain constraints if non-CS leaked CS/code
            violation = _violates_non_cs_guard(generate_resp, subject, degree_program, academic_domain)
            if violation:
                logger.warning(
                    f"Non-CS domain guard triggered for session={session_id}, subject='{subject}', "
                    f"reason={violation}. Retrying lesson generation with strict domain constraints."
                )
                retry_payload = dict(generate_payload)
                retry_payload["strict_domain_constraints"] = True
                retry_payload["forbid_code_blocks"] = True
                retry_payload["user_intent"] = (
                    f"{payload.get('user_intent', '')} "
                    f"[STRICT DOMAIN GUARD: Subject '{subject or session.get('topic')}' is in '{degree_program or academic_domain or 'Non-CS'}'. "
                    "Do NOT emit code blocks, Python classes, database schemas, or software engineering templates.]"
                ).strip()
                generate_resp = await KIEGatewayService._request_with_retry(
                    client,
                    f"{ai2_base_url}/api/v1/kie/lesson/generate",
                    retry_payload
                )
            
            # Step 3: Validate against Pydantic model (preserving raw Markdown & Mermaid verbatim)
            try:
                lesson = Lesson(**generate_resp)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Invalid lesson format returned from KIE: {str(e)}")
            
            # Persist lesson in session - Web BUG-04: Default to Step 1 (blocks[0]), never the last block
            first_block_id = lesson.blocks[0].id if lesson.blocks else None
            existing_cp = session.get("checkpoint_block_id")
            valid_block_ids = {b.id for b in lesson.blocks} if lesson.blocks else set()
            checkpoint_id = existing_cp if (existing_cp and existing_cp in valid_block_ids) else first_block_id

            learning_session_service.update_checkpoint(
                session_id, 
                learner_id, 
                LearningSessionUpdate(
                    checkpoint_block_id=checkpoint_id,
                    progress_percentage=0 if not existing_cp else session.get("progress_percentage", 0),
                    lesson_data=lesson.model_dump()
                )
            )
            
            return lesson

kie_gateway_service = KIEGatewayService()

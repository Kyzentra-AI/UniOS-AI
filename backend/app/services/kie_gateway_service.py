import uuid
import asyncio
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.core.config import settings
from app.core.context_v2_assembler import ContextV2Assembler
from app.services.content_reference_service import content_reference_service
from app.services.learning_session_service import learning_session_service
from app.schemas.learning import Lesson, ContentReferenceQuery, LearningSessionCreate

class KIEGatewayService:
    @staticmethod
    async def _request_with_retry(client: httpx.AsyncClient, url: str, payload: dict, max_retries: int = 3) -> dict:
        base_delay = 1.0
        timeout_config = httpx.Timeout(45.0, connect=10.0)
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

        # Assemble context
        syllabus_id = payload.get("syllabus_id")
        context = await ContextV2Assembler.assemble(learner_id, syllabus_id=syllabus_id)
        
        # Grounding
        references = []
        if syllabus_id:
            query = ContentReferenceQuery(
                syllabus_id=syllabus_id,
                topic=session.get("topic", ""),
                keywords=payload.get("keywords", [])
            )
            ref_resp = content_reference_service.get_references(query)
            references = ref_resp.references
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0)) as client:
            # Step 1: Call AI-1 Interpret
            interpret_payload = {
                "request_id": request_id,
                "learner_id": learner_id,
                "context": context,
                "topic": session.get("topic"),
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
                "lesson_id": session.get("lesson_id")
            }
            ai2_base_url = settings.KIE_AI2_BASE_URL or settings.KIE_BASE_URL
            generate_resp = await KIEGatewayService._request_with_retry(
                client,
                f"{ai2_base_url}/api/v1/kie/lesson/generate",
                generate_payload
            )
            
            # Step 3: Validate against Pydantic model
            try:
                lesson = Lesson(**generate_resp)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Invalid lesson format returned from KIE: {str(e)}")
            
            # Persist lesson in session - Web BUG-04: Default to Step 1 (blocks[0]), never the last block
            from app.schemas.learning import LearningSessionUpdate
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

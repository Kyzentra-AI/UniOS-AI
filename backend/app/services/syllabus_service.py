import hashlib
import httpx
from app.core.supabase import supabase_admin
from app.services.pdf_service import extract_text_from_pdf
from app.services.kie_service import kie_service
from app.schemas.billing import CreditOperation
from app.schemas.syllabus import ParsedContent
from app.services.billing.billing_guard import billing_guard
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class SyllabusService:
    @staticmethod
    async def process_syllabus_background(syllabus_id: str, file_bytes: bytes, file_hash: str | None = None):
        try:
            # PERF-03: Compute file hash if not passed
            sha256_hash = file_hash or hashlib.sha256(file_bytes).hexdigest()

            # Check if this learner already has identical parsed content cached
            doc_res = supabase_admin.table("syllabus_documents").select("learner_id").eq("id", syllabus_id).execute()
            learner_id = doc_res.data[0]["learner_id"] if doc_res.data else None

            if learner_id:
                cached = (
                    supabase_admin.table("syllabus_documents")
                    .select("parsed_content")
                    .eq("learner_id", learner_id)
                    .eq("file_hash", sha256_hash)
                    .neq("id", syllabus_id)
                    .not_.is_("parsed_content", "null")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                if cached.data and cached.data[0].get("parsed_content"):
                    supabase_admin.table("syllabus_documents").update({
                        "file_hash": sha256_hash,
                        "parsed_content": cached.data[0]["parsed_content"],
                        "status": "WAITING_FOR_CONFIRMATION"
                    }).eq("id", syllabus_id).execute()
                    logger.info(f"Reused cached parsed syllabus for hash {sha256_hash}")
                    return

            # 1. Charge LEARN credits on cache miss and extract text + call KIE
            ledger_id = billing_guard.authorize_and_consume(
                learner_id=learner_id,
                operation=CreditOperation.SYLLABUS_ANALYSIS,
                reference_id=syllabus_id,
            ) if learner_id else None

            try:
                text = extract_text_from_pdf(file_bytes)
                parsed_data = await kie_service.extract_syllabus(syllabus_id, text)
                if not parsed_data:
                    raise Exception("Failed to extract syllabus from AI/ML")
                validated_content = ParsedContent(**parsed_data)
            except Exception:
                billing_guard.refund(ledger_id)
                raise
            
            # 4. Save to DB with file_hash
            supabase_admin.table("syllabus_documents").update({
                "file_hash": sha256_hash,
                "parsed_content": validated_content.model_dump(),
                "status": "WAITING_FOR_CONFIRMATION"
            }).eq("id", syllabus_id).execute()
            
        except ValidationError as ve:
            logger.error(f"Validation error for syllabus {syllabus_id}: {ve}")
            supabase_admin.table("syllabus_documents").update({
                "status": "FAILED"
            }).eq("id", syllabus_id).execute()
        except Exception as e:
            logger.error(f"Error processing syllabus {syllabus_id}: {e}")
            supabase_admin.table("syllabus_documents").update({
                "status": "FAILED"
            }).eq("id", syllabus_id).execute()

    @staticmethod
    async def reprocess_syllabus_background(syllabus_id: str, file_url: str):
        try:
            # Fetch file bytes from storage URL
            async with httpx.AsyncClient() as client:
                res = await client.get(file_url)
                res.raise_for_status()
                file_bytes = res.content
                
            await SyllabusService.process_syllabus_background(syllabus_id, file_bytes)
            
        except Exception as e:
            logger.error(f"Error reprocessing syllabus {syllabus_id}: {e}")
            # Keep previous valid content if we fail to reprocess, or mark failed if there was none.
            # "Do not replace a valid existing confirmed syllabus because of a failed re-processing attempt."

syllabus_service = SyllabusService()

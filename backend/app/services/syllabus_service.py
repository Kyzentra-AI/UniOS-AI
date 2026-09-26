import httpx
from app.core.supabase import supabase_admin
from app.services.pdf_service import extract_text_from_pdf
from app.services.kie_service import kie_service
from app.schemas.syllabus import ParsedContent
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class SyllabusService:
    @staticmethod
    async def process_syllabus_background(syllabus_id: str, file_bytes: bytes):
        try:
            # 1. Extract text from PDF
            text = extract_text_from_pdf(file_bytes)
            
            # 2. Call AI/ML for extraction
            parsed_data = await kie_service.extract_syllabus(syllabus_id, text)
            
            if not parsed_data:
                raise Exception("Failed to extract syllabus from AI/ML")
                
            # 3. Validate response
            validated_content = ParsedContent(**parsed_data)
            
            # 4. Save to DB
            supabase_admin.table("syllabus_documents").update({
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

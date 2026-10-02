from uuid import UUID
from typing import List, Dict, Any
from app.core.supabase import supabase_admin
from app.schemas.learning import ContentReferenceQuery, ContentReferenceResponse

class ContentReferenceService:
    @staticmethod
    def get_references(query: ContentReferenceQuery) -> ContentReferenceResponse:
        """
        Extract relevant topic slices from syllabus_documents.parsed_content for grounding.
        """
        syllabus_id = str(query.syllabus_id)
        res = supabase_admin.table("syllabus_documents").select("parsed_content").eq("id", syllabus_id).execute()
        
        if not res.data:
            return ContentReferenceResponse(topic=query.topic, references=[])
            
        parsed_content = res.data[0].get("parsed_content", {})
        references = []
        
        # In a real scenario, this might do semantic search or structured extraction
        # Here we just naively extract if the topic or keywords match structure
        if isinstance(parsed_content, list):
            for block in parsed_content:
                text_content = str(block).lower()
                topic_match = query.topic.lower() in text_content
                keyword_match = query.keywords and any(kw.lower() in text_content for kw in query.keywords)
                
                if topic_match or keyword_match:
                    references.append(block)
        elif isinstance(parsed_content, dict):
            # Try to see if there's a matching key or section
            for key, value in parsed_content.items():
                if query.topic.lower() in key.lower():
                    references.append({key: value})
        
        return ContentReferenceResponse(
            topic=query.topic,
            references=references
        )

content_reference_service = ContentReferenceService()

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
            subjects = parsed_content.get("subjects")
            if isinstance(subjects, list):
                topic_lower = query.topic.lower()
                kw_lowers = [kw.lower() for kw in (query.keywords or []) if kw]
                for subj in subjects:
                    if not isinstance(subj, dict):
                        continue
                    subj_name = str(subj.get("name", ""))
                    # Match chapter-level topics
                    for ch in subj.get("chapters") or []:
                        if not isinstance(ch, dict):
                            continue
                        ch_title = str(ch.get("title") or ch.get("name") or "")
                        ch_topics = ch.get("topics") or []
                        ch_blob = f"{subj_name} {ch_title} {ch_topics}".lower()
                        if topic_lower in ch_blob or any(kw in ch_blob for kw in kw_lowers):
                            references.append({
                                "subject": subj_name,
                                "module": ch_title,
                                "heading": ch_title,
                                "content": f"{subj_name} — {ch_title}: {', '.join(str(t) for t in ch_topics)}",
                            })
                    # Match flat subject topics if no chapter matched
                    subj_topics = subj.get("topics") or []
                    for t in subj_topics:
                        t_str = str(t.get("name") or t.get("title") if isinstance(t, dict) else t)
                        t_lower = t_str.lower()
                        if topic_lower in t_lower or t_lower in topic_lower or any(kw in t_lower for kw in kw_lowers):
                            references.append({
                                "subject": subj_name,
                                "heading": t_str,
                                "content": f"{subj_name}: {t_str}",
                            })
            # Fallback: check top-level keys
            if not references:
                for key, value in parsed_content.items():
                    if query.topic.lower() in key.lower():
                        references.append({key: value})
        
        return ContentReferenceResponse(
            topic=query.topic,
            references=references
        )

content_reference_service = ContentReferenceService()

from app.core.supabase import supabase_admin
from app.services.kie_service import kie_service
from app.core.context_v2_assembler import ContextV2Assembler
from app.schemas.roadmap import AIMLRoadmapResponse
from app.services.event_service import event_service
from pydantic import ValidationError
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class RoadmapService:
    @staticmethod
    async def generate_roadmap_background(
        learner_id: str, 
        scope: str, 
        syllabus_id: str, 
        target_subject: Optional[str] = None
    ):
        try:
            # 1. Assemble Context V2 with target_subject
            context_v2 = await ContextV2Assembler.assemble(
                learner_id, scope, syllabus_id, target_subject=target_subject
            )
            
            # 2. Call KIE 2
            roadmap_data = await kie_service.generate_roadmap(context_v2)
            
            if not roadmap_data:
                raise Exception("Failed to generate roadmap from KIE 2")
                
            # 3. Validate
            validated_roadmap = AIMLRoadmapResponse(**roadmap_data)
            
            # 4. Save Version
            # Inactivate only the current active roadmap for this scope & subject (or master)
            deact_query = (
                supabase_admin.table("roadmaps")
                .update({
                    "status": "INACTIVE",
                    "updated_at": datetime.utcnow().isoformat()
                })
                .eq("learner_id", learner_id)
                .eq("scope", scope)
                .eq("status", "ACTIVE")
            )
            if target_subject:
                deact_query = deact_query.eq("subject", target_subject)
            else:
                deact_query = deact_query.is_("subject", "null")
            deact_query.execute()
            
            # 5. Determine version for this subject track / master roadmap
            ver_query = (
                supabase_admin.table("roadmaps")
                .select("version")
                .eq("learner_id", learner_id)
                .eq("scope", scope)
            )
            if target_subject:
                ver_query = ver_query.eq("subject", target_subject)
            else:
                ver_query = ver_query.is_("subject", "null")
            res = ver_query.order("version", desc=True).limit(1).execute()
            next_version = (res.data[0]["version"] + 1) if res.data else 1
                
            # 6. Insert new active roadmap
            new_roadmap_data = {
                "learner_id": learner_id,
                "syllabus_id": syllabus_id,
                "version": next_version,
                "scope": scope,
                "subject": target_subject,
                "status": "ACTIVE",
                "plan_data": validated_roadmap.model_dump()
            }
            new_roadmap_res = supabase_admin.table("roadmaps").insert(new_roadmap_data).execute()
            new_roadmap_id = new_roadmap_res.data[0]["id"]
            
            # 7. Insert Missions with guaranteed subject tag
            missions_to_insert = []
            for m in validated_roadmap.missions:
                mission_type_val = m.type.value if hasattr(m.type, "value") else str(m.type)
                missions_to_insert.append({
                    "roadmap_id": new_roadmap_id,
                    "title": m.title,
                    "description": m.description,
                    "mission_type": mission_type_val,
                    "subject": m.subject or target_subject or "General",
                    "priority": m.priority,
                    "estimated_minutes": m.estimated_minutes,
                    "week": m.week,
                    "sequence": m.sequence,
                    "status": "PENDING"
                })
                
            if missions_to_insert:
                supabase_admin.table("missions").insert(missions_to_insert).execute()
                
            # 8. Record Event
            event_type = "ROADMAP_CREATED" if next_version == 1 else "ROADMAP_UPDATED"
            event_service.record_event(
                learner_id=learner_id,
                event_type=event_type,
                entity_type="ROADMAP",
                entity_id=new_roadmap_id
            )
            logger.info(f"Successfully generated roadmap {new_roadmap_id} for subject '{target_subject or 'ALL'}'")
            
        except ValidationError as ve:
            logger.error(f"Validation error for roadmap generation for {learner_id}: {ve}", exc_info=True)
        except Exception as e:
            logger.error(f"Error generating roadmap for {learner_id}: {e}", exc_info=True)

roadmap_service = RoadmapService()

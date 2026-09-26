from app.core.supabase import supabase_admin
from app.services.kie_service import kie_service
from app.core.context_v2_assembler import ContextV2Assembler
from app.schemas.roadmap import AIMLRoadmapResponse
from app.services.event_service import event_service
from pydantic import ValidationError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RoadmapService:
    @staticmethod
    async def generate_roadmap_background(learner_id: str, scope: str, syllabus_id: str):
        try:
            # 1. Assemble Context V2
            context_v2 = await ContextV2Assembler.assemble(learner_id, scope, syllabus_id)
            
            # 2. Call AI/ML-1
            roadmap_data = await kie_service.generate_roadmap(context_v2)
            
            if not roadmap_data:
                raise Exception("Failed to generate roadmap from AI/ML-1")
                
            # 3. Validate
            validated_roadmap = AIMLRoadmapResponse(**roadmap_data)
            
            # 4. Save Version
            # Inactive current active roadmaps for this scope
            supabase_admin.table("roadmaps").update({
                "status": "INACTIVE",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("learner_id", learner_id).eq("scope", scope).eq("status", "ACTIVE").execute()
            
            # Get latest version number
            res = supabase_admin.table("roadmaps").select("version").eq("learner_id", learner_id).eq("scope", scope).order("version", desc=True).limit(1).execute()
            next_version = 1
            if res.data:
                next_version = res.data[0]["version"] + 1
                
            # Insert new active roadmap
            new_roadmap_data = {
                "learner_id": learner_id,
                "version": next_version,
                "scope": scope,
                "status": "ACTIVE",
                "plan_data": validated_roadmap.model_dump()
            }
            new_roadmap_res = supabase_admin.table("roadmaps").insert(new_roadmap_data).execute()
            new_roadmap_id = new_roadmap_res.data[0]["id"]
            
            # 5. Insert Missions
            missions_to_insert = []
            for m in validated_roadmap.missions:
                missions_to_insert.append({
                    "roadmap_id": new_roadmap_id,
                    "title": m.title,
                    "description": m.description,
                    "mission_type": m.type.value,
                    "subject": m.subject,
                    "priority": m.priority,
                    "estimated_minutes": m.estimated_minutes,
                    "week": m.week,
                    "sequence": m.sequence,
                    "status": "PENDING"
                })
                
            if missions_to_insert:
                supabase_admin.table("missions").insert(missions_to_insert).execute()
                
            # 6. Record Event
            event_type = "ROADMAP_CREATED" if next_version == 1 else "ROADMAP_UPDATED"
            event_service.record_event(
                learner_id=learner_id,
                event_type=event_type,
                entity_type="ROADMAP",
                entity_id=new_roadmap_id
            )
            
        except ValidationError as ve:
            logger.error(f"Validation error for roadmap generation for {learner_id}: {ve}")
            # Keep existing roadmap unchanged
        except Exception as e:
            logger.error(f"Error generating roadmap for {learner_id}: {e}")
            # Keep existing roadmap unchanged

roadmap_service = RoadmapService()

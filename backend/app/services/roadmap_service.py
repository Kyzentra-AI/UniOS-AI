import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from app.core.context_v2_assembler import ContextV2Assembler
from app.core.supabase import supabase_admin
from app.schemas.roadmap import AIMLRoadmapResponse, MissionType, RoadmapMission
from app.services.event_service import event_service
from app.services.kie_service import kie_service

logger = logging.getLogger(__name__)


def _extract_topic_names(subject_entry: Dict[str, Any]) -> List[str]:
    """Extract normalized topic names from a parsed syllabus subject entry."""
    topics: List[str] = []
    for t in subject_entry.get("topics") or []:
        name = t.get("name") or t.get("title") if isinstance(t, dict) else str(t)
        if name and str(name).strip():
            topics.append(str(name).strip())
    for ch in subject_entry.get("chapters") or []:
        if isinstance(ch, dict):
            for t in ch.get("topics") or []:
                name = t.get("name") or t.get("title") if isinstance(t, dict) else str(t)
                if name and str(name).strip() and str(name).strip() not in topics:
                    topics.append(str(name).strip())
    return topics


class RoadmapService:
    @staticmethod
    def _ensure_topic_coverage(
        missions: List[RoadmapMission],
        subjects: List[Dict[str, Any]],
        target_subject: Optional[str] = None,
    ) -> List[RoadmapMission]:
        """Verify 100% of confirmed syllabus topics map to at least one mission."""
        target_norm = target_subject.strip().lower() if target_subject else None
        relevant_subjects = [
            s for s in subjects
            if isinstance(s, dict)
            and s.get("name")
            and (not target_norm or s["name"].strip().lower() == target_norm)
        ]
        if not relevant_subjects:
            return missions

        covered_missions = list(missions)
        for subj in relevant_subjects:
            subj_name = subj["name"].strip()
            subj_missions = [
                m for m in covered_missions
                if (m.subject or "").strip().lower() == subj_name.lower()
            ]
            searchable_blobs = [
                f"{m.topic or ''} {m.title} {m.description}".lower()
                for m in subj_missions
            ]
            for topic_name in _extract_topic_names(subj):
                t_lower = topic_name.lower()
                if any(t_lower in blob for blob in searchable_blobs):
                    continue
                logger.warning(
                    f"Coverage gate adding missing LEARNING mission for subject='{subj_name}', topic='{topic_name}'"
                )
                objectives = f"Understand core principles and applications of {topic_name}."
                core_concepts = f"Foundational definitions, frameworks, and key concepts of {topic_name}."
                deliverables = f"Structured study notes and concept summary for {topic_name}."
                mastery_criteria = f"Explain {topic_name} accurately and apply it to domain scenarios."
                covered_missions.append(
                    RoadmapMission(
                        title=f"Master {topic_name}",
                        type=MissionType.LEARNING,
                        description=(
                            f"Objectives: {objectives}\n"
                            f"Core Concepts: {core_concepts}\n"
                            f"Deliverables: {deliverables}\n"
                            f"Mastery Criteria: {mastery_criteria}"
                        ),
                        priority="MEDIUM",
                        estimated_minutes=60,
                        subject=subj_name,
                        topic=topic_name,
                        objectives=objectives,
                        core_concepts=core_concepts,
                        deliverables=deliverables,
                        mastery_criteria=mastery_criteria,
                        week=1,
                        sequence=len(covered_missions) + 1,
                    )
                )
        return covered_missions

    @staticmethod
    def _distribute_and_order_missions(
        missions: List[RoadmapMission],
        total_weeks: int = 16,
    ) -> List[RoadmapMission]:
        """Deterministically assign week (1..total_weeks) and global sequence (1..N)."""
        if not missions:
            return []

        # Preserve relative progression without grouping by mission_type
        ordered = sorted(
            enumerate(missions),
            key=lambda item: (item[1].week or 1, item[1].sequence or (item[0] + 1), item[0]),
        )
        total = len(ordered)
        effective_weeks = max(1, min(total_weeks, total))

        result: List[RoadmapMission] = []
        for idx, (_, mission) in enumerate(ordered):
            assigned_week = min(effective_weeks, (idx * effective_weeks) // total + 1)
            result.append(
                mission.model_copy(
                    update={
                        "week": assigned_week,
                        "sequence": idx + 1,
                    }
                )
            )
        return result

    @staticmethod
    async def generate_roadmap_background(
        learner_id: str,
        scope: str,
        syllabus_id: str,
        target_subject: Optional[str] = None,
    ):
        try:
            # Fetch confirmed syllabus subjects for per-subject orchestration & coverage validation
            syl_res = (
                supabase_admin.table("syllabus_documents")
                .select("parsed_content")
                .eq("id", syllabus_id)
                .execute()
            )
            parsed_content = (
                syl_res.data[0].get("parsed_content") or {}
                if syl_res and syl_res.data
                else {}
            )
            subjects = (
                parsed_content.get("subjects", [])
                if isinstance(parsed_content, dict)
                else []
            )
            subject_names = [
                s["name"].strip()
                for s in subjects
                if isinstance(s, dict) and s.get("name") and str(s["name"]).strip()
            ]

            validated_roadmap: Optional[AIMLRoadmapResponse] = None

            if not target_subject and len(subject_names) > 1:
                # Per-subject bounded fan-out so all subjects and topics are preserved
                semaphore = asyncio.Semaphore(3)

                async def _generate_for_subject(subj_name: str) -> Optional[AIMLRoadmapResponse]:
                    async with semaphore:
                        ctx = await ContextV2Assembler.assemble(
                            learner_id, scope, syllabus_id, target_subject=subj_name
                        )
                        raw = await kie_service.generate_roadmap(ctx)
                        if not raw:
                            return None
                        return AIMLRoadmapResponse(**raw)

                per_subject_results = await asyncio.gather(
                    *[_generate_for_subject(name) for name in subject_names],
                    return_exceptions=True,
                )

                merged_missions: List[RoadmapMission] = []
                merged_tracks = []
                merged_semesters = []
                merged_goals: List[str] = []
                merged_milestones: List[str] = []
                merged_career = None

                for subj_name, res in zip(subject_names, per_subject_results):
                    if isinstance(res, Exception) or res is None:
                        logger.warning(f"Subject roadmap generation failed for '{subj_name}': {res}")
                        continue
                    for m in res.missions:
                        merged_missions.append(
                            m.model_copy(update={"subject": m.subject or subj_name})
                        )
                    merged_tracks.extend(res.subject_tracks)
                    merged_semesters.extend(res.semesters)
                    for g in res.goals:
                        if g not in merged_goals:
                            merged_goals.append(g)
                    for ms in res.milestones:
                        if ms not in merged_milestones:
                            merged_milestones.append(ms)
                    if res.career and not merged_career:
                        merged_career = res.career

                if not merged_missions and not merged_tracks:
                    raise Exception("Failed to generate roadmap from KIE 2 across all subjects")

                validated_roadmap = AIMLRoadmapResponse(
                    scope=scope,
                    target_subject=None,
                    subject_tracks=merged_tracks,
                    semesters=merged_semesters,
                    career=merged_career,
                    goals=merged_goals,
                    milestones=merged_milestones,
                    missions=merged_missions,
                )
            else:
                context_v2 = await ContextV2Assembler.assemble(
                    learner_id, scope, syllabus_id, target_subject=target_subject
                )
                roadmap_data = await kie_service.generate_roadmap(context_v2)
                if not roadmap_data:
                    raise Exception("Failed to generate roadmap from KIE 2")
                validated_roadmap = AIMLRoadmapResponse(**roadmap_data)

            # Coverage validation gate & deterministic week/sequence ordering
            covered_missions = RoadmapService._ensure_topic_coverage(
                validated_roadmap.missions,
                subjects,
                target_subject=target_subject,
            )
            ordered_missions = RoadmapService._distribute_and_order_missions(
                covered_missions,
                total_weeks=16,
            )
            validated_roadmap = validated_roadmap.model_copy(update={"missions": ordered_missions})

            # 4. Inactivate previous active roadmap for this scope & subject (or master)
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

            # 7. Insert Missions with guaranteed subject tag & structured metadata
            missions_to_insert = []
            for m in validated_roadmap.missions:
                mission_type_val = m.type.value if hasattr(m.type, "value") else str(m.type)
                mission_row = {
                    "roadmap_id": new_roadmap_id,
                    "title": m.title,
                    "description": m.description,
                    "mission_type": mission_type_val,
                    "subject": m.subject or target_subject or "General",
                    "priority": m.priority,
                    "estimated_minutes": m.estimated_minutes,
                    "week": m.week,
                    "sequence": m.sequence,
                    "status": "PENDING",
                }
                if m.chapter is not None:
                    mission_row["chapter"] = m.chapter
                if m.topic is not None:
                    mission_row["topic"] = m.topic
                if m.objectives is not None:
                    mission_row["objectives"] = m.objectives
                if m.core_concepts is not None:
                    mission_row["core_concepts"] = m.core_concepts
                if m.deliverables is not None:
                    mission_row["deliverables"] = m.deliverables
                if m.mastery_criteria is not None:
                    mission_row["mastery_criteria"] = m.mastery_criteria
                missions_to_insert.append(mission_row)

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

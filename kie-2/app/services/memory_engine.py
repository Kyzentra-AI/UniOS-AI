from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.schemas.memory import (
    LearnerMemory,
    PreferenceMemory,
    ConversationMemory,
    LearningHistoryMemory,
    ProjectMemory,
    GoalMemory,
    AchievementMemory,
    FrictionMemory,
)
from app.schemas.memory_events import (
    MemoryUpdateEvent,
    MemoryUpdateResult,
    MemorySeedResult,
    MemoryEventType,
    EvidenceSource,
)
from app.schemas.intelligence import LearnerIntelligenceReport
from app.schemas.memory_context import (
    RelevantMemoryQuery,
    RelevantMemoryContext,
    RoadmapStatus,
    RoadmapRecommendedAction,
    RoadmapAdaptationContext,
)
from app.services.memory_repository import (
    BaseMemoryRepository,
    InMemoryMemoryRepository,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_clamp_score(val: Any, default: Optional[float] = None) -> Optional[float]:
    if val is None:
        return default
    try:
        f = float(val)
        return max(0.0, min(1.0, f))
    except (ValueError, TypeError):
        return default


class MemoryEngine:
    """Core AI/ML-2 Memory Intelligence Engine.
    Processes evidence-driven memory updates, context retrieval for pedagogical decisions,
    and roadmap adaptation intelligence.
    """

    def __init__(self, repository: Optional[BaseMemoryRepository] = None) -> None:
        self.repository = repository or InMemoryMemoryRepository()

    def get_or_create_memory(self, learner_id: str) -> LearnerMemory:
        """Retrieve existing memory or initialize a clean structured memory container."""
        clean_id = learner_id.strip()
        memory = self.repository.get_memory(clean_id)
        if not memory:
            memory = LearnerMemory(learner_id=clean_id)
            self.repository.save_memory(memory)
        return memory

    def get_memory(self, learner_id: str) -> Optional[LearnerMemory]:
        """Retrieve existing learner memory container without mutating the repository."""
        clean_id = learner_id.strip()
        return self.repository.get_memory(clean_id)

    def initialize_memory_from_onboarding(
        self, report: LearnerIntelligenceReport
    ) -> MemorySeedResult:
        """Bridges Sprint-2 Onboarding intelligence into the Sprint-3 LearnerMemory container.

        Maps career goals, cognitive preferences, pacing, format priorities, and baseline skills
        into structured memory idempotently without replacing existing historical evidence or events.
        """
        if not report or not getattr(report, "learner_id", None) or not str(report.learner_id).strip():
            raise ValueError("Invalid onboarding report: learner_id cannot be empty or whitespace.")

        learner_id = str(report.learner_id).strip()
        existing = self.repository.get_memory(learner_id)
        if existing is None:
            memory = LearnerMemory(learner_id=learner_id)
            is_new = True
        else:
            memory = existing
            is_new = not bool(memory.metadata.get("onboarding_seeded", False))

        seeded_facets: List[str] = []
        now = _utc_now()

        # 1. Map Career Goals
        target_role = (
            getattr(report, "target_role", None)
            or getattr(report.career_goals, "target_role", None)
            or ""
        ).strip()
        if target_role:
            memory.goals.primary_target_role = target_role
        if getattr(report.career_goals, "estimated_timeline_months", None) is not None:
            memory.goals.target_timeline_months = report.career_goals.estimated_timeline_months

        for m in getattr(report.career_goals, "key_milestones", []):
            cleaned_m = str(m).strip()
            if cleaned_m and cleaned_m not in memory.goals.milestones:
                memory.goals.milestones.append(cleaned_m)

        for hook in getattr(report.motivation, "engagement_hooks", []):
            cleaned_h = str(hook).strip()
            if cleaned_h and cleaned_h not in memory.goals.secondary_interests:
                memory.goals.secondary_interests.append(cleaned_h)

        memory.goals.last_updated = now
        seeded_facets.append("goals")

        # 2. Map Learning Preferences
        pref = memory.preferences
        if getattr(report.learning_style, "dominant_modality", None):
            pref.dominant_modality = str(report.learning_style.dominant_modality).strip().lower()
        if getattr(report.learning_style, "secondary_modality", None):
            pref.secondary_modality = str(report.learning_style.secondary_modality).strip().lower()
        if getattr(report.learning_style, "recommended_pacing", None):
            pref.pacing = str(report.learning_style.recommended_pacing).strip().lower()
        if getattr(report.learning_style, "feedback_cadence", None):
            pref.feedback_frequency = str(report.learning_style.feedback_cadence).strip()

        for fmt in getattr(report.learning_style, "content_format_priorities", []):
            cleaned_fmt = str(fmt).strip()
            if cleaned_fmt and cleaned_fmt not in pref.content_format_priorities:
                pref.content_format_priorities.append(cleaned_fmt)

        balance = (getattr(report.knowledge_analysis, "theoretical_vs_applied_balance", "") or "").lower()
        if "applied" in balance or "practical" in balance:
            pref.practical_vs_theory_ratio = 0.8
        elif "theor" in balance:
            pref.practical_vs_theory_ratio = 0.4
        elif "balance" in balance:
            pref.practical_vs_theory_ratio = 0.7

        pref.last_updated = now
        seeded_facets.append("preferences")

        # 3. Map Metadata & Baseline Skills
        stage_val = report.stage.value if hasattr(report.stage, "value") else str(report.stage)
        memory.metadata["onboarding_seeded"] = True
        memory.metadata["academic_stage"] = stage_val

        existing_skills = memory.metadata.get("baseline_skills", [])
        new_skills = [
            s for s in getattr(report.skill_analysis, "core_strengths", [])
            if s not in existing_skills
        ]
        memory.metadata["baseline_skills"] = existing_skills + new_skills

        existing_gaps = memory.metadata.get("critical_skill_gaps", [])
        new_gaps = [
            g for g in getattr(report.skill_analysis, "critical_skill_gaps", [])
            if g not in existing_gaps
        ]
        memory.metadata["critical_skill_gaps"] = existing_gaps + new_gaps

        readiness_tier_val = (
            report.readiness.readiness_tier.value
            if hasattr(report.readiness.readiness_tier, "value")
            else str(report.readiness.readiness_tier)
        )
        memory.metadata["readiness_tier"] = readiness_tier_val
        memory.metadata["overall_readiness_score"] = report.readiness.overall_readiness_score
        if report.executive_summary:
            memory.metadata["executive_summary"] = report.executive_summary
        seeded_facets.append("metadata")

        # 4. Optional Onboarding Milestone Achievement
        if readiness_tier_val == "high":
            ach_title = "Onboarding Excellence"
            if not any(a.title == ach_title for a in memory.achievements):
                memory.achievements.append(
                    AchievementMemory(
                        title=ach_title,
                        category="milestone",
                        description=(
                            f"Demonstrated high onboarding readiness "
                            f"({report.readiness.overall_readiness_score * 100:.0f}%) and strong foundational alignment."
                        ),
                        unlocked_at=now,
                    )
                )
                seeded_facets.append("achievements")

        # 5. Persist to repository
        memory.updated_at = now
        self.repository.save_memory(memory)

        # 6. Record append-only raw evidence event for auditability
        seed_event = MemoryUpdateEvent(
            learner_id=learner_id,
            event_type=MemoryEventType.GOAL_CREATED,
            evidence_source=EvidenceSource.EXPLICIT,
            confidence_score=report.readiness.overall_readiness_score,
            payload={
                "source": "onboarding_intelligence_report",
                "target_role": target_role,
                "dominant_modality": pref.dominant_modality,
                "readiness_tier": readiness_tier_val,
                "is_new_initialization": is_new,
            },
            timestamp=now,
        )
        self.repository.record_event(seed_event)

        unique_facets = list(dict.fromkeys(seeded_facets))
        status_msg = "Freshly initialized" if is_new else "Idempotently updated"
        return MemorySeedResult(
            success=True,
            learner_id=learner_id,
            seeded_facets=unique_facets,
            updated_facets=unique_facets,
            is_new_initialization=is_new,
            summary=f"{status_msg} memory container for learner '{learner_id}' from onboarding report.",
        )

    def record_event(self, event: MemoryUpdateEvent) -> MemoryUpdateResult:
        """Evidence-driven memory update pipeline.
        Distinguishes explicit user statements, observed platform interaction, and heuristic inferences.
        """
        learner_id = event.learner_id.strip()
        self.repository.record_event(event)

        memory = self.get_or_create_memory(learner_id)
        updated_facets: List[str] = []
        friction_level_updated = False
        new_mastery_level: Optional[float] = None
        summary_messages: List[str] = []

        payload = event.payload or {}
        now = event.timestamp or _utc_now()

        # 1. Lesson Completed / Skipped
        if event.event_type == MemoryEventType.LESSON_COMPLETED:
            topic = str(payload.get("topic", "General Unit")).strip()
            score_float = _safe_clamp_score(payload.get("score"))
            time_spent = payload.get("time_spent_minutes")

            # Determine mastery calculation
            mastery = score_float if score_float is not None else 0.7
            new_mastery_level = mastery

            history_entry = LearningHistoryMemory(
                topic=topic,
                lesson_id=payload.get("lesson_id"),
                status="completed",
                assessment_score=score_float,
                attempts_count=int(payload.get("attempts", 1)),
                time_spent_minutes=int(time_spent) if time_spent else None,
                mastery_level=mastery,
                timestamp=now,
            )
            memory.learning_history.append(history_entry)
            updated_facets.append("learning_history")
            summary_messages.append(f"Recorded completed lesson for topic '{topic}'.")

            # Performance correlation
            if score_float is not None:
                if score_float > 0.85:
                    # High performance resolves active friction on this topic
                    for f in memory.friction:
                        if f.topic.lower() == topic.lower() and f.unresolved:
                            f.unresolved = False
                            f.last_observed_at = now
                            friction_level_updated = True
                            updated_facets.append("friction")
                            summary_messages.append(f"Resolved prior friction on '{topic}'.")
                elif score_float < 0.5 and event.confidence_score >= 0.4:
                    # Low performance records or compounds friction
                    self._record_or_escalate_friction(
                        memory=memory,
                        topic=topic,
                        struggle_type="conceptual_gap",
                        confidence=event.confidence_score,
                        now=now,
                        details=f"Assessment score {score_float:.2f} below threshold.",
                    )
                    friction_level_updated = True
                    updated_facets.append("friction")
                    summary_messages.append(f"Recorded friction for low score ({score_float:.2f}) on '{topic}'.")

        elif event.event_type == MemoryEventType.LESSON_SKIPPED:
            topic = str(payload.get("topic", "General Unit")).strip()
            history_entry = LearningHistoryMemory(
                topic=topic,
                lesson_id=payload.get("lesson_id"),
                status="skipped",
                timestamp=now,
            )
            memory.learning_history.append(history_entry)
            updated_facets.append("learning_history")
            summary_messages.append(f"Recorded skipped lesson on '{topic}'.")

        # 2. Assessment Result
        elif event.event_type == MemoryEventType.ASSESSMENT_RESULT:
            topic = str(payload.get("topic", "Assessment")).strip()
            score_float = _safe_clamp_score(payload.get("score"), default=0.5)
            new_mastery_level = score_float

            history_entry = LearningHistoryMemory(
                topic=topic,
                lesson_id=payload.get("lesson_id"),
                status="completed" if score_float >= 0.6 else "struggled",
                assessment_score=score_float,
                mastery_level=score_float,
                timestamp=now,
            )
            memory.learning_history.append(history_entry)
            updated_facets.append("learning_history")

            if score_float > 0.85:
                # De-escalate friction
                for f in memory.friction:
                    if f.topic.lower() == topic.lower() and f.unresolved:
                        f.unresolved = False
                        f.last_observed_at = now
                        friction_level_updated = True
                        updated_facets.append("friction")
                # Award mastery achievement if score >= 0.9 and not already present
                if score_float >= 0.9:
                    ach_title = f"Topic Mastery: {topic}"
                    if not any(a.title == ach_title for a in memory.achievements):
                        memory.achievements.append(
                            AchievementMemory(
                                title=ach_title,
                                category="mastery",
                                description=f"Achieved outstanding score ({score_float * 100:.0f}%) on {topic}.",
                                unlocked_at=now,
                            )
                        )
                        updated_facets.append("achievements")
                summary_messages.append(f"Recorded assessment score {score_float:.2f} on '{topic}'.")
            elif score_float < 0.5:
                self._record_or_escalate_friction(
                    memory=memory,
                    topic=topic,
                    struggle_type="repeated_mistake" if payload.get("repeated") else "conceptual_gap",
                    confidence=event.confidence_score,
                    now=now,
                    details=payload.get("details", f"Assessment score: {score_float:.2f}"),
                )
                friction_level_updated = True
                updated_facets.append("friction")
                summary_messages.append(f"Recorded friction escalation on '{topic}' due to score {score_float:.2f}.")

        # 3. Repeated Mistake / Topic Struggled / Friction Signal
        elif event.event_type in (
            MemoryEventType.REPEATED_MISTAKE,
            MemoryEventType.TOPIC_STRUGGLED,
            MemoryEventType.FRICTION_SIGNAL,
        ):
            topic = str(payload.get("topic", "General Struggle")).strip()
            struggle_type = str(payload.get("struggle_type", "conceptual_gap"))
            self._record_or_escalate_friction(
                memory=memory,
                topic=topic,
                struggle_type=struggle_type,
                confidence=event.confidence_score,
                now=now,
                details=str(payload.get("details", "")),
            )
            friction_level_updated = True
            updated_facets.append("friction")
            summary_messages.append(f"Recorded friction signal on topic '{topic}'.")

        # 4. Topic Mastered
        elif event.event_type == MemoryEventType.TOPIC_MASTERED:
            topic = str(payload.get("topic", "General Topic")).strip()
            # De-escalate any unresolved friction
            for f in memory.friction:
                if f.topic.lower() == topic.lower():
                    f.unresolved = False
                    f.last_observed_at = now
            ach_title = f"Mastered: {topic}"
            if not any(a.title == ach_title for a in memory.achievements):
                memory.achievements.append(
                    AchievementMemory(
                        title=ach_title,
                        category="mastery",
                        description=f"Verified mastery of {topic}.",
                        unlocked_at=now,
                    )
                )
                updated_facets.append("achievements")
            updated_facets.append("friction")
            new_mastery_level = 1.0
            summary_messages.append(f"Recorded verified mastery for topic '{topic}'.")

        # 5. Project Started / Completed
        elif event.event_type in (MemoryEventType.PROJECT_STARTED, MemoryEventType.PROJECT_COMPLETED):
            title = str(payload.get("title", "Applied Project")).strip()
            status_val = "completed" if event.event_type == MemoryEventType.PROJECT_COMPLETED else "started"
            tech = payload.get("technologies_used", [])
            if isinstance(tech, str):
                tech = [t.strip() for t in tech.split(",") if t.strip()]

            existing_proj = next((p for p in memory.projects if p.title.lower() == title.lower()), None)
            if existing_proj:
                existing_proj.status = status_val
                if tech:
                    existing_proj.technologies_used = list(set(existing_proj.technologies_used + tech))
                if status_val == "completed":
                    existing_proj.completed_at = now
            else:
                new_proj = ProjectMemory(
                    title=title,
                    description=payload.get("description"),
                    technologies_used=tech,
                    status=status_val,
                    complexity=str(payload.get("complexity", "intermediate")),
                    completed_at=now if status_val == "completed" else None,
                    timestamp=now,
                )
                memory.projects.append(new_proj)
            updated_facets.append("projects")

            if status_val == "completed":
                ach_title = f"Project Builder: {title}"
                if not any(a.title == ach_title for a in memory.achievements):
                    memory.achievements.append(
                        AchievementMemory(
                            title=ach_title,
                            category="project",
                            description=f"Completed project '{title}'.",
                            unlocked_at=now,
                        )
                    )
                    updated_facets.append("achievements")
            summary_messages.append(f"Project '{title}' updated with status '{status_val}'.")

        # 6. Goal Created / Updated
        elif event.event_type in (MemoryEventType.GOAL_CREATED, MemoryEventType.GOAL_UPDATED):
            new_role = payload.get("primary_target_role") or payload.get("target_role")
            if new_role and str(new_role).strip():
                old_role = memory.goals.primary_target_role
                cleaned_role = str(new_role).strip()
                if old_role != cleaned_role:
                    memory.goals.goal_change_history.append({
                        "previous_role": old_role,
                        "new_role": cleaned_role,
                        "timestamp": now.isoformat(),
                        "reason": payload.get("reason", "Learner goal update"),
                    })
                    memory.goals.primary_target_role = cleaned_role

            if "milestones" in payload and isinstance(payload["milestones"], list):
                memory.goals.milestones = [str(m).strip() for m in payload["milestones"] if str(m).strip()]
            if "completed_milestones" in payload and isinstance(payload["completed_milestones"], list):
                memory.goals.completed_milestones = [
                    str(m).strip() for m in payload["completed_milestones"] if str(m).strip()
                ]
            if "target_timeline_months" in payload:
                try:
                    memory.goals.target_timeline_months = max(1, int(payload["target_timeline_months"]))
                except (ValueError, TypeError):
                    pass
            memory.goals.last_updated = now
            updated_facets.append("goals")
            summary_messages.append(f"Updated learner career goals (Target: '{memory.goals.primary_target_role}').")

        # 7. Achievement Earned
        elif event.event_type == MemoryEventType.ACHIEVEMENT_EARNED:
            title = str(payload.get("title", "Achievement Unlocked")).strip()
            desc = str(payload.get("description", "Recognized accomplishment.")).strip()
            category = str(payload.get("category", "milestone")).strip()
            if not any(a.title.lower() == title.lower() for a in memory.achievements):
                memory.achievements.append(
                    AchievementMemory(
                        title=title,
                        category=category,
                        description=desc,
                        unlocked_at=now,
                    )
                )
                updated_facets.append("achievements")
                summary_messages.append(f"Recorded achievement '{title}'.")

        # 8. Preference Observed
        elif event.event_type == MemoryEventType.PREFERENCE_OBSERVED:
            # Explicit evidence overrides directly; inferred signals apply when confidence >= 0.5
            if event.evidence_source == EvidenceSource.EXPLICIT or event.confidence_score >= 0.5:
                modality = payload.get("dominant_modality") or payload.get("modality")
                if modality:
                    memory.preferences.dominant_modality = str(modality).strip().lower()
                pacing = payload.get("pacing")
                if pacing:
                    memory.preferences.pacing = str(pacing).strip().lower()
                ratio = payload.get("practical_vs_theory_ratio")
                if ratio is not None:
                    try:
                        memory.preferences.practical_vs_theory_ratio = max(0.0, min(1.0, float(ratio)))
                    except (ValueError, TypeError):
                        pass
                memory.preferences.last_updated = now
                updated_facets.append("preferences")
                summary_messages.append("Updated cognitive and learning style preferences.")

        # 9. Conversation Signal
        elif event.event_type == MemoryEventType.CONVERSATION_SIGNAL:
            conv = ConversationMemory(
                topic=payload.get("topic"),
                question_summary=payload.get("question_summary"),
                confusion_points=payload.get("confusion_points", []),
                expressed_sentiment=payload.get("expressed_sentiment", "neutral"),
                timestamp=now,
            )
            memory.conversations.append(conv)
            updated_facets.append("conversations")
            # If learner explicitly expressed frustration or confusion on a topic, register friction indicator
            if conv.expressed_sentiment in ("frustrated", "confused") and conv.topic:
                self._record_or_escalate_friction(
                    memory=memory,
                    topic=conv.topic,
                    struggle_type="cognitive_overload" if conv.expressed_sentiment == "frustrated" else "conceptual_gap",
                    confidence=event.confidence_score * 0.7,
                    now=now,
                    details=f"Expressed {conv.expressed_sentiment} sentiment in conversation.",
                )
                friction_level_updated = True
                updated_facets.append("friction")
            summary_messages.append("Logged conversational signal.")

        memory.updated_at = now
        self.repository.save_memory(memory)

        return MemoryUpdateResult(
            success=True,
            event_id=event.event_id,
            learner_id=learner_id,
            event_type=event.event_type,
            updated_facets=list(set(updated_facets)),
            summary=" ".join(summary_messages) or "Processed learning event.",
            friction_level_updated=friction_level_updated,
            new_mastery_level=new_mastery_level,
        )

    def _record_or_escalate_friction(
        self,
        memory: LearnerMemory,
        topic: str,
        struggle_type: str,
        confidence: float,
        now: datetime,
        details: str = "",
    ) -> None:
        """Internal helper to create or compound friction evidence without lossy overwrite."""
        clean_topic = topic.strip()
        existing = next(
            (f for f in memory.friction if f.topic.lower() == clean_topic.lower() and f.unresolved),
            None,
        )
        if existing:
            existing.mistake_count += 1
            existing.last_observed_at = now
            if existing.mistake_count >= 3:
                existing.severity = "high"
                existing.recommended_intervention = "Immediate foundational remediation with visual worked examples."
            elif existing.mistake_count == 2:
                existing.severity = "moderate"
                existing.recommended_intervention = "Step-by-step reinforcement before moving forward."
        else:
            initial_severity = "moderate" if confidence >= 0.8 else "low"
            new_friction = FrictionMemory(
                topic=clean_topic,
                struggle_type=struggle_type,
                severity=initial_severity,
                mistake_count=1,
                unresolved=True,
                recommended_intervention="Provide foundational scaffolding and targeted practice.",
                first_observed_at=now,
                last_observed_at=now,
            )
            memory.friction.append(new_friction)

    def retrieve_relevant_context(self, query: RelevantMemoryQuery) -> RelevantMemoryContext:
        """Retrieves scoped, relevant memory intelligence for a pedagogical decision.
        Filters by topic, career goal, and active friction without dumping entire raw history.
        """
        learner_id = query.learner_id.strip()
        memory = self.repository.get_memory(learner_id)

        if not memory:
            # Baseline memory context for brand-new or unknown learners
            return RelevantMemoryContext(
                learner_id=learner_id,
                topic=query.topic,
                relevant_preferences=PreferenceMemory(),
                relevant_friction=[],
                relevant_history=[],
                relevant_projects=[],
                active_goal=GoalMemory(primary_target_role=query.target_role or "Software Engineer"),
                recent_achievements=[],
                recent_conversations=[],
                detected_strengths=[],
                detected_weaknesses=[],
                recommended_pedagogical_mode="visual",
                rationale="No previous memory recorded for learner. Baseline pedagogical defaults applied.",
            )

        query_topic = (query.topic or "").lower().strip()

        # 1. Filter relevant friction
        relevant_friction = [
            f for f in memory.friction
            if f.unresolved and (not query_topic or query_topic in f.topic.lower() or f.topic.lower() in query_topic)
        ]
        # If no direct match, include high-severity unresolved friction
        if not relevant_friction:
            relevant_friction = [f for f in memory.friction if f.unresolved and f.severity == "high"][:query.max_history_items]

        # 2. Filter relevant history
        if query_topic:
            relevant_history = [
                h for h in memory.learning_history
                if query_topic in h.topic.lower() or h.topic.lower() in query_topic
            ]
        else:
            relevant_history = []
        # Append recent history if relevant list is small
        if len(relevant_history) < query.max_history_items:
            recent_remaining = [
                h for h in reversed(memory.learning_history)
                if h not in relevant_history
            ][: query.max_history_items - len(relevant_history)]
            relevant_history.extend(recent_remaining)

        # 3. Filter relevant projects
        relevant_projects = [
            p for p in memory.projects
            if (query_topic and any(query_topic in t.lower() for t in p.technologies_used))
            or p.status == "completed"
        ][:3]

        # 4. Synthesize strengths and weaknesses
        detected_strengths: List[str] = []
        for h in memory.learning_history:
            if h.mastery_level > 0.85 and h.topic not in detected_strengths:
                detected_strengths.append(h.topic)
        for a in memory.achievements:
            if a.category == "mastery" and a.title.replace("Topic Mastery: ", "").replace("Mastered: ", "") not in detected_strengths:
                detected_strengths.append(a.title)

        detected_weaknesses: List[str] = [
            f.topic for f in memory.friction if f.unresolved and f.topic not in detected_strengths
        ]

        # 5. Determine recommended pedagogical mode and rationale
        if any(f.severity == "high" for f in relevant_friction):
            rec_mode = "visual"
            rationale = (
                f"High-severity friction detected on topic(s) "
                f"{[f.topic for f in relevant_friction if f.severity == 'high']}. "
                f"Recommend foundational remediation with visual breakdown and worked examples."
            )
        elif memory.preferences.dominant_modality in ("interactive", "hands-on"):
            rec_mode = "interactive"
            rationale = f"Learner shows sustained preference for hands-on, practical execution."
        else:
            rec_mode = memory.preferences.dominant_modality or "visual"
            rationale = f"Standard progression calibrated to learner's {rec_mode} modality."

        return RelevantMemoryContext(
            learner_id=learner_id,
            topic=query.topic,
            relevant_preferences=memory.preferences,
            relevant_friction=relevant_friction,
            relevant_history=relevant_history[:query.max_history_items],
            relevant_projects=relevant_projects,
            active_goal=memory.goals,
            recent_achievements=memory.achievements[-3:],
            recent_conversations=memory.conversations[-3:],
            detected_strengths=detected_strengths[:5],
            detected_weaknesses=detected_weaknesses[:5],
            recommended_pedagogical_mode=rec_mode,
            rationale=rationale,
        )

    def generate_roadmap_context(
        self, learner_id: str, current_topic: Optional[str] = None
    ) -> RoadmapAdaptationContext:
        """Intelligence contract for AI/ML-1 orchestration to adapt curriculum roadmaps."""
        memory = self.repository.get_memory(learner_id.strip())

        if not memory:
            return RoadmapAdaptationContext(
                learner_id=learner_id,
                status=RoadmapStatus.ON_TRACK,
                recommended_action=RoadmapRecommendedAction.PROCEED_NEXT_TOPIC,
                remediation_topics=[],
                mastered_topics=[],
                next_recommended_skills=["Programming Foundations", "Data Structures"],
                rationale="Initial roadmap setup. No friction or history observed yet.",
            )

        unresolved_friction = [f for f in memory.friction if f.unresolved]
        high_severity_friction = [f for f in unresolved_friction if f.severity == "high"]

        mastered = [
            h.topic for h in memory.learning_history if h.mastery_level > 0.85
        ]

        # Case 1: High friction or multiple unresolved topics -> Needs Remediation
        if high_severity_friction or len(unresolved_friction) >= 2:
            remediation_topics = list({f.topic for f in unresolved_friction})
            return RoadmapAdaptationContext(
                learner_id=learner_id,
                status=RoadmapStatus.NEEDS_REMEDIATION,
                recommended_action=RoadmapRecommendedAction.INSERT_REMEDIATION,
                remediation_topics=remediation_topics,
                mastered_topics=mastered,
                next_recommended_skills=[f"Remediation: {t}" for t in remediation_topics[:2]],
                rationale=(
                    f"Learner has {len(unresolved_friction)} active struggle points. "
                    f"Roadmap must insert targeted scaffolding for: {remediation_topics} before proceeding."
                ),
            )

        # Case 2: Goal shifted recently
        if memory.goals.goal_change_history:
            recent_change = memory.goals.goal_change_history[-1]
            return RoadmapAdaptationContext(
                learner_id=learner_id,
                status=RoadmapStatus.GOAL_SHIFTED,
                recommended_action=RoadmapRecommendedAction.ADJUST_MILESTONES,
                remediation_topics=[],
                mastered_topics=mastered,
                next_recommended_skills=[
                    f"{memory.goals.primary_target_role} Core Competencies",
                    "Advanced System Architecture",
                ],
                rationale=(
                    f"Target career role changed from '{recent_change.get('previous_role')}' "
                    f"to '{recent_change.get('new_role')}'. Roadmap milestones require re-alignment."
                ),
            )

        # Case 3: Ready for Advancement (high mastery, zero active friction)
        if len(mastered) >= 3 and not unresolved_friction:
            return RoadmapAdaptationContext(
                learner_id=learner_id,
                status=RoadmapStatus.READY_FOR_ADVANCEMENT,
                recommended_action=RoadmapRecommendedAction.ACCELERATE,
                remediation_topics=[],
                mastered_topics=mastered,
                next_recommended_skills=["Advanced Projects", "System Integration"],
                rationale="Demonstrated strong topic mastery across multiple units with zero friction.",
            )

        # Case 4: Default On-Track
        return RoadmapAdaptationContext(
            learner_id=learner_id,
            status=RoadmapStatus.ON_TRACK,
            recommended_action=RoadmapRecommendedAction.PROCEED_NEXT_TOPIC,
            remediation_topics=[],
            mastered_topics=mastered,
            next_recommended_skills=["Next Curriculum Unit", "Applied Challenge"],
            rationale="Learner is progressing smoothly along planned curriculum milestones.",
        )


_default_memory_repository = InMemoryMemoryRepository()
_default_memory_engine = MemoryEngine(repository=_default_memory_repository)


def get_memory_repository() -> BaseMemoryRepository:
    """Provides the active memory repository instance."""
    return _default_memory_repository


def get_memory_engine(repository: Optional[BaseMemoryRepository] = None) -> MemoryEngine:
    """Provides the active MemoryEngine instance."""
    if repository:
        return MemoryEngine(repository=repository)
    return _default_memory_engine


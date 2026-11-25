import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.schemas.context_v2 import AnalyzeContextRequest
from app.data.canonical_curricula import get_canonical_curriculum
from app.schemas.roadmap import (
    AIMLRoadmapResponse,
    MissionType,
    RoadmapCareer,
    RoadmapMission,
    RoadmapSemester,
    RoadmapSubject,
    SubjectTrack,
)
from app.services.llm_provider import extract_json_payload, get_llm_provider
from app.services.domain_classifier import classify_domain, DomainArchetype

logger = logging.getLogger(__name__)


class RoadmapService:
    """
    KIE Roadmap Generation Engine (Endpoint 4: POST /api/v1/kie/roadmap/generate).
    Supports Dual-Mode Roadmap Generation:
      - Mode 1: Targeted Single-Subject Track (when target_subject is specified)
      - Mode 2: Multi-Subject Master Holistic Curriculum (when target_subject is None / "ALL")
    Strictly adheres to AIMLRoadmapResponse schema required by Backend.
    """

    def generate(self, request: AnalyzeContextRequest) -> AIMLRoadmapResponse:
        raw_scope = (request.scope or "ACADEMIC").upper()
        if raw_scope not in {"ACADEMIC", "CAREER", "BOTH"}:
            raw_scope = "ACADEMIC"

        target_subject = (request.target_subject or "").strip() or None
        if target_subject and target_subject.upper() in {"ALL", "NONE", "NULL"}:
            target_subject = None

        # 1. Attempt LLM generation if live provider is enabled
        if settings.LLM_PROVIDER.lower() != "mock":
            try:
                llm_response = (
                    self._generate_single_subject_llm(request, raw_scope, target_subject)
                    if target_subject
                    else self._generate_multi_subject_llm(request, raw_scope)
                )
                if llm_response and len(llm_response.missions) >= 3:
                    logger.info(
                        f"[RoadmapService] LLM generated roadmap with {len(llm_response.missions)} missions "
                        f"(target_subject={target_subject}, scope={raw_scope})"
                    )
                    return llm_response
            except Exception as e:
                logger.warning(f"[RoadmapService] LLM roadmap generation failed ({e}), using deterministic generator.")

        # 2. Deterministic rule-based roadmap generator (100% reliable fallback)
        return (
            self._generate_single_subject_deterministic(request, raw_scope, target_subject)
            if target_subject
            else self._generate_multi_subject_deterministic(request, raw_scope)
        )

    # -------------------------------------------------------------------------
    # Mode 1: Targeted Single-Subject Track
    # -------------------------------------------------------------------------
    def _generate_single_subject_llm(
        self, request: AnalyzeContextRequest, scope: str, target_subject: str
    ) -> Optional[AIMLRoadmapResponse]:
        provider = get_llm_provider()
        learner = request.learner or {}
        education = request.education or {}
        syllabus = request.syllabus or {}

        # Extract matching subject topics from syllabus
        subject_topics: List[str] = []
        for s in syllabus.get("subjects", []):
            if isinstance(s, dict) and s.get("name", "").strip().lower() == target_subject.lower():
                subject_topics = [str(t) for t in s.get("topics", [])]
                break

        system_instruction = (
            "You are the senior UniOS Curriculum Synthesis Engine. "
            f"Generate a deep, comprehensive, multi-week learning roadmap strictly for SUBJECT: '{target_subject}'.\n\n"
            "CONTENT MAXIMIZATION GUIDELINES:\n"
            f"- Structure 6 to 10 progressive missions across 3 to 4 weeks dedicated entirely to '{target_subject}'.\n"
            f"- Every single mission MUST have 'subject': '{target_subject}'.\n"
            "- For EVERY mission, the 'description' MUST be comprehensive and structured into 4 distinct sections:\n"
            "  🎯 Objectives: <Clear learning goals and competencies>\n"
            "  📚 Core Concepts: <Key theoretical foundations, invariants, and algorithms to master>\n"
            "  💻 Deliverables: <Concrete implementation, project code, or benchmark analysis required>\n"
            "  ✅ Mastery Criteria: <Specific evaluation metrics to verify topic proficiency>\n"
            "DO NOT write brief 1-sentence descriptions. Maximize depth and actionable guidance.\n"
            "Output strictly valid JSON matching this schema:\n"
            "{\n"
            f'  "scope": "{scope}",\n'
            f'  "target_subject": "{target_subject}",\n'
            '  "goals": ["<Goal 1>", "<Goal 2>"],\n'
            '  "milestones": ["<Week 1 Milestone>", "<Week 2 Milestone>", "<Week 3 Milestone>"],\n'
            '  "missions": [\n'
            "    {\n"
            '      "title": "<Mission Title>",\n'
            '      "type": "LEARNING" | "PRACTICAL" | "REVISION" | "ASSIGNMENT" | "ARTIFACT" | "CAREER",\n'
            '      "description": "🎯 Objectives: ...\\n📚 Core Concepts: ...\\n💻 Deliverables: ...\\n✅ Mastery Criteria: ...",\n'
            '      "priority": "HIGH" | "MEDIUM" | "LOW",\n'
            '      "estimated_minutes": 90,\n'
            f'      "subject": "{target_subject}",\n'
            '      "week": 1,\n'
            '      "sequence": 1\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        user_prompt = f"""TARGET SUBJECT: {target_subject}
SYLLABUS TOPICS: {json.dumps(subject_topics) if subject_topics else 'Standard curriculum for ' + target_subject}
LEARNER GOAL: {learner.get('primary_goal', 'Technical Mastery')}
EXPERIENCE: {learner.get('experience_level', 'Intermediate')}
DEGREE PROGRAM: {education.get('degree_program', 'Computer Science')}
Generate 6 to 10 progressive missions across 3 to 4 weeks (theory -> practical coding -> assignment -> capstone artifact).
Every single mission MUST have subject: "{target_subject}".
"""
        raw = provider._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2800,
            temperature=0.2,
        )
        return self._sanitize_and_parse_response(
            raw, scope, target_subject=target_subject, expected_topics=subject_topics
        )

    def _generate_single_subject_deterministic(
        self, request: AnalyzeContextRequest, scope: str, target_subject: str
    ) -> AIMLRoadmapResponse:
        syllabus = request.syllabus or {}
        learner = request.learner or {}
        education = request.education or {}
        primary_goal = learner.get("primary_goal") or f"Mastery in {target_subject}"
        degree = education.get("degree_program")
        total_weeks = self._calculate_total_weeks(request)

        # Check for Canonical Curriculum
        canonical = get_canonical_curriculum(target_subject)
        missions: List[RoadmapMission] = []
        seq = 1

        if canonical:
            chapters = canonical["chapters"]
            total_items = sum(len(ch.get("topics", [])) or 1 for ch in chapters)
            items_per_week = max(1, total_items // total_weeks)

            ch_item_count = 0
            for c_idx, ch in enumerate(chapters):
                ch_title = ch["title"]
                ch_topics = [t["title"] for t in ch.get("topics", [])]
                if not ch_topics:
                    ch_topics = [ch_title]

                for t_idx, t_name in enumerate(ch_topics):
                    ch_item_count += 1
                    curr_week = min(total_weeks, (ch_item_count // max(1, items_per_week)) + 1)
                    m = self._build_mission(
                        title=f"{ch_title}: {t_name}",
                        m_type=MissionType.LEARNING,
                        subject=target_subject,
                        topic=t_name,
                        week=curr_week,
                        sequence=seq,
                        priority="HIGH" if t_idx == 0 else "MEDIUM",
                        estimated_minutes=90,
                        degree_program=degree,
                        chapter=ch_title,
                    )
                    missions.append(m)
                    seq += 1

                # Attach consolidation practice milestone for each chapter
                curr_week = min(total_weeks, (ch_item_count // max(1, items_per_week)) + 1)
                p_mission = self._build_mission(
                    title=f"Applied Practice & Lab: {ch_title}",
                    m_type=MissionType.PRACTICAL,
                    subject=target_subject,
                    topic=ch_topics[0],
                    week=curr_week,
                    sequence=seq,
                    priority="HIGH",
                    estimated_minutes=90,
                    degree_program=degree,
                    chapter=ch_title,
                )
                missions.append(p_mission)
                seq += 1

                # Attach milestone assignment at midpoint and end
                if c_idx in (len(chapters) // 2, len(chapters) - 1):
                    a_mission = self._build_mission(
                        title=f"Milestone Assignment: {ch_title}",
                        m_type=MissionType.ASSIGNMENT,
                        subject=target_subject,
                        topic=ch_topics[0],
                        week=curr_week,
                        sequence=seq,
                        priority="HIGH",
                        estimated_minutes=120,
                        degree_program=degree,
                        chapter=ch_title,
                    )
                    missions.append(a_mission)
                    seq += 1

            topics = [c["title"] for c in canonical["chapters"]]
            subject_tracks = [
                SubjectTrack(
                    subject_name=target_subject,
                    mission_count=len(missions),
                    estimated_total_minutes=sum(m.estimated_minutes for m in missions),
                    core_topics=topics,
                    chapters=canonical["chapters"],
                )
            ]
            semesters = [
                RoadmapSemester(
                    name="Dedicated Subject Track",
                    subjects=[RoadmapSubject(name=target_subject, topics=topics, chapters=canonical["chapters"])],
                )
            ] if scope in {"ACADEMIC", "BOTH"} else []

            career = None
            if scope in {"CAREER", "BOTH"}:
                c_mission = self._build_mission(
                    title=f"Technical Interview Review & Portfolio Capstone: {target_subject}",
                    m_type=MissionType.CAREER,
                    subject=target_subject,
                    topic=f"{target_subject} Portfolio",
                    week=total_weeks,
                    sequence=seq,
                    priority="HIGH",
                    estimated_minutes=90,
                    degree_program=degree,
                    chapter="Capstone & Career Readiness",
                )
                missions.append(c_mission)
                seq += 1
                career = RoadmapCareer(
                    goals=[
                        f"Achieve production-grade mastery in {target_subject}",
                        f"Ship {target_subject} Capstone Portfolio Artifact",
                    ]
                )

            goals = [
                f"Achieve topic mastery across all {len(canonical['chapters'])} canonical chapters of {target_subject}",
                f"Construct and validate an end-to-end portfolio capstone for {target_subject}",
            ]
            milestones = [
                f"Chapter {c['chapter_number']}: {c['title']}" for c in canonical["chapters"][:min(4, len(canonical["chapters"]))]
            ]
            if scope in {"CAREER", "BOTH"}:
                milestones.append(f"{target_subject} Technical Articulation & Career Readiness")

            return AIMLRoadmapResponse(
                scope=scope,
                target_subject=target_subject,
                subject_tracks=subject_tracks,
                semesters=semesters,
                career=career,
                goals=goals,
                milestones=milestones,
                missions=missions,
            )

        # Non-canonical single subject: Extract ALL topics from syllabus without truncation
        topics: List[str] = []
        for s in syllabus.get("subjects", []):
            if isinstance(s, dict) and s.get("name", "").strip().lower() == target_subject.lower():
                topics = [str(t) for t in s.get("topics", [])]
                break
        if not topics:
            topics = [
                f"{target_subject} Foundations & Core Principles",
                f"{target_subject} Structural Frameworks & Methods",
                f"{target_subject} Applied Problem Solving & Optimization",
                f"{target_subject} Advanced Topics & Capstone Integration",
            ]

        # Coverage Guarantee: Map every extracted topic to a LEARNING mission
        topic_count = len(topics)
        missions_per_week = max(1, (topic_count + (topic_count // 2)) // total_weeks)

        running_item = 0
        learning_streak = 0
        for t_idx, topic in enumerate(topics):
            running_item += 1
            curr_week = min(total_weeks, (running_item // max(1, missions_per_week)) + 1)
            
            # 1. LEARNING mission for every topic
            l_mission = self._build_mission(
                title=f"Learn: {topic}",
                m_type=MissionType.LEARNING,
                subject=target_subject,
                topic=topic,
                week=curr_week,
                sequence=seq,
                priority="HIGH" if t_idx < 3 else "MEDIUM",
                estimated_minutes=90,
                degree_program=degree,
            )
            missions.append(l_mission)
            seq += 1
            learning_streak += 1

            # 2. Activity-Type Rules: Attach PRACTICE/ASSIGNMENT milestone after every 2-3 learning missions
            if learning_streak >= 3 or t_idx == topic_count - 1:
                running_item += 1
                curr_week = min(total_weeks, (running_item // max(1, missions_per_week)) + 1)
                m_type = MissionType.ASSIGNMENT if (t_idx == topic_count - 1) else MissionType.PRACTICAL
                title_prefix = "Milestone Assignment" if m_type == MissionType.ASSIGNMENT else "Applied Practice"
                p_mission = self._build_mission(
                    title=f"{title_prefix}: Applied Review of {topic}",
                    m_type=m_type,
                    subject=target_subject,
                    topic=topic,
                    week=curr_week,
                    sequence=seq,
                    priority="HIGH",
                    estimated_minutes=90,
                    degree_program=degree,
                )
                missions.append(p_mission)
                seq += 1
                learning_streak = 0

        # Optional career mission
        career = None
        if scope in {"CAREER", "BOTH"}:
            c_mission = self._build_mission(
                title=f"Career Portfolio & Capstone Articulation: {target_subject}",
                m_type=MissionType.CAREER,
                subject=target_subject,
                topic=f"{target_subject} Capstone",
                week=total_weeks,
                sequence=seq,
                priority="HIGH",
                estimated_minutes=90,
                degree_program=degree,
            )
            missions.append(c_mission)
            seq += 1
            career = RoadmapCareer(
                goals=[
                    f"Achieve specialized proficiency in {target_subject}",
                    f"Ship {target_subject} Capstone Project Artifact",
                ]
            )

        subject_tracks = [
            SubjectTrack(
                subject_name=target_subject,
                mission_count=len(missions),
                estimated_total_minutes=sum(m.estimated_minutes for m in missions),
                core_topics=topics,
            )
        ]

        semesters = [
            RoadmapSemester(
                name="Dedicated Subject Track",
                subjects=[RoadmapSubject(name=target_subject, topics=topics)],
            )
        ] if scope in {"ACADEMIC", "BOTH"} else []

        goals = [
            f"Master all {len(topics)} topics of {target_subject} syllabus",
            f"Build and validate applied portfolio project for {target_subject}",
        ]
        milestones = [
            f"Week 1-{total_weeks // 4}: Foundational Concepts in {target_subject}",
            f"Week {(total_weeks // 4) + 1}-{total_weeks // 2}: Applied Frameworks & Numerical/Practice Work",
            f"Week {(total_weeks // 2) + 1}-{(3 * total_weeks) // 4}: Advanced Methods & Case Studies",
            f"Week {((3 * total_weeks) // 4) + 1}-{total_weeks}: Comprehensive Capstone & Benchmark Mastery",
        ]

        return AIMLRoadmapResponse(
            scope=scope,
            target_subject=target_subject,
            subject_tracks=subject_tracks,
            semesters=semesters,
            career=career,
            goals=goals,
            milestones=milestones,
            missions=missions,
        )


    # -------------------------------------------------------------------------
    # Mode 2: Multi-Subject Master Holistic Curriculum
    # -------------------------------------------------------------------------
    def _generate_multi_subject_llm(
        self, request: AnalyzeContextRequest, scope: str
    ) -> Optional[AIMLRoadmapResponse]:
        provider = get_llm_provider()
        learner = request.learner or {}
        education = request.education or {}
        syllabus = request.syllabus or {}

        parsed_subjects = self._parse_subjects(syllabus, request.selected_subjects)

        system_instruction = (
            "You are the senior UniOS Curriculum & Roadmap Synthesis Engine. "
            "Generate an extensive, rigorous, and highly structured learning roadmap with sequential missions based on ContextV2.\n\n"
            "CONTENT MAXIMIZATION & MULTI-SUBJECT FULL SYLLABUS GUIDELINES:\n"
            "- FULL SYLLABUS COVERAGE REQUIREMENT: Every single subject listed in the syllabus MUST have comprehensive coverage across its units/modules.\n"
            "- For EVERY subject in the syllabus, generate at least 3 to 5 progressive, dedicated missions covering: Foundations & Invariants, Core Mechanics/Architecture, Advanced Optimization/Problem-Solving, and Practical/Benchmark Integration.\n"
            "- NEVER omit or leave any subject with only 1 mission. Every enrolled subject must have substantial multi-week coverage.\n"
            "- Every mission MUST explicitly designate its exact 'subject' name matching the syllabus subject name.\n"
            "- Provide rich, detailed, granular topics for each subject (5-8 topics per subject).\n"
            "- Provide multiple structured goals and clear week-by-week milestones.\n"
            "- Interleave missions across subjects evenly across weeks (Weeks 1 to 6-8) to provide a balanced, manageable study schedule.\n"
            "- Total missions must scale with the number of subjects (typically 3 to 4 missions per subject; for 6-8 subjects, generate 20 to 32 total missions).\n"
            "- For EVERY mission, the 'description' MUST be comprehensive and structured into 4 distinct sections:\n"
            "  🎯 Objectives: <Clear learning goals and competencies>\n"
            "  📚 Core Concepts: <Key theoretical foundations, invariants, and algorithms to master>\n"
            "  💻 Deliverables: <Concrete implementation, project code, or benchmark analysis required>\n"
            "  ✅ Mastery Criteria: <Specific evaluation metrics to verify topic proficiency>\n"
            "DO NOT write brief 1-sentence descriptions. Maximize depth and actionable guidance.\n"
            "Output strictly valid JSON matching this schema:\n"
            "{\n"
            f'  "scope": "{scope}",\n'
            '  "semesters": [\n'
            "    {\n"
            '      "name": "Semester 1",\n'
            '      "subjects": [\n'
            '        {"name": "<Subject Name>", "topics": ["<Topic 1>", "<Topic 2>", "<Topic 3>", "<Topic 4>", "<Topic 5>"]}\n'
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "career": {"goals": ["<Career Goal 1>", "<Career Goal 2>", "<Career Goal 3>"]},\n'
            '  "goals": ["<Goal 1>", "<Goal 2>", "<Goal 3>"],\n'
            '  "milestones": ["<Milestone 1>", "<Milestone 2>", "<Milestone 3>", "<Milestone 4>"],\n'
            '  "missions": [\n'
            "    {\n"
            '      "title": "<Mission Title>",\n'
            '      "type": "LEARNING" | "PRACTICAL" | "REVISION" | "ASSIGNMENT" | "ARTIFACT" | "CAREER",\n'
            '      "description": "🎯 Objectives: ...\\n📚 Core Concepts: ...\\n💻 Deliverables: ...\\n✅ Mastery Criteria: ...",\n'
            '      "priority": "HIGH" | "MEDIUM" | "LOW",\n'
            '      "estimated_minutes": 90,\n'
            '      "subject": "<Exact Subject Name>",\n'
            '      "week": 1,\n'
            '      "sequence": 1\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        subject_summary = [{"name": s.name, "topics": s.topics[:6]} for s in parsed_subjects]
        user_prompt = f"""CONTEXT V2:
Scope: {scope}
Learner Goal: {learner.get('primary_goal', 'Software Engineer')}
Skills: {learner.get('skills', [])}
Target Skills: {learner.get('target_skills', [])}
Academic: {education.get('degree_program', 'Computer Science')} ({education.get('academic_status', 'BACHELOR')})
Syllabus Subjects: {json.dumps(subject_summary)}
Generate an interleaved multi-subject schedule ensuring balanced study load across all subjects.
"""
        raw = provider._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=3500,
            temperature=0.25,
        )
        return self._sanitize_and_parse_response(
            raw, scope, target_subject=None, parsed_subjects=parsed_subjects
        )

    def _generate_multi_subject_deterministic(
        self, request: AnalyzeContextRequest, scope: str
    ) -> AIMLRoadmapResponse:
        learner = request.learner or {}
        education = request.education or {}
        syllabus = request.syllabus or {}

        primary_goal = learner.get("primary_goal") or "Master Academic Competencies"
        degree = education.get("degree_program") or "Undergraduate Degree"
        total_weeks = self._calculate_total_weeks(request)

        parsed_subjects = self._parse_subjects(syllabus, request.selected_subjects)

        # Semesters
        semesters: List[RoadmapSemester] = []
        if scope in {"ACADEMIC", "BOTH"}:
            semesters.append(RoadmapSemester(name="Current Term", subjects=parsed_subjects))

        # Career
        career = None
        if scope in {"CAREER", "BOTH"}:
            career = RoadmapCareer(goals=[primary_goal, "Production Architecture & Portfolio Capstone"])

        goals = [
            f"Achieve topic mastery across all {len(parsed_subjects)} core syllabus subjects",
            f"Complete full semester curriculum across {total_weeks} weeks",
        ]
        milestones = [
            f"Week 1-{total_weeks // 4}: Foundational Principles & Core Concepts across all subjects",
            f"Week {(total_weeks // 4) + 1}-{total_weeks // 2}: Applied Workflows, Practice Problems & Intermediate Methods",
            f"Week {(total_weeks // 2) + 1}-{(3 * total_weeks) // 4}: Advanced Systems, Case Studies & Multi-Subject Synthesis",
            f"Week {((3 * total_weeks) // 4) + 1}-{total_weeks}: Comprehensive Capstone Review, Benchmark Evaluation & Final Preparation",
        ]

        missions: List[RoadmapMission] = []
        global_seq = 1

        # Comprehensive coverage: Collect ALL topics per subject
        # Build queue of (subject, topic, topic_idx, total_topics_for_subj)
        subject_queues: Dict[str, List[str]] = {}
        for subj in parsed_subjects:
            subj_topics = list(subj.topics)
            if not subj_topics:
                subj_topics = [
                    f"{subj.name} Foundational Principles",
                    f"{subj.name} Core Methodologies",
                    f"{subj.name} Applied Analysis",
                    f"{subj.name} Advanced Synthesis",
                ]
            subject_queues[subj.name] = subj_topics

        # Calculate max topics across subjects to interleave round-robin across semester weeks
        max_topics = max(len(t_list) for t_list in subject_queues.values()) if subject_queues else 1
        
        # Track learning streak per subject to attach PRACTICE/ASSIGNMENT milestones
        subject_learning_streaks: Dict[str, int] = {s.name: 0 for s in parsed_subjects}

        for topic_round in range(max_topics):
            # Calculate pacing: distribute rounds smoothly across available weeks
            week_num = min(total_weeks, int((topic_round / max_topics) * (total_weeks - 1)) + 1)

            for subj in parsed_subjects:
                t_list = subject_queues.get(subj.name, [])
                if topic_round < len(t_list):
                    topic = t_list[topic_round]
                    
                    # 1. LEARNING mission for the topic (Coverage Guarantee)
                    l_mission = self._build_mission(
                        title=f"{subj.name}: {topic}",
                        m_type=MissionType.LEARNING,
                        subject=subj.name,
                        topic=topic,
                        week=week_num,
                        sequence=global_seq,
                        priority="HIGH" if topic_round == 0 else "MEDIUM",
                        estimated_minutes=90,
                        degree_program=degree,
                    )
                    missions.append(l_mission)
                    global_seq += 1
                    subject_learning_streaks[subj.name] += 1

                    # 2. Activity-Type Rules: Attach PRACTICE or ASSIGNMENT milestone after every 2-3 learning missions
                    if subject_learning_streaks[subj.name] >= 3:
                        p_mission = self._build_mission(
                            title=f"{subj.name} Applied Review: {topic}",
                            m_type=MissionType.PRACTICAL,
                            subject=subj.name,
                            topic=topic,
                            week=week_num,
                            sequence=global_seq,
                            priority="HIGH",
                            estimated_minutes=90,
                            degree_program=degree,
                        )
                        missions.append(p_mission)
                        global_seq += 1
                        subject_learning_streaks[subj.name] = 0

        # For any subject that ended without a final consolidation milestone, add one at the end
        for subj in parsed_subjects:
            if subject_learning_streaks[subj.name] > 0:
                last_topic = subject_queues[subj.name][-1]
                final_mission = self._build_mission(
                    title=f"{subj.name} Final Milestone Assessment: {last_topic}",
                    m_type=MissionType.ASSIGNMENT,
                    subject=subj.name,
                    topic=last_topic,
                    week=total_weeks,
                    sequence=global_seq,
                    priority="HIGH",
                    estimated_minutes=120,
                    degree_program=degree,
                )
                missions.append(final_mission)
                global_seq += 1

        # Build subject tracks with full topic lists (no truncation)
        subject_tracks: List[SubjectTrack] = []
        for s in parsed_subjects:
            s_missions = [m for m in missions if m.subject.strip().lower() == s.name.strip().lower()]
            canonical = get_canonical_curriculum(s.name)
            subject_tracks.append(
                SubjectTrack(
                    subject_name=s.name,
                    mission_count=len(s_missions),
                    estimated_total_minutes=sum(m.estimated_minutes for m in s_missions),
                    core_topics=s.topics,
                    chapters=s.chapters if s.chapters else (canonical["chapters"] if canonical else []),
                )
            )

        return AIMLRoadmapResponse(
            scope=scope,
            subject_tracks=subject_tracks,
            semesters=semesters,
            career=career,
            goals=goals,
            milestones=milestones,
            missions=missions,
        )


    # -------------------------------------------------------------------------
    # Helper & Sanitization Utilities
    # -------------------------------------------------------------------------
    def _calculate_total_weeks(self, request: AnalyzeContextRequest) -> int:
        """Calculates total weeks for the roadmap (default 16 weeks for full semester)."""
        schedule = getattr(request, "schedule", None) or {}
        if isinstance(schedule, dict):
            for k in ("weeks_remaining", "total_weeks"):
                if schedule.get(k):
                    try:
                        w = int(schedule[k])
                        if 4 <= w <= 24:
                            return w
                    except (ValueError, TypeError):
                        pass
            end_date_str = schedule.get("semester_end_date") or schedule.get("end_date")
            if end_date_str:
                try:
                    from datetime import datetime, date
                    end_dt = datetime.strptime(str(end_date_str)[:10], "%Y-%m-%d").date()
                    diff_days = (end_dt - date.today()).days
                    if diff_days > 14:
                        return max(4, min(24, diff_days // 7))
                except Exception:
                    pass

        education = request.education or {}
        if isinstance(education, dict):
            end_date_str = education.get("semester_end_date") or education.get("term_end_date")
            if end_date_str:
                try:
                    from datetime import datetime, date
                    end_dt = datetime.strptime(str(end_date_str)[:10], "%Y-%m-%d").date()
                    diff_days = (end_dt - date.today()).days
                    if diff_days > 14:
                        return max(4, min(24, diff_days // 7))
                except Exception:
                    pass

        return 16

    def _build_mission(
        self,
        title: str,
        m_type: MissionType,
        subject: str,
        topic: str,
        week: int,
        sequence: int,
        priority: str = "HIGH",
        estimated_minutes: int = 90,
        degree_program: Optional[str] = None,
        academic_domain: Optional[str] = None,
        chapter: Optional[str] = None,
    ) -> RoadmapMission:
        """Constructs a structured, domain-adaptive RoadmapMission with explicit sub-fields."""
        archetype = classify_domain(
            subject=subject,
            degree_program=degree_program,
            topic=topic,
            academic_domain=academic_domain,
        )

        if archetype == DomainArchetype.BUSINESS_MANAGEMENT:
            if m_type == MissionType.LEARNING:
                objectives = f"Analyze core principles, executive decision frameworks, and strategic alignment of {topic} within {subject}."
                core_concepts = f"Strategic leadership, organizational frameworks, stakeholder governance, and operational coordination in {topic}."
                deliverables = f"Formulate executive briefing notes, case analyses, and organizational implementation frameworks for {topic}."
                mastery_criteria = f"Attain >= 85% on comprehension checks and articulate defensible managerial trade-offs."
            elif m_type == MissionType.PRACTICAL:
                objectives = f"Apply management frameworks to evaluate real-world corporate case studies in {topic}."
                core_concepts = f"Applied problem solving, cross-functional team coordination, and bottleneck remediation in {topic}."
                deliverables = f"Complete corporate case analysis report detailing strategic diagnosis and action plan for {topic}."
                mastery_criteria = f"Satisfy professional case study rubric benchmarks with actionable organizational recommendations."
            elif m_type == MissionType.CAREER:
                objectives = f"Synthesize business management achievements in {subject} into executive career credentials."
                core_concepts = f"Strategic leadership articulation, portfolio case study presentation, and management competency frameworks."
                deliverables = f"Draft professional leadership portfolio case study and complete executive interview walkthroughs."
                mastery_criteria = f"Verified managerial competency articulation and executive communication clarity."
            else:
                objectives = f"Consolidate learning and evaluate strategic mastery across core competencies of {topic}."
                core_concepts = f"Critical evaluation, synthesized management principles, and executive decision-making in {topic}."
                deliverables = f"Submit comprehensive business case synthesis and strategic review on {topic}."
                mastery_criteria = f"Demonstrate mastery of core managerial principles with zero conceptual ambiguities."

        elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT:
            if m_type == MissionType.LEARNING:
                objectives = f"Master financial recording principles, ledger equilibrium, and mathematical formulations governing {topic}."
                core_concepts = f"GAAP/IFRS conventions, balance identities, double-entry mechanics, and fiscal ratios in {topic}."
                deliverables = f"Complete structured journal entries, ledger postings, and balance calculations for {topic}."
                mastery_criteria = f"Attain 100% mathematical accuracy on ledger reconciliation and fiscal identity checks."
            elif m_type == MissionType.PRACTICAL:
                objectives = f"Solve step-by-step worked numerical problems and construct financial worksheets for {topic}."
                core_concepts = f"Applied ledger balances, trial balance verification, and cost-volume calculations in {topic}."
                deliverables = f"Submit completed financial workbook and numerical ledger solutions with verified audit trails."
                mastery_criteria = f"Pass numerical precision benchmarks with zero balancing errors or omissions."
            elif m_type == MissionType.CAREER:
                objectives = f"Translate quantitative and financial expertise in {subject} into professional analyst credentials."
                core_concepts = f"Financial modeling articulation, audited workbook defense, and fiscal analysis frameworks."
                deliverables = f"Produce audited financial valuation portfolio and complete technical interview walkthroughs."
                mastery_criteria = f"Demonstrated quantitative precision and professional fiscal reporting standards."
            else:
                objectives = f"Evaluate financial analysis proficiency and audited reporting standards in {topic}."
                core_concepts = f"Financial statement audit, variance analysis, and ratio interpretation in {topic}."
                deliverables = f"Comprehensive problem set solution and analytical financial memorandum for {topic}."
                mastery_criteria = f"Satisfy formal accounting standards and demonstrate quantitative precision."

        elif archetype == DomainArchetype.APPLIED_OFFICE_IT:
            if m_type == MissionType.LEARNING:
                objectives = f"Learn interface operations, structured data layouts, and formula syntax for {topic}."
                core_concepts = f"Absolute/relative cell references, dynamic functions, data hygiene, and automated workflows in {topic}."
                deliverables = f"Construct standardized workbook templates and formula-driven data models for {topic}."
                mastery_criteria = f"Achieve flawless formula execution and clean data organization without hardcoded values."
            elif m_type == MissionType.PRACTICAL:
                objectives = f"Implement hands-on digital tools, dynamic lookups, and reporting summaries for {topic}."
                core_concepts = f"XLOOKUP/INDEX-MATCH, nested conditionals, PivotTables, and data validation rules in {topic}."
                deliverables = f"Submit fully functioning automated spreadsheet model with dynamic dashboard for {topic}."
                mastery_criteria = f"Verify dynamic recalculation, input sanitization, and clean visual presentation."
            elif m_type == MissionType.CAREER:
                objectives = f"Showcase workplace productivity, data automation, and analytical reporting skills in {subject}."
                core_concepts = f"Automated reporting workflows, enterprise spreadsheet modeling, and executive summary dashboards."
                deliverables = f"Construct production-grade business reporting dashboard portfolio piece with automated formulas."
                mastery_criteria = f"Demonstrate professional data hygiene, scalable formula design, and actionable visual presentation."
            else:
                objectives = f"Consolidate applied computing efficiency and workplace automation skills in {topic}."
                core_concepts = f"End-to-end data pipeline, automated auditing, and multi-sheet reporting in {topic}."
                deliverables = f"Deliver workplace-ready automated reporting workbook and functional documentation."
                mastery_criteria = f"100% test pass on edge cases, automated recalculation, and usability benchmarks."

        elif archetype == DomainArchetype.CODING_CS:
            if m_type == MissionType.LEARNING:
                objectives = f"Master computational theory, algorithmic mechanics, and state space complexity of {topic}."
                core_concepts = f"Algorithmic paradigms, time/space complexity bounds, structural invariants, and edge cases in {topic}."
                deliverables = f"Trace algorithmic transitions, analyze complexity bounds, and write conceptual proofs for {topic}."
                mastery_criteria = f"Attain >= 85% on technical comprehension checks and runtime asymptotic proofs."
            elif m_type == MissionType.PRACTICAL:
                objectives = f"Implement a modular, tested, and optimized algorithmic code module realizing {topic}."
                core_concepts = f"Clean encapsulation, defensive input validation, memory efficiency, and unit testing in {topic}."
                deliverables = f"Production-grade code implementation with comprehensive unit and boundary test suites."
                mastery_criteria = f"100% test pass rate across positive, negative, and edge-case test harnesses."
            elif m_type == MissionType.CAREER:
                objectives = f"Translate technical achievements in {subject} into high-impact engineering career credentials."
                core_concepts = f"Google XYZ bullet formulation, architectural system design articulation, and algorithmic problem defense."
                deliverables = f"Draft portfolio case study and complete architectural interview walkthroughs."
                mastery_criteria = f"Verified technical articulation, clean code scoring, and rigorous complexity proofs."
            else:
                objectives = f"Solve complex competitive programming benchmarks and system optimization challenges in {topic}."
                core_concepts = f"Benchmark profiling, memory allocation tuning, and algorithmic optimization in {topic}."
                deliverables = f"Optimized implementation benchmarked against stress workloads with performance telemetry."
                mastery_criteria = f"Demonstrate optimal asymptotic complexity with zero memory leaks or regressions."

        else: # GENERAL_HUMANITIES_SCIENCE
            if m_type == MissionType.LEARNING:
                objectives = f"Examine theoretical frameworks, historical context, and core principles of {topic}."
                core_concepts = f"Methodological perspectives, critical discourse, and foundational literature in {topic}."
                deliverables = f"Structured analytical reading notes and comparative conceptual summaries for {topic}."
                mastery_criteria = f"Demonstrate nuanced critical understanding of core arguments and empirical evidence."
            elif m_type == MissionType.PRACTICAL:
                objectives = f"Conduct applied inquiry and empirical case evaluations investigating {topic}."
                core_concepts = f"Qualitative analysis, empirical evidence gathering, and thematic synthesis in {topic}."
                deliverables = f"Applied case report analyzing real-world implications and empirical data on {topic}."
                mastery_criteria = f"Satisfy academic rubric standards with rigorous evidence-based argumentation."
            elif m_type == MissionType.CAREER:
                objectives = f"Translate critical inquiry and research achievements in {subject} into professional analytical credentials."
                core_concepts = f"Evidence-based analysis, policy evaluation, and structured scholarly communication."
                deliverables = f"Publish analytical research portfolio artifact and articulate findings in executive presentation."
                mastery_criteria = f"Demonstrate rigorous methodology and clear scholarly articulation."
            else:
                objectives = f"Synthesize academic perspectives and evaluate contemporary debates in {topic}."
                core_concepts = f"Interdisciplinary synthesis, theoretical critiques, and forward-looking research in {topic}."
                deliverables = f"Comprehensive research brief and critical evaluation essay on {topic}."
                mastery_criteria = f"Demonstrate rigorous synthesis and clear scholarly articulation."

        description = (
            f"🎯 Objectives: {objectives}\n"
            f"📚 Core Concepts: {core_concepts}\n"
            f"💻 Deliverables: {deliverables}\n"
            f"✅ Mastery Criteria: {mastery_criteria}"
        )

        return RoadmapMission(
            title=title,
            type=m_type,
            description=description,
            priority=priority,
            estimated_minutes=estimated_minutes,
            subject=subject,
            topic=topic,
            chapter=chapter,
            objectives=objectives,
            core_concepts=core_concepts,
            deliverables=deliverables,
            mastery_criteria=mastery_criteria,
            week=week,
            sequence=sequence,
        )

    def _parse_subjects(
        self, syllabus: Dict[str, Any], selected_subjects: Optional[List[str]] = None
    ) -> List[RoadmapSubject]:
        raw_subjects = syllabus.get("subjects") or []
        parsed_subjects: List[RoadmapSubject] = []

        selected_lookup = {s.strip().lower() for s in selected_subjects} if selected_subjects else set()

        if isinstance(raw_subjects, list):
            for s in raw_subjects:
                if isinstance(s, dict) and s.get("name"):
                    s_name = str(s["name"]).strip()
                    if selected_lookup and s_name.lower() not in selected_lookup:
                        continue
                    canonical = get_canonical_curriculum(s_name)
                    raw_topics = [str(t) for t in s.get("topics", [])]
                    if not raw_topics and canonical:
                        raw_topics = [c["title"] for c in canonical["chapters"]]
                    parsed_subjects.append(
                        RoadmapSubject(
                            name=s_name,
                            topics=raw_topics,
                            chapters=canonical["chapters"] if canonical else [],
                        )
                    )

        if not parsed_subjects:
            parsed_subjects = [
                RoadmapSubject(
                    name="Data Structures & Algorithms",
                    topics=["Arrays & Lists", "Trees & Graphs", "Dynamic Programming", "Sorting & Searching"],
                ),
                RoadmapSubject(
                    name="System Design & Architecture",
                    topics=["REST APIs", "Microservices", "Caching & Queues", "Relational Databases"],
                ),
            ]
        return parsed_subjects

    def _sanitize_and_parse_response(
        self,
        raw_llm_output: str,
        scope: str,
        target_subject: Optional[str] = None,
        expected_topics: Optional[List[str]] = None,
        parsed_subjects: Optional[List[RoadmapSubject]] = None,
    ) -> Optional[AIMLRoadmapResponse]:
        json_text = extract_json_payload(raw_llm_output)
        data = json.loads(json_text)
        if not (isinstance(data, dict) and "missions" in data and isinstance(data["missions"], list)):
            return None

        valid_types = {t.value for t in MissionType}
        sanitized_missions: List[RoadmapMission] = []

        known_subject_names = [s.name for s in (parsed_subjects or [])]

        for idx, m in enumerate(data["missions"]):
            if not isinstance(m, dict):
                continue

            # Normalize mission type
            raw_type = str(m.get("type", "LEARNING")).upper()
            if raw_type not in valid_types:
                if any(k in raw_type for k in ["READ", "STUDY", "LEAD", "THEORY", "CONCEPT"]):
                    m["type"] = MissionType.LEARNING
                elif any(k in raw_type for k in ["PRACT", "CODE", "EXERCISE", "HANDS"]):
                    m["type"] = MissionType.PRACTICAL
                elif any(k in raw_type for k in ["REV", "RECAP", "SUMMARY"]):
                    m["type"] = MissionType.REVISION
                elif any(k in raw_type for k in ["ASSIGN", "TEST", "QUIZ", "HOMEWORK"]):
                    m["type"] = MissionType.ASSIGNMENT
                elif any(k in raw_type for k in ["ARTIF", "PROJ", "BUILD"]):
                    m["type"] = MissionType.ARTIFACT
                elif any(k in raw_type for k in ["CAREER", "JOB", "RESUME", "INTERVIEW"]):
                    m["type"] = MissionType.CAREER
                else:
                    m["type"] = MissionType.LEARNING
            else:
                m["type"] = MissionType(raw_type)

            # Normalize priority
            raw_prio = str(m.get("priority", "MEDIUM")).upper()
            if raw_prio not in {"HIGH", "MEDIUM", "LOW"}:
                m["priority"] = "MEDIUM"

            # Strict subject assignment
            if target_subject:
                m["subject"] = target_subject
            else:
                current_subj = (m.get("subject") or "").strip()
                if not current_subj or current_subj.lower() == "general":
                    if known_subject_names:
                        m["subject"] = known_subject_names[idx % len(known_subject_names)]
                    else:
                        m["subject"] = "Computer Systems"
                else:
                    m["subject"] = current_subj

            # Integers
            m["estimated_minutes"] = max(15, int(m.get("estimated_minutes") or 60))
            m["week"] = max(1, int(m.get("week") or ((idx // 3) + 1)))
            m["sequence"] = max(1, int(m.get("sequence") or ((idx % 3) + 1)))

            # Description check
            desc = str(m.get("description") or "").strip()
            if not desc or len(desc) < 30:
                m["description"] = (
                    f"🎯 Objectives: Master essential competencies for {m.get('title')}.\n"
                    f"📚 Core Concepts: Invariants, algorithmic complexity, and failure modes.\n"
                    f"💻 Deliverables: Implement modular solutions and verify via automated unit tests.\n"
                    f"✅ Mastery Criteria: Pass test benchmarks and diagnostic assessments."
                )

            sanitized_missions.append(RoadmapMission.model_validate(m))

        if not sanitized_missions:
            return None

        # Ensure full syllabus coverage: every parsed subject must have at least 2 progressive missions
        if not target_subject and parsed_subjects:
            current_max_seq = max((m.sequence for m in sanitized_missions), default=len(sanitized_missions))
            for subj in parsed_subjects:
                subj_missions = [m for m in sanitized_missions if m.subject.strip().lower() == subj.name.strip().lower()]
                if len(subj_missions) < 2:
                    topics_pool = subj.topics if subj.topics else [f"{subj.name} Core Principles"]
                    for extra_idx in range(len(subj_missions), min(3, max(2, len(topics_pool)))):
                        current_max_seq += 1
                        t_name = topics_pool[extra_idx % len(topics_pool)]
                        m_type = MissionType.PRACTICAL if extra_idx == 1 else MissionType.ASSIGNMENT
                        title = f"Practical Implementation: {t_name}" if extra_idx == 1 else f"Problem Solving: {t_name}"
                        desc = (
                            f"🎯 Objectives: Master applied implementation and edge-case resolution for {t_name} in {subj.name}.\n"
                            f"📚 Core Concepts: Architectural invariants, memory constraints, and defensive validation.\n"
                            f"💻 Deliverables: Implement verified solution module with unit test coverage.\n"
                            f"✅ Mastery Criteria: Pass all validation benchmarks without performance degradation."
                        )
                        sanitized_missions.append(
                            RoadmapMission(
                                title=title,
                                type=m_type,
                                description=desc,
                                priority="HIGH" if extra_idx == 1 else "MEDIUM",
                                estimated_minutes=75,
                                subject=subj.name,
                                week=extra_idx + 1,
                                sequence=current_max_seq,
                            )
                        )

        # Build subject tracks
        subject_tracks: List[SubjectTrack] = []
        if target_subject:
            canonical = get_canonical_curriculum(target_subject)
            subject_tracks.append(
                SubjectTrack(
                    subject_name=target_subject,
                    mission_count=len(sanitized_missions),
                    estimated_total_minutes=sum(m.estimated_minutes for m in sanitized_missions),
                    core_topics=(expected_topics or [target_subject]),
                    chapters=canonical["chapters"] if canonical else [],
                )
            )
        else:
            subjects_map = {s.name.lower(): s for s in (parsed_subjects or [])}
            unique_subjects = {m.subject for m in sanitized_missions}
            for s in (parsed_subjects or []):
                unique_subjects.add(s.name)
            for s_name in sorted(unique_subjects):
                s_missions = [m for m in sanitized_missions if m.subject.lower() == s_name.lower()]
                orig_subj = subjects_map.get(s_name.lower())
                canonical = get_canonical_curriculum(s_name)
                subject_tracks.append(
                    SubjectTrack(
                        subject_name=s_name,
                        mission_count=len(s_missions),
                        estimated_total_minutes=sum(m.estimated_minutes for m in s_missions),
                        core_topics=orig_subj.topics if orig_subj else [s_name],
                        chapters=(orig_subj.chapters if orig_subj and orig_subj.chapters else (canonical["chapters"] if canonical else [])),
                    )
                )

        data["missions"] = sanitized_missions
        data["scope"] = scope
        data["target_subject"] = target_subject
        data["subject_tracks"] = subject_tracks

        return AIMLRoadmapResponse.model_validate(data)


_roadmap_service_instance: Optional[RoadmapService] = None


def get_roadmap_service() -> RoadmapService:
    global _roadmap_service_instance
    if _roadmap_service_instance is None:
        _roadmap_service_instance = RoadmapService()
    return _roadmap_service_instance

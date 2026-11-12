import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.schemas.context_v2 import AnalyzeContextRequest
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
        primary_goal = learner.get("primary_goal") or f"Mastery in {target_subject}"

        topics: List[str] = []
        for s in syllabus.get("subjects", []):
            if isinstance(s, dict) and s.get("name", "").strip().lower() == target_subject.lower():
                topics = [str(t) for t in s.get("topics", [])]
                break
        if not topics:
            topics = [
                f"{target_subject} Fundamentals & Data Layouts",
                f"{target_subject} Core Architecture & Protocols",
                f"{target_subject} Advanced Algorithms & Optimization",
                f"{target_subject} Systems Reliability & Production Engineering",
            ]

        missions: List[RoadmapMission] = []
        seq = 1

        t1 = topics[0]
        t2 = topics[1] if len(topics) > 1 else f"{target_subject} Architecture"
        t3 = topics[2] if len(topics) > 2 else f"{target_subject} Advanced Systems"

        # Week 1: Foundations & Architecture
        missions.append(
            RoadmapMission(
                title=f"Theoretical Invariants of {t1}",
                type=MissionType.LEARNING,
                description=(
                    f"🎯 Objectives: Deep-dive conceptual exploration of {t1} within {target_subject}.\n"
                    f"📚 Core Concepts: Foundational memory models, invariant proofs, and structural mechanics.\n"
                    f"💻 Deliverables: Trace state transitions, memory allocations, and execution invariants through detailed analytical notes.\n"
                    f"✅ Mastery Criteria: Attain >= 85% accuracy on conceptual comprehension checks and runtime analysis."
                ),
                priority="HIGH",
                estimated_minutes=90,
                subject=target_subject,
                week=1,
                sequence=seq,
            )
        )
        seq += 1

        missions.append(
            RoadmapMission(
                title=f"Hands-on Implementation: {t1} Core Module",
                type=MissionType.PRACTICAL,
                description=(
                    f"🎯 Objectives: Construct a modular, robust software module realizing {t1}.\n"
                    f"📚 Core Concepts: Clean encapsulation, defensive boundary validation, and exception management.\n"
                    f"💻 Deliverables: Working code repository containing algorithmic implementation with automated unit tests.\n"
                    f"✅ Mastery Criteria: 100% test pass rate across positive, negative, and edge-case boundary suites."
                ),
                priority="HIGH",
                estimated_minutes=90,
                subject=target_subject,
                week=1,
                sequence=seq,
            )
        )
        seq += 1

        missions.append(
            RoadmapMission(
                title=f"Analytical Verification: {t1} Invariants",
                type=MissionType.ASSIGNMENT,
                description=(
                    f"🎯 Objectives: Validate deep invariant retention and formal edge-case handling in {t1}.\n"
                    f"📚 Core Concepts: Invariant preservation under stress, concurrency, and constrained resource environments.\n"
                    f"💻 Deliverables: Formal diagnostic problem sets and benchmark proofs.\n"
                    f"✅ Mastery Criteria: Flawless invariant verification against simulated failure injections."
                ),
                priority="MEDIUM",
                estimated_minutes=60,
                subject=target_subject,
                week=1,
                sequence=seq,
            )
        )
        seq += 1

        # Week 2: Core Mechanics & Algorithmic Optimization
        missions.append(
            RoadmapMission(
                title=f"Advanced Mechanics & Complexity in {t2}",
                type=MissionType.LEARNING,
                description=(
                    f"🎯 Objectives: Analyze algorithmic complexity, data structures, and edge-case heuristics in {t2}.\n"
                    f"📚 Core Concepts: Asymptotic bounds, memory access locality, and contention mitigation.\n"
                    f"💻 Deliverables: Architectural comparison breakdown contrasting alternative design strategies.\n"
                    f"✅ Mastery Criteria: Precise asymptotic categorization and bottleneck identification."
                ),
                priority="HIGH",
                estimated_minutes=75,
                subject=target_subject,
                week=2,
                sequence=seq,
            )
        )
        seq += 1

        missions.append(
            RoadmapMission(
                title=f"High-Throughput Optimization & Benchmarking: {t2}",
                type=MissionType.PRACTICAL,
                description=(
                    f"🎯 Objectives: Engineer and benchmark an optimized implementation of {t2}.\n"
                    f"📚 Core Concepts: Profiling, memory pooling, cache-friendly data structures, and zero-copy semantics.\n"
                    f"💻 Deliverables: Benchmarking test harness reporting operations/sec and memory allocations.\n"
                    f"✅ Mastery Criteria: Verified throughput improvement without regression on correct results."
                ),
                priority="HIGH",
                estimated_minutes=90,
                subject=target_subject,
                week=2,
                sequence=seq,
            )
        )
        seq += 1

        missions.append(
            RoadmapMission(
                title=f"Failure Mode Analysis & Robustness Review: {t2}",
                type=MissionType.REVISION,
                description=(
                    f"🎯 Objectives: Consolidate comprehension and analyze real-world system outages related to {t2}.\n"
                    f"📚 Core Concepts: Chaos engineering, circuit breaking, and defensive degrade modes.\n"
                    f"💻 Deliverables: Post-mortem remediation report and regression test plan.\n"
                    f"✅ Mastery Criteria: Complete coverage of all identified failure modes."
                ),
                priority="MEDIUM",
                estimated_minutes=60,
                subject=target_subject,
                week=2,
                sequence=seq,
            )
        )
        seq += 1

        # Week 3: Systems Integration & Capstone
        missions.append(
            RoadmapMission(
                title=f"Production Architecture & Integration: {t3}",
                type=MissionType.LEARNING,
                description=(
                    f"🎯 Objectives: Synthesize end-to-end integration patterns combining {t1}, {t2}, and {t3}.\n"
                    f"📚 Core Concepts: Distributed coordination, event logging, fault tolerance, and API contracts.\n"
                    f"💻 Deliverables: System design specification with sequence diagrams and data flow contracts.\n"
                    f"✅ Mastery Criteria: Architectural review sign-off against industry reliability benchmarks."
                ),
                priority="HIGH",
                estimated_minutes=90,
                subject=target_subject,
                week=3,
                sequence=seq,
            )
        )
        seq += 1

        missions.append(
            RoadmapMission(
                title=f"End-to-End Capstone Project: {target_subject}",
                type=MissionType.ARTIFACT,
                description=(
                    f"🎯 Objectives: Build a production-grade portfolio project encapsulating all key concepts of {target_subject}.\n"
                    f"📚 Core Concepts: Modular clean architecture, continuous integration, telemetry, and documentation.\n"
                    f"💻 Deliverables: Publish a structured GitHub repository with README, architecture diagram, and deployment instructions.\n"
                    f"✅ Mastery Criteria: Production readiness, clear operational runbook, and clean code scoring."
                ),
                priority="HIGH",
                estimated_minutes=120,
                subject=target_subject,
                week=3,
                sequence=seq,
            )
        )
        seq += 1

        # Week 4 (if CAREER or BOTH):
        if scope in {"CAREER", "BOTH"}:
            missions.append(
                RoadmapMission(
                    title=f"Technical Interview Review & Portfolio Articulation: {target_subject}",
                    type=MissionType.CAREER,
                    description=(
                        f"🎯 Objectives: Translate technical achievements in {target_subject} into high-impact career credentials.\n"
                        f"📚 Core Concepts: Google XYZ bullet formulation (Accomplished [X], as measured by [Y], by doing [Z]).\n"
                        f"💻 Deliverables: Draft portfolio case study and complete architectural interview walkthroughs targeting '{primary_goal}'.\n"
                        f"✅ Mastery Criteria: Verified ATS keyword density and executive technical articulation."
                    ),
                    priority="MEDIUM",
                    estimated_minutes=60,
                    subject=target_subject,
                    week=4,
                    sequence=seq,
                )
            )

        semesters = [
            RoadmapSemester(
                name="Dedicated Subject Track",
                subjects=[RoadmapSubject(name=target_subject, topics=topics[:6])],
            )
        ] if scope in {"ACADEMIC", "BOTH"} else []

        career = (
            RoadmapCareer(
                goals=[
                    f"Achieve specialized production mastery in {target_subject}",
                    f"Ship {target_subject} Capstone System",
                ]
            )
            if scope in {"CAREER", "BOTH"}
            else None
        )

        subject_tracks = [
            SubjectTrack(
                subject_name=target_subject,
                mission_count=len(missions),
                estimated_total_minutes=sum(m.estimated_minutes for m in missions),
                core_topics=topics[:6],
            )
        ]

        goals = [
            f"Achieve production-grade proficiency in {target_subject}",
            f"Construct and validate an end-to-end portfolio capstone for {target_subject}",
        ]
        milestones = [
            f"Week 1: {t1} Foundations & Invariants",
            f"Week 2: {t2} Optimization & Benchmarking",
            f"Week 3: {target_subject} Production Capstone Deployment",
        ]
        if scope in {"CAREER", "BOTH"}:
            milestones.append(f"Week 4: {target_subject} Technical Articulation & Career Readiness")

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
            "CONTENT MAXIMIZATION & MULTI-SUBJECT GUIDELINES:\n"
            "- Interleave missions across all syllabus subjects evenly across weeks.\n"
            "- Every mission MUST explicitly designate its exact 'subject' name from the syllabus.\n"
            "- Provide rich, detailed, granular topics for each subject (5-8 topics per subject).\n"
            "- Provide multiple structured goals and clear week-by-week milestones.\n"
            "- Generate 8 to 14 sequential missions across 3 to 4 weeks.\n"
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

        primary_goal = learner.get("primary_goal") or "Master Software Engineering Competencies"
        degree = education.get("degree_program") or "Computer Science"

        parsed_subjects = self._parse_subjects(syllabus, request.selected_subjects)

        # Semesters
        semesters: List[RoadmapSemester] = []
        if scope in {"ACADEMIC", "BOTH"}:
            semesters.append(RoadmapSemester(name="Current Term", subjects=parsed_subjects[:4]))

        # Career
        career = None
        if scope in {"CAREER", "BOTH"}:
            career = RoadmapCareer(goals=[primary_goal, "Production Architecture Portfolio Project"])

        goals = [
            f"Achieve topic mastery across {len(parsed_subjects)} core syllabus subjects",
            f"Build production-grade systems targeting '{primary_goal}'",
        ]
        milestones = [
            "Week 1: Algorithmic foundations & core theoretical invariants across subjects",
            "Week 2: Hands-on modular implementation and unit testing across subjects",
            "Week 3: Benchmark problem solving, optimization, and edge-case verification",
            "Week 4: End-to-end capstone integration and portfolio artifact synthesis",
        ]

        missions: List[RoadmapMission] = []
        global_seq = 1

        # Interleave 4 weeks across subjects
        for week_num in range(1, 4):
            for s_idx, subj in enumerate(parsed_subjects):
                top_idx = (week_num - 1) % max(1, len(subj.topics))
                topic = subj.topics[top_idx] if subj.topics else f"{subj.name} Module {week_num}"

                if week_num == 1:
                    m_type = MissionType.LEARNING
                    title = f"Study {topic} Invariants & Core Theory"
                    desc = (
                        f"🎯 Objectives: Deep-dive conceptual exploration of {topic} within {subj.name}.\n"
                        f"📚 Core Concepts: Foundational memory layouts, computational invariants, and structural constraints.\n"
                        f"💻 Deliverables: Trace execution graphs, invariant proofs, and state transitions.\n"
                        f"✅ Mastery Criteria: Achieve >= 85% on comprehension checks with zero conceptual misconceptions."
                    )
                    prio = "HIGH"
                    est = 90
                elif week_num == 2:
                    m_type = MissionType.PRACTICAL
                    title = f"Implement Hands-on {topic} Solution"
                    desc = (
                        f"🎯 Objectives: Construct a modular, production-grade implementation of {topic}.\n"
                        f"📚 Core Concepts: Encapsulation, defensive boundary validation, and error propagation handling.\n"
                        f"💻 Deliverables: Develop an end-to-end executable module with comprehensive unit test coverage.\n"
                        f"✅ Mastery Criteria: Pass all functional test cases and verify algorithmic efficiency under stress."
                    )
                    prio = "HIGH"
                    est = 90
                else:
                    m_type = MissionType.ASSIGNMENT if s_idx % 2 == 0 else MissionType.REVISION
                    title = f"Mastery Check: {topic} Problem Solving"
                    desc = (
                        f"🎯 Objectives: Evaluate conceptual retention and analytical problem-solving in {topic}.\n"
                        f"📚 Core Concepts: Resolve edge cases, off-by-one errors, and multi-variable state transitions.\n"
                        f"💻 Deliverables: Complete structured benchmark assessment tasks with analytical justifications.\n"
                        f"✅ Mastery Criteria: Satisfy formal rubric criteria across correctness, optimization, and code clarity."
                    )
                    prio = "MEDIUM"
                    est = 60

                missions.append(
                    RoadmapMission(
                        title=title,
                        type=m_type,
                        description=desc,
                        priority=prio,
                        estimated_minutes=est,
                        subject=subj.name,
                        week=week_num,
                        sequence=global_seq,
                    )
                )
                global_seq += 1

        # Capstone artifacts in Week 4
        if scope in {"CAREER", "BOTH"}:
            capstone_subj = parsed_subjects[0].name if parsed_subjects else "Computer Systems"
            missions.append(
                RoadmapMission(
                    title="Portfolio Artifact: End-to-End System Integration",
                    type=MissionType.ARTIFACT,
                    description=(
                        "🎯 Objectives: Synthesize learned competencies into an end-to-end, production-grade portfolio artifact.\n"
                        "📚 Core Concepts: Clean modular architecture, automated test suites, and comprehensive documentation.\n"
                        "💻 Deliverables: Publish a structured repository containing system README, architecture diagram, and deployment instructions.\n"
                        "✅ Mastery Criteria: Peer review readiness and adherence to industry open-source standards."
                    ),
                    priority="HIGH",
                    estimated_minutes=120,
                    subject=capstone_subj,
                    week=4,
                    sequence=global_seq,
                )
            )
            global_seq += 1
            missions.append(
                RoadmapMission(
                    title="Career Readiness: Resume Tailoring & Technical Interview Review",
                    type=MissionType.CAREER,
                    description=(
                        f"🎯 Objectives: Bridge technical milestones into high-impact professional career credentials.\n"
                        f"📚 Core Concepts: Google XYZ resume formulation (Accomplished [X], as measured by [Y], by doing [Z]).\n"
                        f"💻 Deliverables: Draft targeted bullet points and complete architectural mock interview walkthroughs targeting '{primary_goal}'.\n"
                        f"✅ Mastery Criteria: Verified ATS keyword density and crisp executive technical articulation."
                    ),
                    priority="MEDIUM",
                    estimated_minutes=60,
                    subject="Career Readiness",
                    week=4,
                    sequence=global_seq,
                )
            )

        # Subject tracks aggregation
        subject_tracks: List[SubjectTrack] = []
        for subj in parsed_subjects:
            s_missions = [m for m in missions if m.subject.strip().lower() == subj.name.strip().lower()]
            subject_tracks.append(
                SubjectTrack(
                    subject_name=subj.name,
                    mission_count=len(s_missions),
                    estimated_total_minutes=sum(m.estimated_minutes for m in s_missions),
                    core_topics=subj.topics[:6],
                )
            )

        return AIMLRoadmapResponse(
            scope=scope,
            target_subject=None,
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
                    parsed_subjects.append(
                        RoadmapSubject(
                            name=s_name,
                            topics=[str(t) for t in s.get("topics", [])[:6]],
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

        # Build subject tracks
        subject_tracks: List[SubjectTrack] = []
        if target_subject:
            subject_tracks.append(
                SubjectTrack(
                    subject_name=target_subject,
                    mission_count=len(sanitized_missions),
                    estimated_total_minutes=sum(m.estimated_minutes for m in sanitized_missions),
                    core_topics=(expected_topics or [target_subject])[:6],
                )
            )
        else:
            subjects_map = {s.name.lower(): s for s in (parsed_subjects or [])}
            unique_subjects = {m.subject for m in sanitized_missions}
            for s_name in sorted(unique_subjects):
                s_missions = [m for m in sanitized_missions if m.subject.lower() == s_name.lower()]
                orig_subj = subjects_map.get(s_name.lower())
                subject_tracks.append(
                    SubjectTrack(
                        subject_name=s_name,
                        mission_count=len(s_missions),
                        estimated_total_minutes=sum(m.estimated_minutes for m in s_missions),
                        core_topics=orig_subj.topics[:6] if orig_subj else [s_name],
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

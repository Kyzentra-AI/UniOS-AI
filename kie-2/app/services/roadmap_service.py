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
)
from app.services.llm_provider import extract_json_payload, get_llm_provider

logger = logging.getLogger(__name__)


class RoadmapService:
    """
    KIE Roadmap Generation Engine (Endpoint 4: POST /api/v1/kie/roadmap/generate).
    Synthesizes academic semesters, career milestones, and sequential weekly missions.
    Strictly adheres to AIMLRoadmapResponse schema required by Backend.
    """

    def generate(self, request: AnalyzeContextRequest) -> AIMLRoadmapResponse:
        raw_scope = (request.scope or "ACADEMIC").upper()
        if raw_scope not in {"ACADEMIC", "CAREER", "BOTH"}:
            raw_scope = "ACADEMIC"

        # 1. Attempt LLM generation if live provider is enabled
        if settings.LLM_PROVIDER.lower() != "mock":
            try:
                llm_response = self._generate_via_llm(request, raw_scope)
                if llm_response and len(llm_response.missions) >= 3:
                    logger.info(f"[RoadmapService] LLM generated roadmap with {len(llm_response.missions)} missions (scope={raw_scope})")
                    return llm_response
            except Exception as e:
                logger.warning(f"[RoadmapService] LLM roadmap generation failed ({e}), using deterministic engine.")

        # 2. Deterministic rule-based roadmap generator
        return self._generate_deterministic(request, raw_scope)

    def _generate_via_llm(self, request: AnalyzeContextRequest, scope: str) -> Optional[AIMLRoadmapResponse]:
        provider = get_llm_provider()
        learner = request.learner or {}
        education = request.education or {}
        syllabus = request.syllabus or {}

        system_instruction = (
            "You are the UniOS Curriculum & Roadmap Synthesis Engine. "
            "Generate a comprehensive, structured learning roadmap with sequential missions based on ContextV2. "
            "Output strictly valid JSON matching this schema:\n"
            "{\n"
            f'  "scope": "{scope}",\n'
            '  "semesters": [\n'
            "    {\n"
            '      "name": "Semester 1",\n'
            '      "subjects": [\n'
            '        {"name": "<Subject Name>", "topics": ["<Topic 1>", "<Topic 2>"]}\n'
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "career": {"goals": ["<Career Goal 1>", "<Career Goal 2>"]},\n'
            '  "goals": ["<Goal 1>", "<Goal 2>"],\n'
            '  "milestones": ["<Milestone 1>", "<Milestone 2>"],\n'
            '  "missions": [\n'
            "    {\n"
            '      "title": "<Mission Title>",\n'
            '      "type": "LEARNING" | "PRACTICAL" | "REVISION" | "ASSIGNMENT" | "ARTIFACT" | "CAREER",\n'
            '      "description": "<Detailed mission steps>",\n'
            '      "priority": "HIGH" | "MEDIUM" | "LOW",\n'
            '      "estimated_minutes": 90,\n'
            '      "subject": "<Subject Name>",\n'
            '      "week": 1,\n'
            '      "sequence": 1\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        user_prompt = f"""CONTEXT V2:
Scope: {scope}
Learner Goal: {learner.get('primary_goal', 'Software Engineer')}
Skills: {learner.get('skills', [])}
Target Skills: {learner.get('target_skills', [])}
Academic: {education.get('degree_program', 'Computer Science')} ({education.get('academic_status', 'BACHELOR')})
Syllabus: {json.dumps(syllabus.get('subjects', [])[:4]) if syllabus else 'Standard curriculum'}
"""
        raw = provider._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1500,
            temperature=0.2,
        )

        json_text = extract_json_payload(raw)
        data = json.loads(json_text)
        if isinstance(data, dict) and "missions" in data and isinstance(data["missions"], list):
            return AIMLRoadmapResponse.model_validate(data)
        return None

    def _generate_deterministic(self, request: AnalyzeContextRequest, scope: str) -> AIMLRoadmapResponse:
        learner = request.learner or {}
        education = request.education or {}
        syllabus = request.syllabus or {}

        primary_goal = learner.get("primary_goal") or "Master Software Engineering Competencies"
        skills = learner.get("skills") or ["Python", "Algorithms"]
        degree = education.get("degree_program") or "Computer Science"

        # Extract subjects from syllabus
        raw_subjects = syllabus.get("subjects") or []
        parsed_subjects: List[RoadmapSubject] = []

        if isinstance(raw_subjects, list):
            for s in raw_subjects:
                if isinstance(s, dict) and s.get("name"):
                    parsed_subjects.append(
                        RoadmapSubject(
                            name=str(s["name"]),
                            topics=[str(t) for t in s.get("topics", [])[:6]],
                        )
                    )

        if not parsed_subjects:
            parsed_subjects = [
                RoadmapSubject(name="Data Structures & Algorithms", topics=["Arrays & Lists", "Trees & Graphs", "Dynamic Programming"]),
                RoadmapSubject(name="System Design & Architecture", topics=["REST APIs", "Microservices", "Caching & Queues"]),
            ]

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
            "Week 1: Core algorithmic foundations & complexity analysis",
            "Week 2: Advanced data structures and tree traversals",
            "Week 3: Asynchronous pipelines and database optimization",
            "Week 4: Capstone build and portfolio artifact synthesis",
        ]

        missions: List[RoadmapMission] = []
        seq = 1

        for idx, subj in enumerate(parsed_subjects[:3]):
            week_num = idx + 1
            top1 = subj.topics[0] if subj.topics else f"{subj.name} Basics"
            top2 = subj.topics[1] if len(subj.topics) > 1 else f"{subj.name} Applied"

            # Mission 1: LEARNING
            missions.append(
                RoadmapMission(
                    title=f"Study {top1} Invariants & Core Theory",
                    type=MissionType.LEARNING,
                    description=f"Deep-dive conceptual explanation of {top1} within {subj.name}. Review memory layout and time complexity.",
                    priority="HIGH",
                    estimated_minutes=90,
                    subject=subj.name,
                    week=week_num,
                    sequence=seq,
                )
            )
            seq += 1

            # Mission 2: PRACTICAL
            missions.append(
                RoadmapMission(
                    title=f"Implement Hands-on {top1} Solution",
                    type=MissionType.PRACTICAL,
                    description=f"Write clean, modular implementation for {top1} with comprehensive unit test coverage in Python.",
                    priority="HIGH",
                    estimated_minutes=90,
                    subject=subj.name,
                    week=week_num,
                    sequence=seq,
                )
            )
            seq += 1

            # Mission 3: REVISION or ASSIGNMENT
            missions.append(
                RoadmapMission(
                    title=f"Mastery Check: {top2} Problem Solving",
                    type=MissionType.ASSIGNMENT if idx % 2 == 0 else MissionType.REVISION,
                    description=f"Solve benchmark evaluation problems covering {top2} to validate retention and edge-case handling.",
                    priority="MEDIUM",
                    estimated_minutes=60,
                    subject=subj.name,
                    week=week_num,
                    sequence=seq,
                )
            )
            seq += 1

        # Capstone mission if CAREER or BOTH
        if scope in {"CAREER", "BOTH"}:
            missions.append(
                RoadmapMission(
                    title="Portfolio Artifact: End-to-End System Integration",
                    type=MissionType.ARTIFACT,
                    description="Package and document your capstone project into a clean repository with README, architecture diagram, and deployment instructions.",
                    priority="HIGH",
                    estimated_minutes=120,
                    subject=parsed_subjects[0].name if parsed_subjects else "Capstone",
                    week=4,
                    sequence=seq,
                )
            )
            seq += 1
            missions.append(
                RoadmapMission(
                    title="Career Readiness: Resume Tailoring & Technical Interview Review",
                    type=MissionType.CAREER,
                    description=f"Synthesize your recent project accomplishments into Google XYZ bullet points targeting '{primary_goal}'.",
                    priority="MEDIUM",
                    estimated_minutes=60,
                    subject="Career Readiness",
                    week=4,
                    sequence=seq,
                )
            )

        return AIMLRoadmapResponse(
            scope=scope,
            semesters=semesters,
            career=career,
            goals=goals,
            milestones=milestones,
            missions=missions,
        )


_roadmap_service_instance: Optional[RoadmapService] = None


def get_roadmap_service() -> RoadmapService:
    global _roadmap_service_instance
    if _roadmap_service_instance is None:
        _roadmap_service_instance = RoadmapService()
    return _roadmap_service_instance


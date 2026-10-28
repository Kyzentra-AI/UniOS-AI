"""
Sprint 5 — Universal Build Engine Prompt Builder (AI/ML-2)

Constructs LLM prompts for:
  1. Contextual Build Coaching  (build_coach_prompt)
  2. Project Recommendations    (build_recommend_prompt)

Follows same pattern as prompt_builder.py:
  - Accepts typed schemas, not raw dicts.
  - Explicitly instructs the LLM to output strictly valid JSON.
  - Embeds domain-adaptive cues and rubric grounding.
  - Token-budgeted to stay within Groq OTPM limits.
"""

from typing import List, Optional

from app.schemas.build import (
    ArtifactType,
    BuildCoachRequest,
    BuildRecommendContext,
)


# ---------------------------------------------------------------------------
# Domain-adaptive style guides (mirrors pedagogy_engine domain mapping)
# ---------------------------------------------------------------------------

_DOMAIN_STYLE: dict = {
    "engineering": "Use precise technical terminology. Refer to algorithms, data structures, system design, and testing practices.",
    "commerce":    "Use financial and business language. Reference accounting standards, market analysis, and case study methodology.",
    "humanities":  "Use analytical and argumentative language. Reference theoretical frameworks, critical thinking, and citation practices.",
    "science":     "Use empirical and experimental language. Reference hypotheses, methodologies, data analysis, and scientific conventions.",
    "management":  "Use strategic and leadership language. Reference frameworks like SWOT, stakeholder analysis, and ROI.",
    "law":         "Use legal reasoning language. Reference statutes, case precedent, IRAC structure, and statutory interpretation.",
}

_ARTIFACT_DESCRIPTIONS: dict = {
    ArtifactType.CODE_PROJECT:    "software implementation project",
    ArtifactType.ESSAY:           "academic essay",
    ArtifactType.RESEARCH_REPORT: "research report or lab report",
    ArtifactType.BUSINESS_PLAN:   "business plan or capstone proposal",
    ArtifactType.CASE_ANALYSIS:   "case study or case brief",
    ArtifactType.DATA_ANALYSIS:   "data analysis project",
    ArtifactType.DESIGN_ARTIFACT: "design or architecture artifact",
    ArtifactType.LAB_NOTEBOOK:    "laboratory notebook or experiment log",
    ArtifactType.ORAL_VIVA:       "oral viva or verbal examination",
    ArtifactType.PORTFOLIO:       "portfolio submission",
    ArtifactType.GENERAL:         "build project",
}


def _domain_guide(domain: Optional[str]) -> str:
    if not domain:
        return "Adapt coaching to the learner's academic context."
    d_lower = domain.strip().lower()
    for key, guide in _DOMAIN_STYLE.items():
        if key in d_lower:
            return guide
    return "Adapt coaching to the learner's academic context."


def _stage_note(stage: Optional[str]) -> str:
    if not stage:
        return ""
    s = stage.strip().lower()
    if s == "master":
        return "The learner is at Master's level — expect depth, theoretical rigour, and advanced analysis."
    if s == "graduate":
        return "The learner is a recent graduate — focus on professional readiness, application, and portfolio quality."
    return "The learner is at Bachelor's level — provide structured scaffolding and clear step-by-step guidance."


# ---------------------------------------------------------------------------
# 1. Coaching Prompt
# ---------------------------------------------------------------------------

def build_coach_prompt(request: BuildCoachRequest) -> str:
    """
    Constructs a token-budgeted prompt for the Contextual Build Coach.
    Target output: 5–7 coaching blocks, ≤ 700 tokens.
    """

    artifact_desc = _ARTIFACT_DESCRIPTIONS.get(request.artifact_type, "build project")
    domain_guide = _domain_guide(request.academic_domain)
    stage_note = _stage_note(request.learner_stage)

    # --- Mastery evidence section ---
    mastery_lines = []
    if request.concept_mastery:
        for concept, score in list(request.concept_mastery.items())[:6]:
            tier = "Weak" if score < 0.50 else ("Developing" if score < 0.80 else "Proficient")
            mastery_lines.append(f"- {concept}: {score:.0%} ({tier})")
    mastery_section = "\n".join(mastery_lines) if mastery_lines else "No concept mastery data provided."

    weak_section = (
        ", ".join(request.weak_topics[:5]) if request.weak_topics else "None reported."
    )

    friction_section = (
        ", ".join(request.relevant_friction[:5]) if request.relevant_friction else "None active."
    )

    # --- Rubric section ---
    rubric_lines = ""
    if request.rubric_criteria:
        rubric_lines = "RUBRIC CRITERIA (provided by Backend — ground all feedback to these):\n"
        rubric_lines += "\n".join(f"  - {c}" for c in request.rubric_criteria[:8])

    # --- Submitted work ---
    work_section = request.submitted_work_summary or "Not provided — provide orientation coaching."
    struggle_section = request.struggle_description or "None described."
    milestone_section = request.current_milestone or "Not specified."
    milestone_desc = (
        f"\nMilestone Description: {request.milestone_description}"
        if request.milestone_description else ""
    )

    return f"""You are the UniOS Universal Build Coach (AI/ML-2). Your role is to deliver structured, pedagogically sound coaching for a learner working on a {artifact_desc}.

DOMAIN STYLE GUIDE: {domain_guide}
{stage_note}

PROJECT CONTEXT:
- Project Title: {request.project_title}
- Artifact Type: {request.artifact_type.value}
- Academic Domain: {request.academic_domain or "General"}
- Current Milestone: {milestone_section}{milestone_desc}

LEARNER EVIDENCE:
- Concept Mastery:
{mastery_section}
- Weak Topics: {weak_section}
- Active Friction: {friction_section}

CURRENT SUBMISSION SUMMARY:
{work_section}

LEARNER'S STRUGGLE:
{struggle_section}

{rubric_lines}

OUTPUT INSTRUCTIONS:
Generate a structured coaching response strictly as valid JSON matching this schema:
{{
  "coaching_tone": "encouraging" | "instructive" | "challenging",
  "coaching_blocks": [
    {{
      "block_type": "orientation" | "gap_analysis" | "guidance" | "example" | "next_step" | "encouragement",
      "title": "<short heading>",
      "content": "<coaching prose — no HTML, JSX, or raw code unless it is a code snippet inside markdown fences>"
    }}
  ],
  "gap_summary": "<one paragraph: what gaps exist vs rubric criteria>",
  "next_milestone_hint": "<concrete next step hint>",
  "remediation_recommended": true | false
}}

RULES:
1. Generate 4–6 coaching_blocks covering: orientation, gap analysis, specific guidance, worked example relevant to the domain, and next step.
2. Do NOT output raw HTML, React/JSX, or frontend UI code anywhere.
3. Ground all gap_summary to the rubric criteria if provided; otherwise infer from mastery evidence.
4. Set remediation_recommended = true only if concept_mastery shows Weak tier on a prerequisite topic.
5. coaching_tone must reflect mastery: weak = encouraging, developing = instructive, proficient = challenging.
6. Output only the JSON object — no preamble, no trailing text.
"""


# ---------------------------------------------------------------------------
# 2. Recommendation Prompt
# ---------------------------------------------------------------------------

def build_recommend_prompt(context: BuildRecommendContext, count: int = 3) -> str:
    """
    Constructs a token-budgeted prompt for project recommendations.
    Target output: `count` recommendations, ≤ 600 tokens.
    """

    domain_guide = _domain_guide(context.academic_domain)
    stage_note = _stage_note(context.learner_stage)

    mastery_lines = []
    if context.concept_mastery:
        for concept, score in list(context.concept_mastery.items())[:5]:
            tier = "Weak" if score < 0.50 else ("Developing" if score < 0.80 else "Proficient")
            mastery_lines.append(f"- {concept}: {score:.0%} ({tier})")
    mastery_section = "\n".join(mastery_lines) if mastery_lines else "No mastery data available."

    weak_section = (
        ", ".join(context.current_weak_topics[:4]) if context.current_weak_topics else "None."
    )
    completed_section = (
        ", ".join(context.completed_milestones[:4]) if context.completed_milestones else "None."
    )
    role_section = context.target_role or "Not specified."

    preferred_types = ""
    if context.preferred_artifact_types:
        preferred_types = f"Preferred artifact types: {', '.join(t.value for t in context.preferred_artifact_types)}."

    return f"""You are the UniOS Project Recommendation Engine (AI/ML-2). Recommend build projects tailored to this learner.

DOMAIN STYLE GUIDE: {domain_guide}
{stage_note}

LEARNER PROFILE:
- Learner ID: {context.learner_id}
- Academic Domain: {context.academic_domain or "General"}
- Target Role: {role_section}
- Completed Milestones: {completed_section}
- Weak Topics (from Backend mastery): {weak_section}
- Concept Mastery:
{mastery_section}
{preferred_types}

OUTPUT INSTRUCTIONS:
Generate exactly {count} project recommendations strictly as valid JSON:
{{
  "recommendations": [
    {{
      "recommendation_id": "<short_slug_id>",
      "title": "<project title>",
      "artifact_type": "code_project" | "essay" | "research_report" | "business_plan" | "case_analysis" | "data_analysis" | "design_artifact" | "lab_notebook" | "oral_viva" | "portfolio" | "general",
      "difficulty": "foundational" | "intermediate" | "advanced",
      "academic_domain": "<domain>",
      "description": "<2-3 sentence domain-adaptive project description>",
      "rationale": "<why this project suits this learner's mastery and goals>",
      "key_skills_targeted": ["<skill1>", "<skill2>"],
      "estimated_effort_hours": <number or null>,
      "prerequisite_topics": ["<topic1>"]
    }}
  ],
  "recommendation_rationale": "<overall paragraph explaining the selection strategy>"
}}

RULES:
1. Recommendations must be domain-appropriate — do NOT recommend code projects to humanities students unless explicitly requested.
2. At least one recommendation must address a weak topic or skill gap.
3. Vary difficulty: include at least one foundational and one intermediate recommendation unless all mastery is high.
4. Do NOT output raw HTML, JSX, or UI code.
5. Output only the JSON object — no preamble.
"""

from app.schemas.onboarding import OnboardingInputProfile
from app.services.prompt_builder import get_stage_guidelines


def build_onboarding_intelligence_prompt(profile: OnboardingInputProfile) -> str:
    """Builds a token-optimized, strictly grounded prompt instructing the LLM to generate
    multi-dimensional Learner Intelligence matching LearnerIntelligenceReport.
    Target output token budget: ~700-900 tokens.
    """
    if profile.stage:
        stage_text = profile.stage.value
        stage_guide = get_stage_guidelines(profile.stage)
    else:
        stage_text = "[NOT PROVIDED - academic stage is unspecified; do NOT assume bachelor or enrolled university student status]"
        stage_guide = "- Stage Guidelines: General learner (no academic stage specified)."
    target_role = profile.get_effective_target_role()

    # 1. Declared Skills
    if profile.declared_skills:
        skills_text = "\n".join(
            [
                f"  - {s.skill_name} ({s.category.value}): Rating {s.self_rating}/5"
                for s in profile.declared_skills
            ]
        )
    else:
        skills_text = "  - [NONE DECLARED - DO NOT INVENT OR ASSUME ANY DECLARED SKILLS]"

    # 2. Concept Mastery & Assessed Topics from LearnerState
    concept_mastery = profile.get_effective_concept_mastery()
    if concept_mastery:
        mastery_lines = [
            f"  - {concept}: {score:.2f} (mastery scale 0.0 to 1.0)"
            for concept, score in concept_mastery.items()
        ]
        concept_mastery_text = "\n".join(mastery_lines)
    else:
        concept_mastery_text = "  - [NOT PROVIDED - DO NOT INVENT MASTERY SCORES]"

    weak_topics = profile.get_effective_weak_topics()
    weak_topics_text = ", ".join(weak_topics) if weak_topics else "[NOT PROVIDED]"

    strong_topics = profile.get_effective_strong_topics()
    strong_topics_text = ", ".join(strong_topics) if strong_topics else "[NOT PROVIDED]"

    # 3. Domain Interests
    interests_text = (
        ", ".join(profile.interests) if profile.interests else "[NOT PROVIDED]"
    )

    # 4. Learning Preferences (Strict Grounding: No phantom defaults)
    pref_medium = profile.get_effective_learning_preference()
    medium_text = pref_medium if pref_medium else "[NOT PROVIDED - DO NOT ASSUME INTERACTIVE OR VISUAL]"

    pace = profile.get_effective_pace()
    pace_text = pace if pace else "[NOT PROVIDED - DO NOT ASSUME MODERATE OR FAST]"

    weekly_hours = profile.get_effective_weekly_hours()
    hours_text = f"{weekly_hours}h/week" if weekly_hours is not None else "[NOT PROVIDED - DO NOT ASSUME 10h/week OR ANY FIXED HOURS]"

    practical_ratio = profile.get_effective_practical_ratio()
    ratio_text = (
        f"{practical_ratio:.2f} (1.0 = 100% practical)"
        if practical_ratio is not None
        else "[NOT PROVIDED - information unavailable; do NOT assume any ratio or write 'default to balanced', state clearly that this information is unavailable]"
    )

    # 5. Background & Academic Program
    if profile.academic_program:
        academic_text = f"{profile.academic_program} (Semester {profile.current_semester or 'N/A'})"
    else:
        academic_text = "[NOT PROVIDED]"

    projects_text = profile.prior_projects_summary if profile.prior_projects_summary else "[NONE PROVIDED - DO NOT INVENT PRIOR PROJECTS]"
    motivation_text = profile.motivation_statement if profile.motivation_statement else "[NONE PROVIDED]"

    return f"""You are the UniOS Learner Intelligence Engine (AI/ML-2).
Analyze the learner onboarding profile and output a comprehensive, strictly grounded Learner Intelligence Report.

CRITICAL DATA GROUNDING RULES (NON-NEGOTIABLE):
1. STRICT DATA GROUNDING: You must ONLY use the information explicitly provided in the profile below.
2. DO NOT HALLUCINATE OR ASSUME:
   - If study time is [NOT PROVIDED], do NOT assume 10h/week or any number. Set estimated_timeline_months to null.
   - If practical vs theory ratio is [NOT PROVIDED], state clearly that the information is unavailable; do NOT write 'default to balanced foundational exposure' or assume 0.70.
   - If academic stage is [NOT PROVIDED], do NOT claim the learner is an enrolled Bachelor's student.
   - If prior projects are [NONE PROVIDED], do NOT invent past projects or coursework.
   - If declared skills are [NONE DECLARED] and no concept mastery or strong topics are provided, do NOT invent skills or strengths; state clearly that no baseline technical skills were declared.
3. LEARNER STATE INTEGRATION:
   - If weak topics or low concept mastery (<0.50) are provided, they MUST be prioritized in critical_skill_gaps and recommended_foundation_topics.
   - If strong topics or high concept mastery (>=0.70) are provided, they MUST be prioritized in core_strengths.
   - Target role / career goal '{target_role}' MUST be used for career alignment and milestone planning.

LEARNER ONBOARDING PROFILE:
- Learner ID: {profile.learner_id}
- Stage: {stage_text}
{stage_guide}
- Target Role / Career Goal: {target_role}
- Academic Program: {academic_text}
- Declared Skills & Baseline Ratings:
{skills_text}
- Assessed Concept Mastery:
{concept_mastery_text}
- Known Weak Topics / Remediation Areas: {weak_topics_text}
- Known Strong Topics: {strong_topics_text}
- Domain Interests: {interests_text}
- Learning Preferences:
  * Preferred Medium: {medium_text}
  * Pace: {pace_text}
  * Weekly Study Commitment: {hours_text}
  * Practical vs Theory Balance: {ratio_text}
- Prior Projects / Background: {projects_text}
- Motivation Statement: {motivation_text}

EVALUATION OBJECTIVES (6 DIMENSIONS):
1. Skill Baseline & Gap Analysis:
   - Synthesize baseline proficiency (beginner, intermediate, advanced) in a concise narrative strictly grounded in provided data.
   - Extract core verified strengths (from declared skills >= 3, high concept mastery >= 0.7, or strong topics) and 2-4 critical skill gaps for '{target_role}' (incorporating weak topics).
2. Conceptual & Prerequisite Depth Analysis:
   - Evaluate conceptual depth and prerequisite health based strictly on provided mastery or declared stage.
   - Prescribe 2-4 prerequisite foundation topics (prioritizing any weak topics or low mastery concepts).
3. Learning Style & Cognitive Modality:
   - Prescribe dominant & secondary cognitive modality, optimal pacing, feedback cadence, and content formats.
4. Career Role Alignment & Milestone Roadmap:
   - Calculate role alignment score (0.0 to 1.0) and estimate timeline in months (set to null if weekly hours was NOT PROVIDED).
   - Outline 3 sequenced roadmap milestones and high-priority competencies for '{target_role}'.
5. Motivation, Engagement & Frustration Triggers:
   - Identify primary driver, intrinsic/extrinsic orientation, engagement hooks, frustration triggers, and resilience advice.
6. Readiness Scoring & Entry-Level Determination:
   - Calculate overall readiness score (0.0 to 1.0) and readiness tier (high, moderate, needs_scaffolding).
   - Assign recommended entry level (foundational, intermediate, advanced) and 3-4 immediate onboarding recommendations.

OUTPUT JSON SCHEMA:
Output strictly valid JSON matching the following structure. Keep values concise (under 800 tokens total):
{{
  "learner_id": "{profile.learner_id}",
  "stage": "{profile.stage.value if profile.stage else 'bachelor'}",
  "target_role": "{target_role}",
  "executive_summary": "<2-3 sentence synthesized learner overview grounded strictly in provided data>",
  "skill_analysis": {{
    "baseline_summary": "<concise baseline summary>",
    "proficiency_level": "beginner" | "intermediate" | "advanced",
    "core_strengths": ["<strength1>", "<strength2>"],
    "critical_skill_gaps": ["<gap1>", "<gap2>"]
  }},
  "knowledge_analysis": {{
    "conceptual_depth": "foundational" | "applied" | "theoretical",
    "prerequisite_health": "solid" | "minor_gaps" | "needs_remediation",
    "theoretical_vs_applied_balance": "<concise balance assessment>",
    "recommended_foundation_topics": ["<topic1>", "<topic2>"]
  }},
  "learning_style": {{
    "dominant_modality": "<modality>",
    "secondary_modality": "<modality>",
    "recommended_pacing": "accelerated" | "standard" | "scaffolded",
    "feedback_cadence": "<cadence description>",
    "content_format_priorities": ["<format1>", "<format2>"]
  }},
  "career_goals": {{
    "target_role": "{target_role}",
    "role_alignment_score": <float 0.0-1.0>,
    "key_milestones": ["<milestone 1>", "<milestone 2>", "<milestone 3>"],
    "high_priority_competencies": ["<competency 1>", "<competency 2>"],
    "estimated_timeline_months": <integer or null>
  }},
  "motivation": {{
    "primary_driver": "<primary driver>",
    "intrinsic_vs_extrinsic": "mostly_intrinsic" | "balanced" | "mostly_extrinsic",
    "engagement_hooks": ["<hook 1>", "<hook 2>"],
    "potential_frustration_triggers": ["<trigger 1>", "<trigger 2>"],
    "resilience_advice": "<actionable advice>"
  }},
  "readiness": {{
    "overall_readiness_score": <float 0.0-1.0>,
    "readiness_tier": "high" | "moderate" | "needs_scaffolding",
    "recommended_entry_level": "foundational" | "intermediate" | "advanced",
    "onboarding_recommendations": ["<rec 1>", "<rec 2>", "<rec 3>"]
  }}
}}

CRITICAL BOUNDARY RULES:
- Output ONLY valid JSON.
- Under NO circumstances should you output raw HTML, JSX, or React UI code.
- Keep bullet points concise to maintain the safe token budget (700-900 tokens).
"""


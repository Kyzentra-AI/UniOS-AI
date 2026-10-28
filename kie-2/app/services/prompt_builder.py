from app.schemas import NormalizedLearningContext, PedagogyDecision, LearnerStage


def get_stage_guidelines(stage: LearnerStage) -> str:
    """Returns pedagogical guidelines based on the learner's academic stage (Section 17)."""
    if stage == LearnerStage.BACHELOR:
        return (
            "- Learner Stage: Bachelor's Degree\n"
            "- Guidelines: Provide foundational sequencing, step-by-step prerequisite reinforcement, "
            "and clear concept progression."
        )
    elif stage == LearnerStage.MASTER:
        return (
            "- Learner Stage: Master's Degree\n"
            "- Guidelines: Provide specialization depth, architectural trade-offs, and advanced theoretical insight."
        )
    else:  # GRADUATE
        return (
            "- Learner Stage: Recent Graduate\n"
            "- Guidelines: Focus on job/interview readiness, industry application, and practical execution."
        )


def build_pedagogy_prompt(context: NormalizedLearningContext) -> str:
    """Constructs the prompt for selecting the teaching strategy and presentation mode."""
    learner = context.learner_state
    stage_guide = get_stage_guidelines(learner.stage)

    memory_section = ""
    if context.memory_context:
        mem = context.memory_context
        friction_lines = []
        for f in mem.relevant_friction:
            friction_lines.append(
                f"- Active struggle on '{f.topic}' (Severity: {f.severity}, Mistakes: {f.mistake_count}): "
                f"{f.recommended_intervention or 'Targeted reinforcement'}"
            )
        friction_summary = "\n  ".join(friction_lines) if friction_lines else "None active"

        history_lines = []
        for h in mem.relevant_history[:3]:
            score_str = f"{h.assessment_score:.2f}" if h.assessment_score is not None else "N/A"
            history_lines.append(
                f"- {h.topic}: status={h.status}, score={score_str}, mastery={h.mastery_level:.2f}"
            )
        history_summary = "\n  ".join(history_lines) if history_lines else "None recorded"

        memory_section = f"""
RELEVANT LEARNER MEMORY INTELLIGENCE:
- Preferred Modality: {mem.relevant_preferences.dominant_modality} (Secondary: {mem.relevant_preferences.secondary_modality or 'None'})
- Pacing Velocity: {mem.relevant_preferences.pacing}
- Practical vs Theory Ratio: {mem.relevant_preferences.practical_vs_theory_ratio:.2f}
- Active Friction Points:
  {friction_summary}
- Detected Strengths: {', '.join(mem.detected_strengths) if mem.detected_strengths else 'None identified'}
- Detected Weaknesses: {', '.join(mem.detected_weaknesses) if mem.detected_weaknesses else 'None identified'}
- Recommended Mode by Memory: {mem.recommended_pedagogical_mode or 'Standard'}
- Memory Rationale: {mem.rationale}
- Relevant Learning History:
  {history_summary}
"""

    domain_info = context.academic_domain or (learner.academic_domain if learner else None) or (learner.academic_program if learner else "Standard")

    return f"""You are the UniOS Pedagogy Engine. Determine how to teach the following topic to the student.

LEARNER CONTEXT:
{stage_guide}
- Academic Domain / Program: {domain_info}
- Current Confidence: {learner.confidence.value}
- Weak Topics: {', '.join(learner.weak_topics) if learner.weak_topics else 'None reported'}
- Known Concept Mastery: {learner.concept_mastery}
- Career Goal: {learner.career_goal or 'Not specified'}
{memory_section}
TARGET TOPIC & OBJECTIVE:
- Topic: {context.topic}
- Objective: {context.objective}

INSTRUCTIONS:
1. Select the appropriate TeachingStrategy (foundational, reinforcement, advancement, remediation).
   - If Active Friction Points are present on this or related topics, prioritize REMEDIATION with foundational scaffolding.
2. Select DifficultyLevel (beginner, intermediate, advanced) based on mastery.
3. Select PresentationMode (traditional, visual, story, simulation, animation, interactive, analytical, case_study) calibrated to learner modality and domain.
4. Provide a clear pedagogical rationale for your choices.
5. Return strictly structured output adhering to the PedagogyDecision schema.
"""


def build_lesson_prompt(
    context: NormalizedLearningContext, pedagogy: PedagogyDecision
) -> str:
    """Constructs the prompt for generating structured lesson blocks."""
    learner = context.learner_state
    stage_guide = get_stage_guidelines(learner.stage)
    domain_info = context.academic_domain or (learner.academic_domain if learner else None) or (learner.academic_program if learner else "Standard")

    # Honor memory preference if available, else learner state preference
    preferred_mode = learner.learning_preference
    format_priorities_line = ""
    if context.memory_context and context.memory_context.relevant_preferences:
        pref = context.memory_context.relevant_preferences
        preferred_mode = context.memory_context.recommended_pedagogical_mode or pref.dominant_modality or preferred_mode
        if pref.content_format_priorities:
            format_priorities_line = f"- Content Format Priorities: {', '.join(pref.content_format_priorities)}\n"

    grounded_refs = ""
    if context.curriculum_references:
        grounded_refs = f"\nGROUNDED CURRICULUM CONTEXT:\n" + "\n".join(f"- {ref}" for ref in context.curriculum_references)

    return f"""You are the UniOS Lesson Generation Engine. Generate structured lesson blocks for the student.

LEARNER CONTEXT:
{stage_guide}
- Academic Domain / Program: {domain_info}
- Preferred Mode: {preferred_mode}
{format_priorities_line}
SELECTED PEDAGOGICAL STRATEGY:
- Strategy: {pedagogy.strategy.value}
- Difficulty: {pedagogy.difficulty.value}
- Presentation Mode: {pedagogy.presentation_mode.value}
- Explanation Depth: {pedagogy.explanation_depth}
- Pedagogical Sequence: {', '.join(pedagogy.sequence)}
- Practice Level: {pedagogy.practice_level.value}
{grounded_refs}
TOPIC & OBJECTIVE:
- Topic: {context.topic}
- Objective: {context.objective}
- Grounded References: {context.curriculum_references if context.curriculum_references else 'Standard curriculum'}

STRICT GENERATION RULES:
1. Generate an ordered sequence of structured LessonBlocks (objective, explanation, worked_example, visual_spec, practice_task, or domain-adaptive blocks).
2. Under no circumstances should you generate raw HTML, React, JSX, or frontend UI code.
3. For visual_spec blocks, provide structured layout/renderer metadata (e.g. renderer type, step instructions).
4. Ensure the content strictly matches the {pedagogy.difficulty.value} level and domain context.
"""


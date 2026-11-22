from typing import Any
from app.schemas import NormalizedLearningContext, PedagogyDecision, LearnerStage


def _val(x: Any) -> str:
    """Safely extracts value from Enum or returns string representation."""
    if hasattr(x, "value"):
        return str(x.value)
    return str(x) if x is not None else ""


def get_stage_guidelines(stage: LearnerStage) -> str:
    """Returns pedagogical guidelines based on the learner's academic stage (Section 17)."""
    clean_stage = _val(stage).lower()
    if clean_stage == "bachelor":
        return (
            "- Learner Stage: Bachelor's Degree\n"
            "- Guidelines: Provide foundational sequencing, step-by-step prerequisite reinforcement, "
            "and clear concept progression."
        )
    elif clean_stage == "master":
        return (
            "- Learner Stage: Master's Degree\n"
            "- Guidelines: Provide specialization depth, architectural trade-offs, and advanced theoretical insight."
        )
    else:  # GRADUATE
        return (
            "- Learner Stage: Recent Graduate\n"
            "- Guidelines: Focus on job/interview readiness, industry application, and practical execution."
        )


def get_strategy_delivery_guidelines(strategy: Any) -> str:
    """Returns pedagogical delivery instructions according to UniOS Adaptive Learning Architecture (Section 1)."""
    clean_strat = _val(strategy).lower()
    if "foundational" in clean_strat or "remediation" in clean_strat:
        return (
            "- Teaching Strategy: Foundational Support\n"
            "- Method: Use plain language, smaller progressive steps, familiar everyday analogies, and fully worked examples with clear baseline checks."
        )
    elif "visual" in clean_strat:
        return (
            "- Teaching Strategy: Visual Support\n"
            "- Method: Prioritize flowcharts, tree structures, state diagrams, execution graphs, and visual comparisons."
        )
    elif "logical" in clean_strat or "analytical" in clean_strat:
        return (
            "- Teaching Strategy: Logical / Analytical Support\n"
            "- Method: Provide step-by-step reasoning, mathematical recurrence derivations, formal invariant proofs, assumptions, and equations."
        )
    elif "practical" in clean_strat or "applied" in clean_strat:
        return (
            "- Teaching Strategy: Practical / Applied Support\n"
            "- Method: Deliver complete executable code, runtime trace benchmarks, datasets, debugging scenarios, and concrete implementation tasks."
        )
    elif "advanced" in clean_strat or "extension" in clean_strat or "advancement" in clean_strat:
        return (
            "- Teaching Strategy: Advanced / Extension\n"
            "- Method: Deepen theoretical rigor, edge-case optimization, formal asymptotic boundary proofs (constants c, n_0), and unfamiliar challenge problems."
        )
    return "- Teaching Strategy: Standard Balanced Instruction"


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

    return f"""You are the UniOS Pedagogy Engine. Determine how to teach the following topic according to the UniOS Adaptive Learning Content Architecture.

LEARNER CONTEXT:
{stage_guide}
- Academic Domain / Program: {domain_info}
- Current Confidence: {_val(learner.confidence)}
- Weak Topics: {', '.join(learner.weak_topics) if learner.weak_topics else 'None reported'}
- Known Concept Mastery: {learner.concept_mastery}
- Career Goal: {learner.career_goal or 'Not specified'}
{memory_section}
TARGET TOPIC & OBJECTIVE:
- Topic: {context.topic}
- Objective: {context.objective}

INSTRUCTIONS:
1. Select the appropriate TeachingStrategy from UniOS Adaptive Learning Architecture:
   - foundational_support: Plain language, smaller steps, familiar analogies, fully worked examples.
   - visual_support: Flowcharts, diagrams, graphs, animations, visual comparisons.
   - logical_analytical: Step-by-step reasoning, patterns, equations, derivations, assumptions, proofs.
   - practical_applied: Code, experiments, datasets, real-world use cases, debugging, implementation tasks.
   - advanced_extension: Deeper theory, edge cases, optimization, formal analysis, unfamiliar challenge problems.
   - (Or legacy strategies: foundational, reinforcement, advancement, remediation).
   - If Active Friction Points or low confidence are present, prioritize foundational_support / remediation.
2. Select DifficultyLevel (beginner, intermediate, advanced) based on demonstrated mastery.
3. Select PresentationMode (traditional, visual, story, simulation, animation, interactive, analytical, case_study) calibrated to learner modality and domain.
4. Provide a clear pedagogical rationale for your choices.
5. Return strictly structured output adhering to the PedagogyDecision schema.
"""


def build_lesson_prompt(
    context: NormalizedLearningContext, pedagogy: PedagogyDecision
) -> str:
    """Constructs the prompt for generating structured lesson blocks with maximum pedagogical depth."""
    learner = context.learner_state
    stage_guide = get_stage_guidelines(learner.stage)
    domain_info = context.academic_domain or (learner.academic_domain if learner else None) or (learner.academic_program if learner else "Standard")

    # Honor memory preference if available, else learner state preference
    preferred_mode = _val(learner.learning_preference)
    format_priorities_line = ""
    if context.memory_context and context.memory_context.relevant_preferences:
        pref = context.memory_context.relevant_preferences
        preferred_mode = _val(context.memory_context.recommended_pedagogical_mode or pref.dominant_modality or preferred_mode)
        if pref.content_format_priorities:
            format_priorities_line = f"- Content Format Priorities: {', '.join(pref.content_format_priorities)}\n"

    grounded_refs = ""
    if context.curriculum_references:
        grounded_refs = f"\nGROUNDED CURRICULUM CONTEXT:\n" + "\n".join(f"- {ref}" for ref in context.curriculum_references)

    strategy_instructions = get_strategy_delivery_guidelines(pedagogy.strategy)

    return f"""You are the senior pedagogical architect for UniOS. Generate a comprehensive, university-level, masterclass lesson for the student.

LEARNER CONTEXT:
{stage_guide}
- Academic Domain / Program: {domain_info}
- Preferred Mode: {preferred_mode}
{format_priorities_line}
SELECTED PEDAGOGICAL STRATEGY:
- Strategy: {_val(pedagogy.strategy)}
{strategy_instructions}
- Difficulty: {_val(pedagogy.difficulty)}
- Presentation Mode: {_val(pedagogy.presentation_mode)}
- Explanation Depth: {pedagogy.explanation_depth}
- Pedagogical Sequence: {', '.join(pedagogy.sequence)}
- Practice Level: {_val(pedagogy.practice_level)}
{grounded_refs}
TOPIC & OBJECTIVE:
- Topic: {context.topic}
- Objective: {context.objective}
- Grounded References: {context.curriculum_references if context.curriculum_references else 'Standard curriculum'}

CONTENT MAXIMIZATION & 10-STAGE ADAPTIVE STRUCTURE REQUIREMENTS:
1. MAXIMIZE PEDAGOGICAL DEPTH:
   - Absolutely DO NOT produce brief 1-2 sentence summaries. Provide rigorous, extensive, deeply educational content for each section.
2. RICH MARKDOWN FORMATTING:
   - Use markdown subheadings ('### Heading') to clearly segment core concepts.
   - Use bold ('**Key Concept**') to emphasize technical terminology, definitions, and invariants.
   - Use bullet points ('- Point') and numbered lists ('1. Step') for procedural logic and takeaways.
   - Use inline code spans ('`code`') for keywords, syntax, commands, and function calls.
3. LEARNING OBJECTIVE & PREREQUISITE CHECK:
   - In the objective block, explicitly define the observable outcome and include a short prerequisite check identifying missing foundational knowledge.
4. PERSONALIZED INTRODUCTION & CORE CONCEPT:
   - Open with an explanation selected for the student's current needs according to the selected Teaching Strategy.
   - Deliver an accurate, syllabus-aligned conceptual deep-dive detailing foundational theory, core mechanics, and constraints.
5. WORKED EXAMPLE & ALTERNATIVE REPRESENTATION:
   - Provide a complete, production-quality implementation walkthrough (e.g. Python, SQL, Java) with step-by-step commentary and input/output traces.
   - Deliver an alternative visual representation (ASCII architecture/flowchart diagram, state-space tree, execution graph, or formal mathematical derivation).
6. GUIDED PRACTICE CHALLENGE:
   - Provide a structured hands-on challenge with Scenario, Requirements Checklist, Starter Template, and scaffolded Hints.
7. COMPREHENSION CHECK & MASTERY EVALUATION:
   - Provide an insightful scenario-based question assessing concept transfer and application, with 4 options ('A) ...', 'B) ...', 'C) ...', 'D) ...'), correct answer, and detailed explanation.
8. Under no circumstances output raw HTML, JSX, or React UI tags. Output clean text and markdown.
"""


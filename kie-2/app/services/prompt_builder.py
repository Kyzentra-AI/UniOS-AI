from typing import Any
from app.schemas import NormalizedLearningContext, PedagogyDecision, LearnerStage
from app.services.domain_classifier import classify_domain, DomainArchetype


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
    """Constructs the prompt for generating a 5-section domain-adaptive lesson blueprint (1,200-1,800 words)."""
    learner = context.learner_state
    stage_guide = get_stage_guidelines(learner.stage)
    domain_info = context.academic_domain or (learner.academic_domain if learner else None) or (learner.academic_program if learner else "Standard")

    archetype = classify_domain(
        subject=context.topic,
        degree_program=learner.academic_program if learner else None,
        topic=context.topic,
        academic_domain=context.academic_domain,
    )

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

    is_coding = archetype == DomainArchetype.CODING_CS

    domain_specific_walkthrough_rule = ""
    if archetype == DomainArchetype.BUSINESS_MANAGEMENT:
        domain_specific_walkthrough_rule = (
            "FOR BUSINESS_MANAGEMENT: Provide a concrete corporate case study (e.g. how Tata, Zomato, or Swiggy applies "
            "Planning, Organizing, Directing, and Controlling) with strategic decisions and operational takeaways. "
            "DO NOT write Python code or technical software classes."
        )
    elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT:
        domain_specific_walkthrough_rule = (
            "FOR ACCOUNTING_FINANCE_QUANT: Provide step-by-step worked numerical problems (e.g., journal entries in debit/credit tables, "
            "trial balance, or elasticity calculations with LaTeX formulas). DO NOT write Python code or software scripts."
        )
    elif archetype == DomainArchetype.APPLIED_OFFICE_IT:
        domain_specific_walkthrough_rule = (
            "FOR APPLIED_OFFICE_IT: Provide practical workflow walkthroughs (e.g., spreadsheet formulas such as XLOOKUP/VLOOKUP, "
            "SUMIFS, PivotTables, data validation, or executive document structuring). DO NOT write OOP Python classes."
        )
    elif archetype == DomainArchetype.GENERAL_HUMANITIES_SCIENCE:
        domain_specific_walkthrough_rule = (
            "FOR GENERAL_HUMANITIES_SCIENCE: Provide critical textual analysis, scientific empirical methodology, or "
            "historical/ethical framework analysis. DO NOT write software engineering code."
        )
    else:
        domain_specific_walkthrough_rule = (
            "FOR CODING_CS: Provide a runnable, verified code walkthrough with step-by-step commentary and input/output traces."
        )

    code_rule = (
        "STRICT ARCHETYPE RULE: Code blocks (type: 'code'), schema design, and system architecture diagrams are FORBIDDEN "
        "unless the archetype is CODING_CS."
        if not is_coding
        else "Permitted to include clean executable code blocks for algorithmic walkthrough."
    )

    return f"""You are the senior pedagogical architect for UniOS. Generate a comprehensive, textbook-grade, 5-section masterclass lesson (Target 1,200 to 1,800 words).

LEARNER CONTEXT:
{stage_guide}
- Domain Archetype: {archetype.value}
- Academic Domain / Program: {domain_info}
- Preferred Mode: {preferred_mode}
{format_priorities_line}
SELECTED PEDAGOGICAL STRATEGY:
- Strategy: {_val(pedagogy.strategy)}
{strategy_instructions}
- Difficulty: {_val(pedagogy.difficulty)}
- Presentation Mode: {_val(pedagogy.presentation_mode)}
- Explanation Depth: {pedagogy.explanation_depth}
{grounded_refs}
TOPIC & OBJECTIVE:
- Topic: {context.topic}
- Objective: {context.objective}

5-SECTION LESSON BLUEPRINT (Strict Sequence):
1. Section 1 — Learning Outcomes & Context (type: 'objective'):
   - Clear bulleted objectives, why this topic matters in the real world, and prerequisite concepts.
   - Absolutely NO robotic 'establish a rigorous theoretical mastery over its core invariants' phrasing.
2. Section 2 — Deep Concept Breakdown (type: 'explanation'):
   - Full, textbook-grade explanation broken into digestible sub-concepts.
   - Key definitions in callout blocks (> [!NOTE]) and clear comparisons (e.g., Top vs Middle vs First-Line Management, Taylor vs Fayol).
3. Section 3 — Real-World Applied Walkthrough (type: 'worked_example'):
   - {domain_specific_walkthrough_rule}
4. Section 4 — Visual Framework & Mental Model (type: 'visual_spec'):
   - Output a valid fenced ```mermaid diagram (flowchart, hierarchy, mindmap, or cycle) or a structured GFM Markdown comparison table tailored to the topic.
   - NEVER output a raw ASCII box, drawing instructions, or CS topology map.
5. Section 5 — Applied Scenario & Exam Takeaways (type: 'practice_task'):
   - A domain-appropriate mini-scenario/reflection prompt + concise exam-ready summary points and common mistakes.

CRITICAL CONSTRAINTS:
- {code_rule}
- REMOVE SECTION 6: Do NOT generate an inline Comprehension Check MCQ or quiz block. Assessment belongs exclusively to the assessment service.
- MARKDOWN HYGIENE: Ban #### headers (use ## and ### only) and NEVER emit triple single quotes ('''python). Always use standard triple backticks (```).
- Under NO circumstances output raw HTML, JSX, or React UI tags.
"""


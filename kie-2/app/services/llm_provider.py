import json
from typing import Dict as _Dict
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.core.config import settings
from app.schemas import (
    PedagogyDecision,
    TeachingStrategy,
    DifficultyLevel,
    PresentationMode,
    PracticeLevel,
    GeneratedLesson,
    LessonBlock,
    LessonBlockType,
    LearnerStage,

    OnboardingInputProfile,
    LearnerIntelligenceReport,
    SkillAnalysis,
    KnowledgeAnalysis,
    LearningStyleProfile,
    CareerGoalProfile,
    MotivationProfile,
    ReadinessAssessment,
    ReadinessTier,
)
from app.services.domain_classifier import classify_domain, DomainArchetype


class LLMProviderError(Exception):
    """Application-level controlled error for LLM provider connectivity or rate-limit issues."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LLMParseError(LLMProviderError):
    """Application-level controlled error when LLM output cannot be safely parsed or validated."""

    def __init__(self, message: str, raw_content: Optional[str] = None, status_code: int = 502):
        super().__init__(message, status_code=status_code)
        self.raw_content = raw_content


def extract_json_payload(raw_text: str) -> str:
    """Defensively extracts JSON substring from LLM response text, stripping markdown blocks or conversational text."""
    if not raw_text or not isinstance(raw_text, str):
        raise LLMParseError("LLM returned empty or non-string response.")

    text = raw_text.strip()

    # 1. If text is already valid JSON, return directly (prevents stripping inner code blocks)
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # 2. Strip outer markdown code blocks like ```json ... ``` or ``` ... ```
    outer_match = re.search(r"^\s*```(?:json)?\s*([\s\S]*?)\s*```\s*$", text, re.IGNORECASE)
    if outer_match:
        unfenced = outer_match.group(1).strip()
        try:
            json.loads(unfenced)
            return unfenced
        except Exception:
            text = unfenced

    # 3. Locate outermost JSON object braces or array brackets
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    first_bracket = text.find("[")
    last_bracket = text.rfind("]")

    start_idx = -1
    end_idx = -1

    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        if last_brace != -1 and last_brace > first_brace:
            start_idx = first_brace
            end_idx = last_brace + 1
    elif first_bracket != -1:
        if last_bracket != -1 and last_bracket > first_bracket:
            start_idx = first_bracket
            end_idx = last_bracket + 1

    if start_idx != -1 and end_idx != -1:
        candidate = text[start_idx:end_idx].strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            text = candidate

    return text



def normalize_intelligence_dict(data: Dict[str, Any], profile: OnboardingInputProfile) -> Dict[str, Any]:
    """Defensively repairs and normalizes key names, aliases, and missing optional structures in LLM output
    WITHOUT silently fabricating critical learner ground truth.
    """
    if not isinstance(data, dict):
        raise LLMParseError("Normalized LLM output must be a dictionary object.")

    target_role = profile.get_effective_target_role()

    # 1. Enforce ground-truth learner metadata
    data["learner_id"] = profile.learner_id
    data["stage"] = profile.stage.value if profile.stage else profile.get_effective_stage().value
    data["target_role"] = target_role

    # 2. Normalize top-level section key aliases (camelCase / synonyms)
    key_mapping = {
        "skillAnalysis": "skill_analysis",
        "skills": "skill_analysis",
        "skill_baseline": "skill_analysis",
        "knowledgeAnalysis": "knowledge_analysis",
        "knowledge": "knowledge_analysis",
        "conceptual_analysis": "knowledge_analysis",
        "learningStyle": "learning_style",
        "learning_style_profile": "learning_style",
        "style": "learning_style",
        "careerGoals": "career_goals",
        "career_goals_profile": "career_goals",
        "career": "career_goals",
        "motivationProfile": "motivation",
        "motivation_profile": "motivation",
        "readinessAssessment": "readiness",
        "readiness_assessment": "readiness",
        "executiveSummary": "executive_summary",
        "summary": "executive_summary",
    }
    for old_k, new_k in key_mapping.items():
        if old_k in data and new_k not in data:
            data[new_k] = data.pop(old_k)

    # 3. Defensive defaults for missing sections
    if not isinstance(data.get("skill_analysis"), dict):
        data["skill_analysis"] = {}
    if not isinstance(data.get("knowledge_analysis"), dict):
        data["knowledge_analysis"] = {}
    if not isinstance(data.get("learning_style"), dict):
        data["learning_style"] = {}
    if not isinstance(data.get("career_goals"), dict):
        data["career_goals"] = {}
    if not isinstance(data.get("motivation"), dict):
        data["motivation"] = {}
    if not isinstance(data.get("readiness"), dict):
        data["readiness"] = {}

    # 4. Normalize nested aliases in skill_analysis
    sa = data["skill_analysis"]
    if "strengths" in sa and "core_strengths" not in sa:
        sa["core_strengths"] = sa.pop("strengths")
    if "gaps" in sa and "critical_skill_gaps" not in sa:
        sa["critical_skill_gaps"] = sa.pop("gaps")
    if "proficiency" in sa and "proficiency_level" not in sa:
        sa["proficiency_level"] = sa.pop("proficiency")
    if "summary" in sa and "baseline_summary" not in sa:
        sa["baseline_summary"] = sa.pop("summary")

    # 5. Normalize nested aliases in knowledge_analysis
    ka = data["knowledge_analysis"]
    if "topics" in ka and "recommended_foundation_topics" not in ka:
        ka["recommended_foundation_topics"] = ka.pop("topics")
    if "foundation_topics" in ka and "recommended_foundation_topics" not in ka:
        ka["recommended_foundation_topics"] = ka.pop("foundation_topics")

    # 6. Normalize nested aliases in career_goals
    cg = data["career_goals"]
    cg["target_role"] = target_role
    if "milestones" in cg and "key_milestones" not in cg:
        cg["key_milestones"] = cg.pop("milestones")
    if "competencies" in cg and "high_priority_competencies" not in cg:
        cg["high_priority_competencies"] = cg.pop("competencies")
    if "alignment_score" in cg and "role_alignment_score" not in cg:
        cg["role_alignment_score"] = cg.pop("alignment_score")
    if "timeline" in cg and "estimated_timeline_months" not in cg:
        cg["estimated_timeline_months"] = cg.pop("timeline")

    # 7. Normalize nested aliases in motivation
    mo = data["motivation"]
    if "driver" in mo and "primary_driver" not in mo:
        mo["primary_driver"] = mo.pop("driver")
    if "hooks" in mo and "engagement_hooks" not in mo:
        mo["engagement_hooks"] = mo.pop("hooks")
    if "triggers" in mo and "potential_frustration_triggers" not in mo:
        mo["potential_frustration_triggers"] = mo.pop("triggers")
    if "advice" in mo and "resilience_advice" not in mo:
        mo["resilience_advice"] = mo.pop("advice")

    # 8. Normalize nested aliases in readiness
    rd = data["readiness"]
    if "score" in rd and "overall_readiness_score" not in rd:
        rd["overall_readiness_score"] = rd.pop("score")
    if "tier" in rd and "readiness_tier" not in rd:
        rd["readiness_tier"] = rd.pop("tier")
    if "entry_level" in rd and "recommended_entry_level" not in rd:
        rd["recommended_entry_level"] = rd.pop("entry_level")
    if "recommendations" in rd and "onboarding_recommendations" not in rd:
        rd["onboarding_recommendations"] = rd.pop("recommendations")

    # === STRICT GROUNDING SANITIZATION ===
    weekly_hours = profile.get_effective_weekly_hours()
    if weekly_hours is None:
        cg["estimated_timeline_months"] = None
        # Sanitize any hallucinated study hours from core_strengths
        if isinstance(sa.get("core_strengths"), list):
            sa["core_strengths"] = [
                item for item in sa["core_strengths"]
                if not re.search(r'\b(?:10h/week|\d+h/week|\d+\s*hours?/week)\b', str(item), re.I)
            ]

    practical_ratio = profile.get_effective_practical_ratio()
    if practical_ratio is None:
        if "theoretical_vs_applied_balance" in ka and isinstance(ka["theoretical_vs_applied_balance"], str):
            bal = ka["theoretical_vs_applied_balance"]
            if re.search(r'\(?0\.70?\)?|\b70%\b|default\s+to|balanced\s+foundational', bal, re.I):
                ka["theoretical_vs_applied_balance"] = "Information unavailable: no practical vs theoretical preference was provided by the learner."

    # Remove hallucinated "10h/week", "0.70", or assumed bachelor enrollment from executive_summary if not provided
    if isinstance(data.get("executive_summary"), str):
        summary = data["executive_summary"]
        if weekly_hours is None:
            summary = re.sub(r'\(?\b10h/week\b\)?', '', summary)
            summary = re.sub(r'with\s+10\s*hours?/week\s+commitment', '', summary, flags=re.I)
        if practical_ratio is None:
            summary = re.sub(r'\(?0\.70?\)?', '', summary)
        if profile.stage is None:
            summary = re.sub(r'\b(?:is a Bachelor\'s degree student|is a Bachelor student|is a bachelor\'s student|is a bachelor student)\b', 'is targeting', summary, flags=re.I)
        data["executive_summary"] = " ".join(summary.split())

    # Forward weak_topics and concept_mastery into skill gaps / foundation topics
    weak_topics = profile.get_effective_weak_topics()
    if weak_topics:
        if not isinstance(sa.get("critical_skill_gaps"), list):
            sa["critical_skill_gaps"] = []
        for wt in weak_topics:
            if not any(wt.lower() in str(g).lower() for g in sa["critical_skill_gaps"]):
                sa["critical_skill_gaps"].insert(0, wt)

        if not isinstance(ka.get("recommended_foundation_topics"), list):
            ka["recommended_foundation_topics"] = []
        for wt in weak_topics:
            if not any(wt.lower() in str(t).lower() for t in ka["recommended_foundation_topics"]):
                ka["recommended_foundation_topics"].insert(0, wt)

    strong_topics = profile.get_effective_strong_topics()
    if strong_topics:
        if not isinstance(sa.get("core_strengths"), list):
            sa["core_strengths"] = []
        for st in strong_topics:
            if not any(st.lower() in str(s).lower() for s in sa["core_strengths"]):
                sa["core_strengths"].insert(0, st)

    concept_mastery = profile.get_effective_concept_mastery()
    if concept_mastery:
        if not isinstance(sa.get("core_strengths"), list):
            sa["core_strengths"] = []
        if not isinstance(sa.get("critical_skill_gaps"), list):
            sa["critical_skill_gaps"] = []
        for concept, score in concept_mastery.items():
            if score >= 0.70:
                if not any(concept.lower() in str(s).lower() for s in sa["core_strengths"]):
                    sa["core_strengths"].append(f"{concept} (Mastery: {score:.0%})")
            elif score < 0.50:
                if not any(concept.lower() in str(g).lower() for g in sa["critical_skill_gaps"]):
                    sa["critical_skill_gaps"].insert(0, f"{concept} (Remediation)")

    if not sa.get("core_strengths"):
        sa["core_strengths"] = ["No verified technical skills declared during onboarding"]

    # Executive summary fallback if omitted
    if not data.get("executive_summary"):
        data["executive_summary"] = (
            f"Onboarding analysis for {profile.learner_id} targeting '{target_role}' "
            f"in stage {profile.stage.value}."
        )

    return data


class BaseLLMProvider(ABC):
    """Abstract base provider for generating structured pedagogical and learner intelligence."""

    @abstractmethod
    def generate_pedagogy_decision(self, prompt: str) -> PedagogyDecision:
        """Generate a structured pedagogy decision from a prompt."""
        pass

    @abstractmethod
    def generate_lesson(
        self,
        prompt: str,
        context_id: str,
        topic: str,
        pedagogy_decision: Optional[PedagogyDecision] = None,
        academic_domain: Optional[str] = None,
        degree_program: Optional[str] = None,
    ) -> GeneratedLesson:
        """Generate structured lesson blocks from a prompt."""
        pass

    @abstractmethod
    def analyze_learner_onboarding(
        self, profile: OnboardingInputProfile, prompt: str
    ) -> LearnerIntelligenceReport:
        """Generate structured multi-dimensional Learner Intelligence from an onboarding profile."""
        pass

    @abstractmethod
    def generate_build_coaching(self, prompt: str) -> _Dict[str, Any]:
        """Generate structured build coaching response from a prompt.

        Returns a raw dict that the build_coach_service validates against
        BuildCoachResponse before returning to the caller.
        """
        pass

    @abstractmethod
    def generate_career_response(self, prompt: str) -> _Dict[str, Any]:
        """Generate structured career response (resume draft or ATS analysis) from a prompt.

        Returns a raw dict that the career_service validates against
        ResumeDraft or ATSAnalyzeResponse before returning to the caller.
        """
        pass

    @abstractmethod
    def generate_assessment(self, prompt: str) -> _Dict[str, Any]:
        """Generate structured assessment JSON with answer keys/rubrics from a prompt."""
        pass

    @abstractmethod
    def evaluate_mastery_attempt(self, prompt: str) -> _Dict[str, Any]:
        """Evaluate submitted assessment attempt, returning normalized score and mastery updates."""
        pass

    @abstractmethod
    def generate_mentor_reply(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate persona-aligned educational response string for mentor chat."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Deterministic, contract-compliant provider for testing and zero-cost local development.
    Requires NO API keys and runs completely offline.
    """

    def generate_pedagogy_decision(self, prompt: str) -> PedagogyDecision:
        # Detect active struggle or friction points in prompt
        is_remediation = (
            "Active struggle on" in prompt
            or "Severity: high" in prompt
            or "Severity: moderate" in prompt
            or "prioritize REMEDIATION" in prompt and ("struggle" in prompt.lower() or "friction" in prompt.lower())
        )
        prompt_lower = prompt.lower()

        # Check for advancement
        is_advancement = (
            "advancement" in prompt_lower
            or "confidence: high" in prompt_lower and ("0.8" in prompt or "0.9" in prompt)
        )

        mode = PresentationMode.VISUAL
        if "recommended mode by memory: interactive" in prompt_lower or "preferred modality: interactive" in prompt_lower or "interactive" in prompt_lower:
            mode = PresentationMode.INTERACTIVE
        elif "recommended mode by memory: story" in prompt_lower or "preferred modality: story" in prompt_lower:
            mode = PresentationMode.STORY
        elif "recommended mode by memory: simulation" in prompt_lower or "preferred modality: simulation" in prompt_lower or "simulation" in prompt_lower:
            mode = PresentationMode.SIMULATION
        elif any(term in prompt_lower for term in ["commerce", "b.com", "mba", "finance", "accounting"]):
            mode = PresentationMode.CASE_STUDY
        elif any(term in prompt_lower for term in ["law", "legal", "humanities", "arts", "psychology"]):
            mode = PresentationMode.ANALYTICAL

        if is_remediation:
            return PedagogyDecision(
                strategy=TeachingStrategy.REMEDIATION,
                difficulty=DifficultyLevel.BEGINNER,
                presentation_mode=mode,
                explanation_depth="step-by-step",
                rationale="Active friction detected in learner memory context. Prioritizing targeted remediation with worked examples and scaffolding.",
                sequence=[
                    "prerequisite_review",
                    "simplified_concept_breakdown",
                    "scaffolded_worked_example",
                    "guided_remedial_practice",
                    "formative_reassessment",
                ],
                practice_level=PracticeLevel.REMEDIAL,
                remediation=True,
                recommended_level="beginner",
            )
        elif is_advancement:
            return PedagogyDecision(
                strategy=TeachingStrategy.ADVANCEMENT,
                difficulty=DifficultyLevel.ADVANCED,
                presentation_mode=mode,
                explanation_depth="deep-dive",
                rationale="Advancement strategy: High verified mastery and confidence. Prioritizing architectural trade-offs and complex application.",
                sequence=[
                    "concept_synthesis",
                    "advanced_domain_tradeoffs",
                    "complex_edge_cases",
                    "challenge_based_practice",
                    "summative_assessment",
                ],
                practice_level=PracticeLevel.CHALLENGE_BASED,
                remediation=False,
                recommended_level="advanced",
            )

        return PedagogyDecision(
            strategy=TeachingStrategy.FOUNDATIONAL,
            difficulty=DifficultyLevel.BEGINNER,
            presentation_mode=mode,
            explanation_depth="step-by-step",
            rationale="Deterministic mock: Learner requires foundational scaffolding with visual demonstrations.",
            sequence=[
                "prerequisite_check",
                "core_concept_introduction",
                "worked_example",
                "guided_practice",
                "formative_assessment",
            ],
            practice_level=PracticeLevel.GUIDED,
            remediation=False,
            recommended_level="beginner",
        )

    def generate_lesson(
        self,
        prompt: str,
        context_id: str,
        topic: str,
        pedagogy_decision: Optional[PedagogyDecision] = None,
        academic_domain: Optional[str] = None,
        degree_program: Optional[str] = None,
    ) -> GeneratedLesson:
        """Deterministic 5-section offline domain-adaptive lesson generator (100% reliable, zero network)."""
        if pedagogy_decision is None:
            pedagogy_decision = self.generate_pedagogy_decision(prompt)

        # Do NOT pass prompt as academic_domain; prompt contains formatting keywords that corrupt domain classification
        archetype = classify_domain(
            subject=topic,
            degree_program=degree_program,
            topic=topic,
            academic_domain=academic_domain,
        )

        topic_clean = (topic or "Foundational Concepts").strip()
        topic_lower = topic_clean.lower()

        # Strict Cross-Domain Safety Gate: Never permit CODING_CS for biological, medical, natural science, or humanities topics
        _NON_CS_INDICATORS = [
            "life", "zoolog", "botan", "biolog", "medic", "health", "anatom", "physiolog",
            "patholog", "pharmac", "pediatric", "surg", "cell", "organ", "species", "specimen",
            "animal", "plant", "kinematic", "chemistr", "physic", "history", "philosophy",
            "sociolog", "literature", "jurisprudence", "law", "governance"
        ]
        if archetype == DomainArchetype.CODING_CS and any(k in topic_lower for k in _NON_CS_INDICATORS):
            archetype = DomainArchetype.GENERAL_HUMANITIES_SCIENCE
        from app.schemas.lesson import AssessmentIntent, NextLearningAction

        # Domain-specific block assembly
        if archetype == DomainArchetype.CODING_CS:
            from app.services.daa_curriculum_service import get_daa_lesson
            daa_lesson = get_daa_lesson(topic_clean, context_id)
            if daa_lesson:
                if pedagogy_decision:
                    daa_lesson.pedagogy_decision = pedagogy_decision
                return daa_lesson

            if any(w in topic_lower for w in ["neural network", "neural networks", "artificial neural network", "artificial neural networks", "deep learning", "perceptron", "ann"]):
                from app.services.neural_networks_curriculum import build_neural_networks_lesson
                nn_lesson = build_neural_networks_lesson(topic_clean, context_id)
                if pedagogy_decision:
                    nn_lesson.pedagogy_decision = pedagogy_decision
                return nn_lesson

            is_algo = any(w in topic_lower for w in ["algorithm", "daa", "complexity", "asymptotic", "sorting", "divide", "greedy", "dynamic programming", "graph", "tree", "recurrence", "big-o"])
            is_automata = any(w in topic_lower for w in ["theory of computation", "automata", "formal language", "chomsky", "turing", "dfa", "nfa", "grammar", "pda", "decidab"])
            is_ai = any(w in topic_lower for w in ["artificial intelligence", "ai", "machine learning", "neural", "heuristic", "agent", "state-space"])

            if is_algo:
                obj_title = f"Learning Outcomes & Computational Complexity: {topic_clean}"
                obj_content = (
                    f"## 🎯 Learning Outcomes & Competencies\n"
                    f"- Formulate and evaluate time and space asymptotic complexity ($O, \\Omega, \\Theta$) for algorithmic procedures.\n"
                    f"- Master divide-and-conquer recurrence relations using the Master Theorem ($T(n) = aT(n/b) + f(n)$).\n"
                    f"- Verify algorithmic state invariants and formal termination boundaries.\n\n"
                    f"### 📚 Prerequisites & Readiness\n"
                    f"- Basic procedural control flow, pointer manipulation, and recursive call frames.\n"
                    f"- Mathematical intuition for logarithms ($O(\\log n)$) and geometric series.\n\n"
                    f"### 💡 Why This Topic Matters\n"
                    f"In production engineering, selecting an $O(n \\log n)$ algorithm over an $O(n^2)$ approach reduces computation time on a million records from days to seconds."
                )
                expl_title = f"Algorithmic Mechanics & Asymptotic Analysis: {topic_clean}"
                expl_content = (
                    f"## 🔬 Foundational Theory & Recurrence Relations\n"
                    f"Algorithmic analysis quantifies resource consumption as input size $n$ scales toward infinity.\n\n"
                    f"> [!NOTE]\n"
                    f"> **The Divide-and-Conquer Paradigm**: Breaks a problem of size $n$ into $a$ subproblems of size $n/b$, solves them recursively, and combines solutions in $O(n^d)$ time.\n\n"
                    f"### Asymptotic Growth Comparison Table\n\n"
                    f"| Complexity Class | Formal Bound | Operations ($N = 10^4$) | Practical Feasibility |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"| Constant | $O(1)$ | 1 | Instantaneous |\n"
                    f"| Logarithmic | $O(\\log n)$ | ~14 | Instantaneous |\n"
                    f"| Linear | $O(n)$ | $10^4$ | Real-time |\n"
                    f"| Linearithmic | $O(n \\log n)$ | ~1.4 \\times 10^5 | Optimal for Comparison Sort |\n"
                    f"| Quadratic | $O(n^2)$ | $10^8$ | Unscalable for Large Data |\n\n"
                    f"### Core Invariants & Correctness Guarantees\n"
                    f"- **Loop Invariant**: In partition and merge steps, sub-arrays maintain strictly sorted order.\n"
                    f"- **Termination**: Every recursive step strictly decreases problem size ($n/2 < n$), guaranteeing base-case termination."
                )
                code_title = f"Verified Implementation: Divide-and-Conquer Merge Sort"
                code_lang = "python"
                code_snippet = (
                    "def merge_sort(arr: list) -> list:\n"
                    '    """Sorts an array using divide-and-conquer with O(n log n) runtime."""\n'
                    "    if len(arr) <= 1:\n"
                    "        return arr\n\n"
                    "    mid = len(arr) // 2\n"
                    "    left_sorted = merge_sort(arr[:mid])\n"
                    "    right_sorted = merge_sort(arr[mid:])\n\n"
                    "    # Linear two-pointer merge operation O(n)\n"
                    "    merged = []\n"
                    "    i = j = 0\n"
                    "    while i < len(left_sorted) and j < len(right_sorted):\n"
                    "        if left_sorted[i] <= right_sorted[j]:\n"
                    "            merged.append(left_sorted[i])\n"
                    "            i += 1\n"
                    "        else:\n"
                    "            merged.append(right_sorted[j])\n"
                    "            j += 1\n"
                    "    merged.extend(left_sorted[i:])\n"
                    "    merged.extend(right_sorted[j:])\n"
                    "    return merged\n\n"
                    "# Verification assertions\n"
                    "assert merge_sort([38, 27, 43, 3, 9, 82, 10]) == [3, 9, 10, 27, 38, 43, 82]\n"
                    "assert merge_sort([]) == []\n"
                    "assert merge_sort([42]) == [42]"
                )
                code_content = (
                    f"## 🛠️ Step-by-Step Implementation Walkthrough\n"
                    f"The implementation below demonstrates the canonical divide-and-conquer sort with verified correctness assertions:\n\n"
                    f"```{code_lang}\n{code_snippet}\n```\n\n"
                    f"### 🔍 Key Implementation Invariants\n"
                    f"- **Midpoint Calculation**: Integer division `len(arr) // 2` isolates divide step in $O(1)$.\n"
                    f"- **Stability**: `left_sorted[i] <= right_sorted[j]` preserves relative order of equal keys."
                )
                vis_title = f"Recursive Divide-and-Conquer Flowchart & Call Hierarchy"
                vis_content = (
                    f"## 📊 Recursive Call Hierarchy & Merging Flow\n\n"
                    f"```mermaid\n"
                    f"flowchart TD\n"
                    f'    A["Array [38, 27, 43, 3, 9, 82, 10] (n)"] --> B["Left: [38, 27, 43, 3] (n/2)"]\n'
                    f'    A --> C["Right: [9, 82, 10] (n/2)"]\n'
                    f'    B --> D["Left-Left: [38, 27]"]\n'
                    f'    B --> E["Left-Right: [43, 3]"]\n'
                    f'    C --> F["Right-Left: [9]"]\n'
                    f'    C --> G["Right-Right: [82, 10]"]\n'
                    f'    D & E --> H["Merged Left: [3, 27, 38, 43] O(n/2)"]\n'
                    f'    F & G --> I["Merged Right: [9, 10, 82] O(n/2)"]\n'
                    f'    H & I --> J["Final Sorted Array: [3, 9, 10, 27, 38, 43, 82] O(n)"]\n'
                    f"```\n\n"
                    f"### 🔄 Tree Depth & Work Per Level\n"
                    f"- **Tree Height**: Exactly $\\log_2 n$ levels of division.\n"
                    f"- **Work Per Level**: Merging takes $c \\cdot n$ operations across all nodes at each level.\n"
                    f"- **Total Time Complexity**: $\\log_2 n \\times c \\cdot n = O(n \\log n)$."
                )
                task_title = f"Applied Engineering Challenge & Exam Review: {topic_clean}"
                task_content = (
                    f"## 🎯 Applied Hands-On Challenge\n"
                    f"**Problem**: Implement an in-place inversion counter that computes how many pairs $(i, j)$ satisfy $i < j$ and $arr[i] > arr[j]$ in $O(n \\log n)$ time.\n\n"
                    f"### 📋 Input Constraints & Edge Cases\n"
                    f"- Constraints: $1 \\le N \\le 10^5$, elements are integers (can be negative).\n"
                    f"- Edge Cases: Already sorted array (0 inversions), strictly decreasing array ($n(n-1)/2$ inversions).\n\n"
                    f"### 💡 High-Yield University Exam Takeaways\n"
                    f"1. **Recurrence Solving**: Master the 3 cases of the Master Theorem.\n"
                    f"2. **Stability**: Merge sort is inherently stable; quicksort is generally not.\n"
                    f"3. **Auxiliary Space**: Standard merge sort requires $O(n)$ additional memory for temporary arrays.\n"
                    f"4. **Common Pitfall**: Forgetting the base case `len(arr) <= 1` results in infinite recursion stack overflow."
                )
            elif is_automata:
                obj_title = f"Learning Outcomes & Formal Language Foundations: {topic_clean}"
                obj_content = (
                    f"## 🎯 Learning Outcomes & Competencies\n"
                    f"- Understand the formal mathematical definition of a 5-tuple Deterministic Finite Automaton $M = (Q, \\Sigma, \\delta, q_0, F)$.\n"
                    f"- Formulate transition functions $\\delta: Q \\times \\Sigma \\to Q$ and trace acceptance states.\n"
                    f"- Distinguish between regular languages and context-free languages in the Chomsky Hierarchy.\n\n"
                    f"### 📚 Prerequisites & Readiness\n"
                    f"- Set theory basics (Cartesian products, subsets, empty set $\\emptyset$).\n"
                    f"- Discrete mathematics and formal alphabet definitions ($\\Sigma = \\{{0, 1\\}}$).\n\n"
                    f"### 💡 Why This Topic Matters\n"
                    f"Automata theory provides the theoretical foundation for compiler lexical analysis, regular expression engines, and state machine validation."
                )
                expl_title = f"Formal Automaton Architecture & State Transitions: {topic_clean}"
                expl_content = (
                    f"## 🔬 Mathematical Definition of a DFA\n"
                    f"A Deterministic Finite Automaton (DFA) is formally defined as a 5-tuple:\n"
                    f"$$M = (Q, \\Sigma, \\delta, q_0, F)$$\n\n"
                    f"- $Q$: Finite set of internal states.\n"
                    f"- $\\Sigma$: Finite set of input symbols (alphabet).\n"
                    f"- $\\delta$: Transition function mapping $Q \\times \\Sigma \\to Q$.\n"
                    f"- $q_0 \\in Q$: Initial start state.\n"
                    f"- $F \\subseteq Q$: Set of accept/final states.\n\n"
                    f"> [!NOTE]\n"
                    f"> **Determinism Property**: For every state $q \\in Q$ and symbol $a \\in \\Sigma$, there is exactly ONE transition $\\delta(q, a)$ defined.\n\n"
                    f"### The Chomsky Hierarchy Overview\n\n"
                    f"| Level | Language Class | Recognizing Automaton | Production Rule Form |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"| Type 3 | Regular | Finite Automaton (DFA/NFA) | $A \\to aB$ or $A \\to a$ |\n"
                    f"| Type 2 | Context-Free | Pushdown Automaton (PDA) | $A \\to \\alpha$ |\n"
                    f"| Type 1 | Context-Sensitive | Linear-Bounded Automaton | $\\alpha A \\beta \\to \\alpha \\gamma \\beta$ |\n"
                    f"| Type 0 | Unrestricted / RE | Turing Machine | $\\gamma \\to \\alpha$ |"
                )
                code_title = f"Formal Automaton Simulation: DeterministicFiniteAutomaton"
                code_lang = "python"
                code_snippet = (
                    "class DeterministicFiniteAutomaton:\n"
                    '    """Simulates a 5-tuple DFA M = (Q, Sigma, delta, q0, F) recognizing binary strings ending in \\\'01\\\'."""\\n'
                    "    def __init__(self):\n"
                    '        self.states = {"q0", "q1", "q2"}\n'
                    '        self.alphabet = {"0", "1"}\n'
                    '        self.start_state = "q0"\n'
                    '        self.accept_states = {"q2"}\n'
                    "        self.transitions = {\n"
                    '            ("q0", "0"): "q1", ("q0", "1"): "q0",\n'
                    '            ("q1", "0"): "q1", ("q1", "1"): "q2",\n'
                    '            ("q2", "0"): "q1", ("q2", "1"): "q0",\n'
                    "        }\n\n"
                    "    def accepts(self, input_string: str) -> bool:\n"
                    "        curr = self.start_state\n"
                    "        for symbol in input_string:\n"
                    "            if symbol not in self.alphabet:\n"
                    "                return False\n"
                    "            curr = self.transitions[(curr, symbol)]\n"
                    "        return curr in self.accept_states\n\n"
                    "# Verified test suite\n"
                    "dfa = DeterministicFiniteAutomaton()\n"
                    'assert dfa.accepts("1001") is True\n'
                    'assert dfa.accepts("1010") is False\n'
                    'assert dfa.accepts("01") is True\n'
                    'assert dfa.accepts("") is False'
                )
                code_content = (
                    f"## 🛠️ Step-by-Step DFA Simulator\n"
                    f"The verified Python class below models the transition delta function and validates string acceptance:\n\n"
                    f"```{code_lang}\n{code_snippet}\n```\n\n"
                    f"### 🔍 State Invariants\n"
                    f"- State `q0`: Neutral state (last symbol was not '0', or initial).\n"
                    f"- State `q1`: Holds memory of having just observed a '0'.\n"
                    f"- State `q2`: Accepting state reached when '0' is immediately followed by '1'."
                )
                vis_title = f"DFA State Machine Transition Diagram"
                vis_content = (
                    f"## 📊 State Machine Transition Diagram\n\n"
                    f"```mermaid\n"
                    f"stateDiagram-v2\n"
                    f"    [*] --> q0\n"
                    f'    q0 --> q1: input "0"\n'
                    f'    q0 --> q0: input "1"\n'
                    f'    q1 --> q1: input "0"\n'
                    f'    q1 --> q2: input "1"\n'
                    f'    q2 --> q1: input "0"\n'
                    f'    q2 --> q0: input "1"\n'
                    f"```\n\n"
                    f"### 🔄 Operational State Semantics\n"
                    f"- **Start State**: Directed arrow from `[*]` entering `q0`.\n"
                    f"- **Accepting State**: `q2` represents successful recognition of pattern ending in `01`."
                )
                task_title = f"Applied Automaton Design & Exam Preparation: {topic_clean}"
                task_content = (
                    f"## 🎯 Applied Automaton Challenge\n"
                    f"**Problem**: Construct a minimal DFA over $\\Sigma = \\{{a, b\\}}$ that accepts all strings where the number of $a$'s is a multiple of 3.\n\n"
                    f"### 📋 Requirements\n"
                    f"- Specify $Q$, $\\Sigma$, $\\delta$, $q_0$, and $F$.\n"
                    f"- Verify acceptance on strings: $\\varepsilon, aaa, baaab, aaba$.\n\n"
                    f"### 💡 High-Yield University Exam Takeaways\n"
                    f"1. **Pumping Lemma**: Used exclusively to prove a language is NOT regular, never that it is regular.\n"
                    f"2. **DFA vs NFA**: Every NFA has an equivalent DFA via the subset construction algorithm ($2^{{|Q|}}$ states worst case).\n"
                    f"3. **Closure Properties**: Regular languages are closed under union, intersection, complementation, and concatenation."
                )
            else:
                obj_title = f"Learning Outcomes & Practical Competencies: {topic_clean}"
                obj_content = (
                    f"## 🎯 Learning Outcomes & Competencies\n"
                    f"- Master the fundamental syntax, execution mechanics, and principles of **{topic_clean}**.\n"
                    f"- Write clean, readable, and functional solutions with proper error handling.\n"
                    f"- Trace program execution state step-by-step and verify execution results.\n\n"
                    f"### 📚 Prerequisites & Readiness\n"
                    f"- Basic variables, conditional logic, and procedural control flow."
                )
                expl_title = f"Core Concepts & Execution Mechanics: {topic_clean}"
                expl_content = (
                    f"## 🔬 Foundations & Core Principles\n"
                    f"Understanding **{topic_clean}** requires examining runtime execution and state transitions.\n\n"
                    f"> [!NOTE]\n"
                    f"> **Key Principle**: Clear structure and predictable state transitions minimize runtime defects and simplify debugging."
                )
                code_title = f"Hands-On Implementation Walkthrough: {topic_clean}"
                code_lang = "python"
                code_snippet = (
                    f"# Practical implementation for {topic_clean}\n\n"
                    f"def solve_{topic_clean.lower().replace(' ', '_').replace('-', '_')}():\n"
                    f'    """Demonstrates execution logic for {topic_clean}."""\n'
                    f'    items = ["Initial State", "Processing", "Completed"]\n'
                    f"    result = []\n"
                    f"    for item in items:\n"
                    f"        result.append(f'Handled: {{item}}')\n"
                    f"    return result\n\n"
                    f"output = solve_{topic_clean.lower().replace(' ', '_').replace('-', '_')}()\n"
                    f"assert len(output) == 3\n"
                    f"print('Successfully executed:', output)"
                )
                code_content = (
                    f"## 🛠️ Step-by-Step Implementation\n\n"
                    f"```{code_lang}\n{code_snippet}\n```"
                )
                vis_title = f"Execution Flow & Logic Map: {topic_clean}"
                vis_content = (
                    f"## 📊 Execution Flow\n\n"
                    f"```mermaid\n"
                    f"flowchart TD\n"
                    f'    A["Input Data"] --> B["Processing Logic: {topic_clean}"]\n'
                    f'    B --> C["Validation & Transformation"]\n'
                    f'    C --> D["Return Output"]\n'
                    f"```"
                )
                task_title = f"Hands-On Challenge & Exam Takeaways: {topic_clean}"
                task_content = (
                    f"## 🎯 Applied Hands-On Challenge\n"
                    f"Extend the implementation above to handle boundary cases such as empty inputs or negative values.\n\n"
                    f"### 💡 Key Exam Takeaways\n"
                    f"- Always validate inputs before performing state transformations.\n"
                    f"- Test code thoroughly against nominal, boundary, and edge conditions."
                )

            blocks = [
                LessonBlock(type=LessonBlockType.OBJECTIVE, title=obj_title, content=obj_content),
                LessonBlock(type=LessonBlockType.EXPLANATION, title=expl_title, content=expl_content),
                LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title=code_title, content=code_content, code=code_snippet, language=code_lang),
                LessonBlock(type=LessonBlockType.VISUAL_SPEC, title=vis_title, content=vis_content),
                LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=task_title, content=task_content),
            ]

        elif archetype == DomainArchetype.BUSINESS_MANAGEMENT:
            obj_title = f"Learning Outcomes & Managerial Context: {topic_clean}"
            obj_content = (
                f"## 🎯 Learning Outcomes & Competencies\n"
                f"- Understand core strategic and operational responsibilities across the 4 managerial functions: Planning, Organizing, Directing, and Controlling.\n"
                f"- Analyze corporate leadership structures and organizational behavior in competitive enterprise environments.\n"
                f"- Apply strategic audit frameworks (SWOT, PESTLE) to real-world corporate scenarios.\n\n"
                f"### 📚 Prerequisites & Readiness\n"
                f"- Basic understanding of business organizations, market competition, and commercial enterprises.\n"
                f"- Familiarity with stakeholder perspectives (shareholders, customers, employees, community).\n\n"
                f"### 💡 Why This Topic Matters\n"
                f"Effective managerial leadership separates surviving enterprises from failing ones. Modern Indian and global corporate giants like the Tata Group, Reliance, Swiggy, and Infosys scale sustainably through rigorous planning, transparent delegation, and agile operational controls."
            )
            expl_title = f"Conceptual Masterclass: Principles & Theories of Management"
            expl_content = (
                f"## 🔬 Foundations of Management Thought\n"
                f"Management is the art and science of coordinating collective human effort and material resources toward defined institutional goals.\n\n"
                f"> [!NOTE]\n"
                f"> **Henri Fayol's Administrative Theory**: Outlines 14 immutable principles including Division of Work, Authority & Responsibility, Unity of Command, and Remuneration.\n\n"
                f"### Managerial Hierarchy & Functional Scope\n\n"
                f"| Managerial Tier | Primary Roles | Key Deliverables | Time Horizon |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| **Top-Level (Executive)** | CEO, MD, Board of Directors | Vision, PESTLE Analysis, Capital Allocation | Long-Term (3-5 Years) |\n"
                f"| **Middle-Level (Tactical)** | Regional Heads, Plant Managers | Resource Deployment, Departmental OKRs | Medium-Term (6-18 Months) |\n"
                f"| **First-Line (Operational)** | Supervisors, Team Leads | Daily Scheduling, Quality Control, Safety | Short-Term (Daily / Weekly) |\n\n"
                f"### Core Invariants of Effective Leadership\n"
                f"- **Unity of Command**: An employee must receive orders from exactly one superior to prevent conflicting operational priorities.\n"
                f"- **Span of Control**: The number of direct subordinates a manager can effectively oversee is bounded by task complexity and geographical dispersion.\n"
                f"- **Scalar Chain**: Formal communication lines run unbroken from the highest executive to the front line, with provision for Fayol's *gangplank* during emergencies."
            )
            case_title = f"Applied Corporate Case Study: Tata Group Strategic Execution"
            case_content = (
                f"## 🏢 Case Study: Strategic Organizational Architecture at Tata Group\n\n"
                f"### 1. Executive Situation & Context\n"
                f"The Tata Group encompasses over 30 operating companies spanning 10 business verticals (automotive, steel, hospitality, digital services, consumer goods). The group sought to maintain aggressive multi-market growth while enforcing uncompromising ethical governance.\n\n"
                f"### 2. The Core Strategic Challenge\n"
                f"How can a diversified conglomerate decentralize operational P&L accountability to autonomous business unit leaders without diluting group brand equity or compromising the Tata Code of Conduct (TCoC)?\n\n"
                f"### 3. Managerial Intervention & Implementation\n"
                f"- **Decentralized Execution**: Tata Motors, TCS, and Tata Consumer operate with independent boards and dedicated operational leadership.\n"
                f"- **Centralized Governance & TBEM**: Enforced the Tata Business Excellence Model (TBEM), standardizing operational audit metrics across all subsidiaries.\n"
                f"- **Values-Driven Leadership**: Zero tolerance for ethics violations, audited directly by independent ethics counselors.\n\n"
                f"### 4. Measurable Enterprise Results\n"
                f"- Global brand valuation exceeding \\$24 billion.\n"
                f"- Consistent top-tier corporate governance and credit ratings across all listed operating entities.\n"
                f"- Seamless entry into cutting-edge sectors (semiconductors, EV batteries, super-apps)."
            )
            vis_title = f"Strategic Management Framework & Closed-Loop Control"
            vis_content = (
                f"## 📊 Closed-Loop Managerial Control Architecture\n\n"
                f"```mermaid\n"
                f"flowchart TD\n"
                f'    A["Corporate Vision & Stakeholder Objectives"] --> B["Strategic Planning (PESTLE & SWOT Audit)"]\n'
                f'    B --> C["Organizing: Structure, Staffing & Delegation"]\n'
                f'    C --> D["Directing: Motivation, Communication & Leadership"]\n'
                f'    D --> E["Controlling: KPI Performance Measurement"]\n'
                f'    E -->|"Variance Analysis & Corrective Feedback"| B\n'
                f"```\n\n"
                f"### 🔄 Comparative Framework of Managerial Theories\n\n"
                f"| School of Thought | Key Pioneers | Core Premise | Primary Focus |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| **Classical / Scientific** | F.W. Taylor, Henri Fayol, Max Weber | Workers are motivated economically; efficiency stems from job standardization. | Task optimization & formal hierarchy |\n"
                f"| **Human Relations** | Elton Mayo (Hawthorne Studies) | Social relationships, informal groups, and recognition drive productivity. | Employee psychological well-being |\n"
                f"| **Contingency / Modern** | Peter Drucker, Michael Porter | No single management method fits all organizations; actions depend on environment. | Situational adaptation & competitive advantage |"
            )
            task_title = f"Executive Reflection Challenge & University Exam Takeaways: {topic_clean}"
            task_content = (
                f"## 🎯 Applied Executive Scenario Challenge\n"
                f"**Scenario**: You are appointed Chief Operating Officer of a fast-growing Indian retail chain scaling from 10 to 60 locations within 12 months. Store managers report severe inventory delays and burnout due to seeking headquarters approval for minor store expenses.\n\n"
                f"### 📋 Strategic Assignment\n"
                f"1. Design a delegation matrix defining the monetary spending threshold permitted for store managers.\n"
                f"2. Formulate 3 internal control metrics to detect stock shrink and budget variances without micromanaging daily operations.\n\n"
                f"### 💡 High-Yield University Exam Preparation\n"
                f"1. **Taylor vs. Fayol**: Taylor concentrated on the shop-floor operational level (time & motion studies); Fayol analyzed overall administrative management from the top down.\n"
                f"2. **Management by Objectives (MBO)**: First popularized by Peter Drucker, ensuring employee goals directly align with corporate mission.\n"
                f"3. **Common Exam Mistake**: Do not confuse *delegation* (transfer of authority from superior to subordinate) with *decentralization* (systematic corporate-wide policy philosophy)."
            )

            blocks = [
                LessonBlock(type=LessonBlockType.OBJECTIVE, title=obj_title, content=obj_content),
                LessonBlock(type=LessonBlockType.EXPLANATION, title=expl_title, content=expl_content),
                LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title=case_title, content=case_content),
                LessonBlock(type=LessonBlockType.VISUAL_SPEC, title=vis_title, content=vis_content),
                LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=task_title, content=task_content),
            ]

        elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT:
            obj_title = f"Learning Outcomes & Accounting Standards Framework: {topic_clean}"
            obj_content = (
                f"## 🎯 Learning Outcomes & Competencies\n"
                f"- Master the fundamental Accounting Equation: $\\text{{Assets}} = \\text{{Liabilities}} + \\text{{Owner's Equity}}$.\n"
                f"- Apply the Golden Rules of Debit and Credit across Personal, Real, and Nominal accounts under double-entry bookkeeping.\n"
                f"- Record source transactions into chronological journal entries, post to ledger T-accounts, and extract a balanced Trial Balance.\n\n"
                f"### 📚 Prerequisites & Readiness\n"
                f"- Mathematical arithmetic, percentage calculations, and basic financial concepts (invoices, receipts, cash vs. credit).\n\n"
                f"### 💡 Regulatory & Real-World Context\n"
                f"Financial accounting governed by Ind-AS (Indian Accounting Standards) and IFRS ensures transparency and fiduciary integrity. Reliable financial records protect investors, enable bank lending, and determine statutory tax obligations."
            )
            expl_title = f"Double-Entry Principles, Account Types & Golden Rules"
            expl_content = (
                f"## 🔬 Foundations of Double-Entry Bookkeeping\n"
                f"Every financial transaction impacts at least two accounts in opposing directions with equal monetary value, maintaining the balance of the accounting equation at all times.\n\n"
                f"> [!NOTE]\n"
                f"> **The Accounting Equation**: $\\text{{Assets}} = \\text{{Liabilities}} + \\text{{Capital}} + (\\text{{Revenues}} - \\text{{Expenses}})$.\n\n"
                f"### The Golden Rules of Accounting\n\n"
                f"| Account Classification | Nature of Account | Golden Rule (Debit) | Golden Rule (Credit) | Examples |\n"
                f"| :--- | :--- | :--- | :--- | :--- |\n"
                f"| **Personal Account** | Relates to persons, firms, or entities | **Debit the Receiver** | **Credit the Giver** | Suppliers, Customers, Bank A/c |\n"
                f"| **Real Account** | Tangible and intangible assets/property | **Debit What Comes In** | **Credit What Goes Out** | Cash, Plant, Machinery, Patents |\n"
                f"| **Nominal Account** | Revenues, expenses, gains, and losses | **Debit All Expenses & Losses** | **Credit All Incomes & Gains** | Rent, Wages, Sales, Interest Received |\n\n"
                f"### Core Accounting Conventions\n"
                f"- **Accrual Concept**: Revenues and expenses are recognized when earned or incurred, regardless of when cash is settled.\n"
                f"- **Prudence / Conservatism**: Anticipate no profits, but provide for all foreseeable losses.\n"
                f"- **Materiality**: Items of significant economic consequence to decision-makers must be disclosed explicitly."
            )
            num_title = f"Step-by-Step Practical Problem: Journal Entries to Trial Balance"
            num_content = (
                f"## 📝 Worked Practical Problem: Journalizing Commercial Transactions\n\n"
                f"**Transaction Scenario**: An enterprise initiates commercial operations with the following chronological events:\n"
                f"1. *April 1, 2026*: Proprietor introduces capital into business bank account: ₹5,00,000.\n"
                f"2. *April 4, 2026*: Purchased inventory goods on credit from Alpha Supplies Ltd: ₹1,20,000.\n"
                f"3. *April 10, 2026*: Sold goods on credit to Beta Enterprises: ₹1,80,000 (cost of goods ₹1,00,000).\n"
                f"4. *April 20, 2026*: Paid office rent via bank transfer: ₹25,000.\n\n"
                f"### General Journal Record (Original Entry)\n\n"
                f"| Date (2026) | Particulars | L.F. | Debit Amount (₹) | Credit Amount (₹) |\n"
                f"| :--- | :--- | :--- | :--- | :--- |\n"
                f"| **Apr 01** | **Bank A/c ... Dr.** | 01 | 5,00,000 | |\n"
                f"| | To Capital A/c | 02 | | 5,00,000 |\n"
                f"| | *(Being capital introduced by proprietor into business)* | | | |\n"
                f"| **Apr 04** | **Purchases / Inventory A/c ... Dr.** | 03 | 1,20,000 | |\n"
                f"| | To Alpha Supplies Ltd A/c | 04 | | 1,20,000 |\n"
                f"| | *(Being goods purchased on credit terms)* | | | |\n"
                f"| **Apr 10** | **Beta Enterprises A/c ... Dr.** | 05 | 1,80,000 | |\n"
                f"| | To Sales Revenue A/c | 06 | | 1,80,000 |\n"
                f"| | *(Being goods sold on credit)* | | | |\n"
                f"| **Apr 20** | **Rent Expense A/c ... Dr.** | 07 | 25,000 | |\n"
                f"| | To Bank A/c | 01 | | 25,000 |\n"
                f"| | *(Being office rent paid through bank)* | | | |\n\n"
                f"### Trial Balance Verification at April 30, 2026\n\n"
                f"| Ledger Account Title | Debit Balance (₹) | Credit Balance (₹) |\n"
                f"| :--- | :--- | :--- |\n"
                f"| Bank A/c (₹5,00,000 - ₹25,000) | 4,75,000 | - |\n"
                f"| Capital A/c | - | 5,00,000 |\n"
                f"| Purchases A/c | 1,20,000 | - |\n"
                f"| Alpha Supplies Ltd (Creditor) | - | 1,20,000 |\n"
                f"| Beta Enterprises (Debtor) | 1,80,000 | - |\n"
                f"| Sales Revenue A/c | - | 1,80,000 |\n"
                f"| Rent Expense A/c | 25,000 | - |\n"
                f"| **TOTALS (ARITHMETICAL PROOF)** | **₹8,00,000** | **₹8,00,000** |"
            )
            vis_title = f"The End-to-End Accounting Cycle"
            vis_content = (
                f"## 📊 The Systematic Accounting Information Flow\n\n"
                f"```mermaid\n"
                f"flowchart LR\n"
                f'    A["Source Documents (Invoices & Vouchers)"] --> B["Journalizing (Books of Original Entry)"]\n'
                f'    B --> C["Ledger Accounts Posting (T-Accounts)"]\n'
                f'    C --> D["Trial Balance Extraction (Arithmetical Audit)"]\n'
                f'    D --> E["Adjustment Entries (Depreciation, Accruals)"]\n'
                f'    E --> F["Final Financial Statements (P&L & Balance Sheet)"]\n'
                f"```\n\n"
                f"### 🔄 Key Distinction: Capital vs Revenue Expenditure\n\n"
                f"| Dimension | Capital Expenditure | Revenue Expenditure |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Economic Life** | Benefits extend across multiple accounting periods (> 1 Year). | Consumed entirely within current accounting cycle (< 1 Year). |\n"
                f"| **Balance Sheet Impact** | Capitalized as an Asset on the Balance Sheet. | Expensed directly to the Income / P&L Statement. |\n"
                f"| **Earning Capacity** | Enhances future revenue-generating capacity. | Maintains existing operating efficiency and assets. |"
            )
            task_title = f"Applied Numerical Challenge & Exam Takeaways: {topic_clean}"
            task_content = (
                f"## 🎯 Applied Numerical Practice Problem\n"
                f"**Scenario**: On March 31, 2026, an accountant discovers ₹15,000 in accrued but unpaid employee salaries and ₹8,000 in prepaid annual insurance.\n\n"
                f"### 📋 Assignment\n"
                f"1. Pass the adjusting journal entries required under the accrual basis of accounting.\n"
                f"2. Explain the net impact on reported operating profit before and after adjustments.\n\n"
                f"### 💡 High-Yield University Exam Takeaways\n"
                f"1. **Trial Balance Agreement**: A balanced trial balance proves arithmetical accuracy but does NOT guarantee freedom from errors of omission or principle.\n"
                f"2. **Bad Debts & Provisions**: Creation of a provision for doubtful debts is mandated by the Conservatism / Prudence convention.\n"
                f"3. **Common Exam Mistake**: Never credit purchases account directly when inventory is purchased; only credit purchases during purchase returns or private proprietor drawings."
            )

            blocks = [
                LessonBlock(type=LessonBlockType.OBJECTIVE, title=obj_title, content=obj_content),
                LessonBlock(type=LessonBlockType.EXPLANATION, title=expl_title, content=expl_content),
                LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title=num_title, content=num_content),
                LessonBlock(type=LessonBlockType.VISUAL_SPEC, title=vis_title, content=vis_content),
                LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=task_title, content=task_content),
            ]

        elif archetype == DomainArchetype.APPLIED_OFFICE_IT:
            obj_title = f"Learning Outcomes & Enterprise Office IT: {topic_clean}"
            obj_content = (
                f"## 🎯 Learning Outcomes & Competencies\n"
                f"- Master spreadsheet modeling, automated formula evaluation, and tabular data integrity.\n"
                f"- Implement advanced dynamic lookups (`XLOOKUP`, `INDEX/MATCH`) and conditional aggregations (`SUMIFS`).\n"
                f"- Construct automated executive dashboards and enforce data validation audit rules.\n\n"
                f"### 📚 Prerequisites & Readiness\n"
                f"- Basic familiarity with office productivity software (spreadsheets, docs, cloud workbooks).\n\n"
                f"### 💡 Enterprise Relevance\n"
                f"Modern commercial businesses rely on automated spreadsheet workbooks for budgeting, financial analysis, sales reporting, and payroll calculation without requiring custom software engineering."
            )
            expl_title = f"Workbook Architecture & Advanced Formula Mechanics"
            expl_content = (
                f"## 🔬 Spreadsheet Data Modeling Principles\n"
                f"Professional spreadsheets separate raw transactional data inputs from calculation engines and final presentation dashboards.\n\n"
                f"> [!NOTE]\n"
                f"> **Absolute vs Relative Referencing**: Prefixing a cell coordinate with `$` (e.g. `$B$4`) locks the row or column coordinate when dragging formulas across ranges.\n\n"
                f"### Essential Business Lookup Functions\n\n"
                f"| Function | Purpose | Syntax | Advantages Over Legacy VLOOKUP |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| **`XLOOKUP`** | Modern universal lookup | `=XLOOKUP(lookup_val, lookup_rng, return_rng, [if_not_found], [match_mode])` | Looks left and right; defaults to exact match; robust against column insertions. |\n"
                f"| **`INDEX/MATCH`** | Two-dimensional matrix lookup | `=INDEX(return_rng, MATCH(lookup_val, lookup_rng, 0))` | High performance on huge datasets; dynamic row/column coordinates. |\n"
                f"| **`SUMIFS`** | Multi-condition sum | `=SUMIFS(sum_rng, criteria_rng1, criteria1, criteria_rng2, criteria2)` | Aggregates sales or expenses across specific dates, regions, and categories. |"
            )
            office_title = f"Step-by-Step Business Modeling: Automated Sales Reporting Workbook"
            office_content = (
                f"## 📊 Step-by-Step Practical Spreadsheet Walkthrough\n\n"
                f"### 1. Data Schema & Table Structure\n"
                f"Consider an enterprise transactions table `SalesData` containing `OrderID`, `SalespersonID`, `Region`, `Date`, and `RevenueAmount`.\n\n"
                f"### 2. Implementation Formulas\n"
                f"- **Salesperson Name Dynamic Lookup**:\n"
                f"  `=XLOOKUP(B2, StaffDirectory!$A$2:$A$100, StaffDirectory!$B$2:$B$100, 'Unknown ID', 0)`\n"
                f"- **Regional Sales Q1 Aggregation**:\n"
                f"  `=SUMIFS(SalesData!$E:$E, SalesData!$C:$C, 'North', SalesData!$D:$D, '>=' & DATE(2026,1,1), SalesData!$D:$D, '<=' & DATE(2026,3,31))`\n"
                f"- **Tiered Commission Calculation**:\n"
                f"  `=IFS(E2 >= 100000, E2 * 0.10, E2 >= 50000, E2 * 0.07, TRUE, E2 * 0.04)`\n\n"
                f"### 3. Verification & Error Trapping\n"
                f"Wrapping formulas with `=IFERROR(formula, alternative_value)` ensures dashboards display clean summaries rather than breaking with `#N/A` or `#DIV/0!`."
            )
            vis_title = f"Automated Reporting Pipeline Flowchart"
            vis_content = (
                f"## 📊 Automated Spreadsheet Data Pipeline\n\n"
                f"```mermaid\n"
                f"flowchart LR\n"
                f'    A["Raw Transaction Export (.CSV / ERP)"] --> B["Data Validation & Cleansing Gateway"]\n'
                f'    B --> C["Formula Calculation Engine (XLOOKUP / SUMIFS)"]\n'
                f'    C --> D["Pivot Table Multi-Dimensional Cache"]\n'
                f'    D --> E["Dynamic Executive KPI Dashboard"]\n'
                f"```\n\n"
                f"### 🔄 Data Validation Rules for Integrity\n"
                f"- **Restricted Dropdown Lists**: Prevent typographical entry errors by binding inputs to named ranges.\n"
                f"- **Numerical Boundary Checks**: Enforce positive quantities (`> 0`) on all unit orders."
            )
            task_title = f"Applied Office IT Challenge & Exam Review: {topic_clean}"
            task_content = (
                f"## 🎯 Applied Hands-On Challenge\n"
                f"**Challenge**: Construct a dynamic monthly payroll workbook with 5 employee records calculating Gross Pay, Provident Fund deduction (12%), Income Tax deduction (10%), and Net Pay with dynamic formula propagation.\n\n"
                f"### 💡 Key Exam Takeaways\n"
                f"1. **Order of Evaluation (PEMDAS)**: Spreadsheets evaluate parentheses first, followed by exponents, multiplication/division, and addition/subtraction.\n"
                f"2. **Circular Reference Error**: Occurs when a formula references its own cell coordinate directly or indirectly, preventing convergence.\n"
                f"3. **VLOOKUP Vulnerability**: Hardcoded column index numbers break whenever new columns are inserted into the source data."
            )

            blocks = [
                LessonBlock(type=LessonBlockType.OBJECTIVE, title=obj_title, content=obj_content),
                LessonBlock(type=LessonBlockType.EXPLANATION, title=expl_title, content=expl_content),
                LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title=office_title, content=office_content),
                LessonBlock(type=LessonBlockType.VISUAL_SPEC, title=vis_title, content=vis_content),
                LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=task_title, content=task_content),
            ]

        else:
            # DomainArchetype.GENERAL_HUMANITIES_SCIENCE
            obj_title = f"Learning Outcomes & Academic Context: {topic_clean}"
            obj_content = (
                f"## 🎯 Learning Outcomes & Competencies\n"
                f"- Establish a comprehensive foundation in the core concepts and historical development of **{topic_clean}**.\n"
                f"- Evaluate theoretical frameworks and peer-reviewed methodologies in empirical inquiry.\n"
                f"- Articulate reasoned arguments supported by multidisciplinary evidence.\n\n"
                f"### 📚 Prerequisites & Readiness\n"
                f"- Foundational critical thinking, scientific method inquiry, and analytical reading comprehension."
            )
            expl_title = f"Conceptual Analysis & Theoretical Framework: {topic_clean}"
            expl_content = (
                f"## 🔬 Foundations & Core Principles\n"
                f"Investigation of **{topic_clean}** requires examining underlying assumptions, systemic relationships, and causal mechanisms.\n\n"
                f"> [!NOTE]\n"
                f"> **Methodological Grounding**: Academic inquiry demands empirical validation, reproducible observations, and balanced peer critique."
            )
            hum_title = f"Empirical Case Analysis & Applied Methodology: {topic_clean}"
            hum_content = (
                f"## 📖 Applied Case Analysis\n"
                f"Detailed examination of real-world implementation demonstrating the principles of **{topic_clean}** in active societal and scientific contexts."
            )
            vis_title = f"Conceptual Framework & Relational Map"
            vis_content = (
                f"## 📊 Conceptual Framework\n\n"
                f"```mermaid\n"
                f"flowchart TD\n"
                f'    A["Core Problem Formulation"] --> B["Empirical Inquiry & Evidence Collection"]\n'
                f'    B --> C["Theoretical Framework Application"]\n'
                f'    C --> D["Synthesis & Conclusions"]\n'
                f"```"
            )
            task_title = f"Critical Reflection & University Exam Preparation: {topic_clean}"
            task_content = (
                f"## 🎯 Critical Reflection Challenge\n"
                f"Analyze a contemporary case study illustrating **{topic_clean}** and structure a formal 500-word academic argument.\n\n"
                f"### 💡 Key Exam Takeaways\n"
                f"- Support assertions with recognized theoretical frameworks and peer evidence.\n"
                f"- Clearly differentiate correlation from causation in analysis."
            )

            blocks = [
                LessonBlock(type=LessonBlockType.OBJECTIVE, title=obj_title, content=obj_content),
                LessonBlock(type=LessonBlockType.EXPLANATION, title=expl_title, content=expl_content),
                LessonBlock(type=LessonBlockType.WORKED_EXAMPLE, title=hum_title, content=hum_content),
                LessonBlock(type=LessonBlockType.VISUAL_SPEC, title=vis_title, content=vis_content),
                LessonBlock(type=LessonBlockType.PRACTICE_TASK, title=task_title, content=task_content),
            ]

        assessment_intent = AssessmentIntent(
            target_concepts=[topic_clean],
            assessment_mode="diagnostic" if pedagogy_decision.remediation else "formative",
            difficulty=pedagogy_decision.difficulty.value,
            question_count=3,
            evaluation_criteria=[f"Demonstrate comprehensive mastery of {topic_clean}"],
        )

        next_action = NextLearningAction(
            action_type="reassessment" if pedagogy_decision.remediation else "practice",
            target_topic=topic_clean,
            rationale=(
                f"Complete formative reassessment for '{topic_clean}' to verify remediation success."
                if pedagogy_decision.remediation
                else f"Proceed with guided practice on '{topic_clean}' to build proficiency."
            ),
            urgency="immediate" if pedagogy_decision.remediation else "normal",
        )

        return GeneratedLesson(
            context_id=context_id,
            topic=topic_clean,
            pedagogy_decision=pedagogy_decision,
            blocks=blocks,
            prerequisites=[f"Prerequisite foundations of {topic_clean}"],
            assessment_intent=assessment_intent,
            next_action=next_action,
        )


    def analyze_learner_onboarding(
        self, profile: OnboardingInputProfile, prompt: str
    ) -> LearnerIntelligenceReport:
        target_role = profile.get_effective_target_role()
        concept_mastery = profile.get_effective_concept_mastery()
        weak_topics = profile.get_effective_weak_topics()
        strong_topics = profile.get_effective_strong_topics()
        pref_medium = profile.get_effective_learning_preference()
        weekly_hours = profile.get_effective_weekly_hours()
        ratio = profile.get_effective_practical_ratio()
        pace = profile.get_effective_pace()

        # 1. Evaluate baseline competency from explicit data ONLY
        ratings = [s.self_rating for s in profile.declared_skills]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
        elif concept_mastery:
            avg_rating = (sum(concept_mastery.values()) / len(concept_mastery)) * 5.0
        else:
            avg_rating = None

        # Determine proficiency level
        if avg_rating is not None:
            if avg_rating >= 3.8:
                prof_level = "advanced"
            elif avg_rating >= 2.5:
                prof_level = "intermediate"
            else:
                prof_level = "beginner"
        else:
            prof_level = "beginner"

        # 2. Build Core Strengths (strictly grounded)
        strengths = []
        for s in profile.declared_skills:
            if s.self_rating >= 3:
                strengths.append(s.skill_name)
        for st in strong_topics:
            if st not in strengths:
                strengths.append(st)
        for concept, score in concept_mastery.items():
            if score >= 0.7 and concept not in strengths:
                strengths.append(f"{concept} (Mastery: {score:.0%})")

        if not strengths:
            strengths = ["No verified technical skills declared during onboarding"]

        # 3. Build Critical Skill Gaps & Foundation Topics
        skill_gaps = []
        foundation_topics = []

        for wt in weak_topics:
            if wt not in skill_gaps:
                skill_gaps.append(wt)
            if wt not in foundation_topics:
                foundation_topics.append(wt)

        for concept, score in concept_mastery.items():
            if score < 0.5:
                gap_label = f"{concept} (Remediation)"
                if gap_label not in skill_gaps:
                    skill_gaps.append(gap_label)
                if concept not in foundation_topics:
                    foundation_topics.append(concept)

        default_role_gaps = [
            f"Core {target_role} Architecture",
            "Scalable Systems & Production Readiness",
        ]
        for rg in default_role_gaps:
            if len(skill_gaps) < 4 and rg not in skill_gaps:
                skill_gaps.append(rg)

        default_foundations = [
            f"{target_role} Core Fundamentals",
            "Data Structures & Algorithmic Thinking",
        ]
        for df in default_foundations:
            if len(foundation_topics) < 4 and df not in foundation_topics:
                foundation_topics.append(df)

        # 4. Baseline summary
        if profile.declared_skills:
            baseline_summary = f"Demonstrated self-assessed average competency of {avg_rating:.1f}/5 across {len(profile.declared_skills)} declared skills."
        elif concept_mastery:
            baseline_summary = f"Demonstrated baseline competency across {len(concept_mastery)} assessed concepts (average mastery: {sum(concept_mastery.values())/len(concept_mastery):.0%})."
        elif strong_topics or weak_topics:
            baseline_summary = f"Baseline evaluated from {len(strong_topics)} strong topics and {len(weak_topics)} remediation areas."
        else:
            baseline_summary = "No declared technical skills, prior projects, or baseline diagnostic scores provided in onboarding profile."

        # 5. Theoretical vs Applied balance
        if ratio is not None:
            theoretical_vs_applied = (
                f"Prefers practical application (ratio {ratio:.2f}) with scaffolding."
                if ratio >= 0.5
                else f"Prefers theoretical foundations (ratio {ratio:.2f}) before hands-on tasks."
            )
        else:
            theoretical_vs_applied = "Information unavailable: no practical vs theoretical preference was provided by the learner."

        # 6. Pacing and modality
        dominant_modality = pref_medium if pref_medium else "adaptive"
        effective_pacing = pace if pace else ("scaffolded" if prof_level == "beginner" else "standard")

        # 7. Timeline & Alignment
        if weekly_hours is not None:
            timeline_months = max(3, int(300 / max(1, weekly_hours * 4)))
        else:
            timeline_months = None

        if avg_rating is not None:
            alignment_score = round(min(1.0, max(0.2, avg_rating / 5.0)), 2)
            readiness_score = round(min(0.95, max(0.35, avg_rating / 5.0 + (0.1 if profile.stage == LearnerStage.MASTER else 0.0))), 2)
        else:
            alignment_score = 0.30
            readiness_score = 0.40

        if readiness_score >= 0.75:
            readiness_tier = ReadinessTier.HIGH
            entry_level = "advanced"
        elif readiness_score >= 0.55:
            readiness_tier = ReadinessTier.MODERATE
            entry_level = "intermediate"
        else:
            readiness_tier = ReadinessTier.NEEDS_SCAFFOLDING
            entry_level = "foundational"

        # 8. Grounded executive summary
        stage_desc = f" ({profile.stage.value} stage)" if profile.stage else ""
        exec_parts = [
            f"Learner {profile.learner_id}{stage_desc} is targeting '{target_role}'."
        ]
        if profile.declared_skills:
            exec_parts.append(f"Demonstrates {prof_level} baseline across {len(profile.declared_skills)} declared skills.")
        elif concept_mastery:
            exec_parts.append(f"Diagnostic mastery evaluated across {len(concept_mastery)} concepts.")
        else:
            exec_parts.append("Profile has no declared skills or prior projects, requiring foundational scaffolding.")

        if pref_medium:
            exec_parts.append(f"Prefers {pref_medium} learning style.")
        if weekly_hours is not None:
            exec_parts.append(f"Committed to {weekly_hours}h/week study schedule.")

        return LearnerIntelligenceReport(
            learner_id=profile.learner_id,
            stage=profile.get_effective_stage(),
            target_role=target_role,
            executive_summary=" ".join(exec_parts),
            skill_analysis=SkillAnalysis(
                baseline_summary=baseline_summary,
                proficiency_level=prof_level,
                core_strengths=strengths,
                critical_skill_gaps=skill_gaps,
            ),
            knowledge_analysis=KnowledgeAnalysis(
                conceptual_depth="foundational" if prof_level == "beginner" else "applied",
                prerequisite_health="needs_remediation" if prof_level == "beginner" else "solid",
                theoretical_vs_applied_balance=theoretical_vs_applied,
                recommended_foundation_topics=foundation_topics,
            ),
            learning_style=LearningStyleProfile(
                dominant_modality=dominant_modality,
                secondary_modality="interactive" if dominant_modality != "interactive" else "visual",
                recommended_pacing=effective_pacing,
                feedback_cadence="Immediate feedback after every worked practice task",
                content_format_priorities=["worked_example", "practice_task", "visual_spec"],
            ),
            career_goals=CareerGoalProfile(
                target_role=target_role,
                role_alignment_score=alignment_score,
                key_milestones=[
                    f"Milestone 1: Core {target_role} fundamentals",
                    "Milestone 2: Guided end-to-end project implementation",
                    "Milestone 3: Advanced domain design and production optimization",
                ],
                high_priority_competencies=[
                    f"{target_role} Core Competencies",
                    "Modular System Architecture",
                    "Testing & Reliability Automation",
                ],
                estimated_timeline_months=timeline_months,
            ),
            motivation=MotivationProfile(
                primary_driver="career_growth" if not profile.motivation_statement else "learner_stated_goal",
                intrinsic_vs_extrinsic="balanced",
                engagement_hooks=[
                    "Hands-on milestone builds",
                    "Real-world scenario simulations",
                ],
                potential_frustration_triggers=[
                    "Abstract theoretical lectures without applied examples",
                    "Steep unassisted difficulty leaps",
                ],
                resilience_advice="Break complex problems into verifiable 15-minute micro-objectives.",
            ),
            readiness=ReadinessAssessment(
                overall_readiness_score=readiness_score,
                readiness_tier=readiness_tier,
                recommended_entry_level=entry_level,
                onboarding_recommendations=[
                    "Complete foundational prerequisite orientation",
                    "Set up initial guided project milestone",
                    "Calibrate weekly study schedule",
                ],
            ),
        )


    def generate_build_coaching(self, prompt: str) -> _Dict[str, Any]:
        """Deterministic mock build coaching response — domain-adaptive, zero external calls."""
        prompt_lower = prompt.lower()

        # Determine coaching tone from mastery evidence in prompt
        if "weak" in prompt_lower and "proficient" not in prompt_lower:
            tone = "encouraging"
            remediation = True
        elif "proficient" in prompt_lower:
            tone = "challenging"
            remediation = False
        else:
            tone = "instructive"
            remediation = False

        # Domain-adaptive example block content
        if any(t in prompt_lower for t in ["commerce", "business_plan", "accounting", "finance"]):
            example_content = "Worked example: Construct a break-even analysis table using fixed vs variable cost data from the provided scenario."
        elif any(t in prompt_lower for t in ["law", "case_analysis", "legal"]):
            example_content = "Worked example: Apply the IRAC structure to the leading precedent identified in your submission draft."
        elif any(t in prompt_lower for t in ["science", "lab_notebook", "research_report", "biotech"]):
            example_content = "Worked example: Structure your methodology section using hypothesis → variables → procedure → data collection format."
        elif any(t in prompt_lower for t in ["humanities", "essay", "psychology", "history"]):
            example_content = "Worked example: Anchor your argument using a primary source quotation followed by analytical commentary."
        else:
            example_content = "Worked example: Break the current milestone into three verifiable sub-tasks and complete each before moving to the next."

        # Extract project title from prompt for personalisation
        project_title = "your project"
        for line in prompt.split("\n"):
            if "Project Title:" in line:
                project_title = line.split("Project Title:")[-1].strip()
                break

        return {
            "coaching_tone": tone,
            "coaching_blocks": [
                {
                    "block_type": "orientation",
                    "title": "Where You Stand",
                    "content": (
                        f"This coaching session focuses on '{project_title}'. "
                        "Based on your submission summary and mastery evidence, here is a structured review of your progress."
                    ),
                },
                {
                    "block_type": "gap_analysis",
                    "title": "Identified Gaps",
                    "content": (
                        "Review the rubric criteria listed above. Your submission addresses the core requirements "
                        "but may need deeper engagement with the analytical depth and citation rigor specified."
                    ),
                },
                {
                    "block_type": "guidance",
                    "title": "Key Improvement Actions",
                    "content": (
                        "Focus on the following: (1) Strengthen your evidence with domain-specific references. "
                        "(2) Make your argument or solution logic explicit and step-by-step. "
                        "(3) Address any weak prerequisite concepts before advancing."
                    ),
                },
                {
                    "block_type": "example",
                    "title": "Worked Example",
                    "content": example_content,
                },
                {
                    "block_type": "next_step",
                    "title": "Recommended Next Action",
                    "content": (
                        "Complete the revision checklist above, then request a review of the updated milestone. "
                        "If weak prerequisite topics remain unresolved, complete the associated remediation lesson first."
                    ),
                },
            ],
            "gap_summary": (
                "The submission demonstrates effort but requires stronger alignment to rubric criteria, "
                "particularly in analytical depth and evidence grounding."
            ),
            "next_milestone_hint": "Revise the current section addressing the identified gaps, then submit for re-evaluation.",
            "remediation_recommended": remediation,
        }

    def generate_career_response(self, prompt: str) -> _Dict[str, Any]:
        """Deterministic mock career response (resume generation & ATS analysis) — zero external calls."""
        prompt_lower = prompt.lower()
        if "ats intelligence engine" in prompt_lower or "deterministic rule score" in prompt_lower or "rule findings from engine" in prompt_lower:
            finding_ids = re.findall(r"Finding ID:\s*([^\s\n]+)", prompt)
            findings = []
            for fid in finding_ids:
                findings.append({
                    "id": fid,
                    "category": "ats_optimization",
                    "severity": "suggestion",
                    "title": f"Actionable ATS enhancement for {fid}",
                    "description": f"Enriched critique for {fid}: Recruiters and ATS screening engines require higher metric density and active verbs.",
                    "recommendation": "Use the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'.",
                })
            return {
                "summary": "Candidate displays strong technical foundations and software development background. However, the resume exhibits critical ATS filter liabilities including missing metrics, lack of quantified project impact, and unformatted contact links. Addressing these gaps will improve candidate screening rates.",
                "findings": findings,
            }
        else:
            target_role_match = re.search(r"Target Role:\s*'([^']+)'", prompt)
            target_role = target_role_match.group(1) if target_role_match else "Software Engineer"

            phone_match = re.search(r"- Phone:\s*([^\n]+)", prompt)
            email_match = re.search(r"- Email:\s*([^\n]+)", prompt)
            full_name_match = re.search(r"- Full Name:\s*([^\n]+)", prompt)
            location_match = re.search(r"- Location:\s*([^\n]+)", prompt)
            linkedin_match = re.search(r"- LinkedIn:\s*([^\n]+)", prompt)
            github_match = re.search(r"- GitHub:\s*([^\n]+)", prompt)
            portfolio_match = re.search(r"- Portfolio:\s*([^\n]+)", prompt)

            no_edu = "[no education entries provided" in prompt_lower
            no_exp = "[no work experience provided" in prompt_lower
            no_proj = "[no projects provided" in prompt_lower
            no_ach = "[no achievements provided" in prompt_lower

            edu_ids = re.findall(r"\(ID:\s*([^)]+)\)", prompt)
            
            education = []
            if not no_edu:
                education.append({
                    "id": edu_ids[0] if edu_ids else "edu-001",
                    "institution": "University of Technology",
                    "degree": "Bachelor of Science",
                    "fieldOfStudy": "Computer Science",
                    "startDate": "2020-09",
                    "endDate": "2024-05",
                    "grade": "3.8 GPA",
                })

            experience = []
            if not no_exp:
                experience.append({
                    "id": "exp-001",
                    "company": "Acme Innovations",
                    "role": f"Backend Engineer ({target_role})",
                    "location": "Remote",
                    "startDate": "2023-06",
                    "endDate": "2023-09",
                    "isCurrent": False,
                    "description": "Architected distributed message processing queue handling 100k events/sec with 99.99% availability.",
                })

            projects = []
            if not no_proj:
                projects.append({
                    "id": "proj-001",
                    "name": "Cloud Ledger System",
                    "description": "Engineered event-driven ledger system with automated reconciliation and real-time auditing.",
                    "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                    "projectUrl": "https://github.com/example/ledger",
                    "startDate": "2023-01",
                    "endDate": "2023-05",
                })

            achievements = []
            if not no_ach:
                achievements.append({
                    "id": "ach-001",
                    "title": "AWS Certified Solutions Architect",
                    "description": "Demonstrated mastery of distributed cloud architecture and security principles.",
                    "date": "2024-01",
                })

            return {
                "contact": {
                    "fullName": full_name_match.group(1).strip() if full_name_match else "Jane Doe",
                    "email": email_match.group(1).strip() if email_match else "jane.doe@example.com",
                    "phone": phone_match.group(1).strip() if phone_match else None,
                    "location": location_match.group(1).strip() if location_match else "San Francisco, CA",
                    "linkedInUrl": linkedin_match.group(1).strip() if linkedin_match else None,
                    "githubUrl": github_match.group(1).strip() if github_match else None,
                    "portfolioUrl": portfolio_match.group(1).strip() if portfolio_match else None,
                },
                "headline": f"Impact-Driven {target_role}",
                "summary": f"Results-focused software engineering specialist targeting {target_role} with strong background in distributed systems and performance optimization.",
                "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "System Design"],
                "education": education,
                "experience": experience,
                "projects": projects,
                "achievements": achievements,
            }

    def generate_assessment(self, prompt: str) -> _Dict[str, Any]:
        """Deterministic, discipline-adaptive mock assessment generation with stable IDs and answer keys / rubrics."""
        topic_match = re.search(r"- Topic:\s*([^\n]+)", prompt)
        topic = topic_match.group(1).strip() if topic_match else "Core Principles"

        type_match = re.search(r"- Preferred Question Type:\s*([^\n]+)", prompt)
        pref_type = type_match.group(1).strip().lower() if type_match else "mcq"

        count_match = re.search(r"- Question Count:\s*(\d+)", prompt)
        question_count = int(count_match.group(1)) if count_match else 5

        t_low = (topic + " " + prompt).lower()
        is_entrepreneur = any(k in t_low for k in ["entrepreneur", "business", "startup", "venture", "market", "incubation"])
        is_commerce = any(k in t_low for k in ["commerce", "account", "finance", "banking", "tax", "fiscal", "ledger", "audit"])
        is_law = any(k in t_low for k in ["law", "legal", "constitution", "statute", "jurisprudence", "court", "justice"])
        is_science = any(k in t_low for k in ["physics", "chem", "biology", "medical", "health", "anatomy", "clinical", "pharma"])
        is_humanities = any(k in t_low for k in ["history", "sociol", "philosophy", "politic", "literat", "humanit"])

        # Discipline-tailored question banks (5 questions each)
        if is_entrepreneur:
            q_bank = [
                {
                    "q": f"In {topic}, which methodology emphasizes building a Minimum Viable Product (MVP) to achieve validated learning before scaling?",
                    "options": [
                        ("opt-1", "The Lean Startup Framework (Build-Measure-Learn)"),
                        ("opt-2", "Traditional Waterfall Product Lifecycle"),
                        ("opt-3", "Speculative Inventory Front-Loading"),
                        ("opt-4", "Fixed Five-Year Static Business Planning"),
                    ],
                    "correct": "opt-1",
                    "expl": "The Lean Startup framework prioritizes rapid experimentation, MVP release, and empirical customer feedback to minimize market risk.",
                },
                {
                    "q": f"When evaluating early-stage venture funding in {topic}, what is the primary advantage of bootstrapping over venture capital?",
                    "options": [
                        ("opt-1", "Retaining 100% equity ownership and operational decision autonomy"),
                        ("opt-2", "Instantaneous access to institutional venture networks"),
                        ("opt-3", "Eliminating all personal financial exposure unconditionally"),
                        ("opt-4", "Guaranteed multi-million dollar early valuation multiples"),
                    ],
                    "correct": "opt-1",
                    "expl": "Bootstrapping relies on internal cash flow and personal resources, allowing founders to maintain complete equity and strategic independence.",
                },
                {
                    "q": f"Which instrument in {topic} provides entrepreneurs with legal exclusivity over a novel, non-obvious technological innovation?",
                    "options": [
                        ("opt-1", "Utility Patent Protection"),
                        ("opt-2", "Non-Exclusive Trade Secret Agreement"),
                        ("opt-3", "Creative Commons Open Attribution"),
                        ("opt-4", "Standard Commercial General Liability Policy"),
                    ],
                    "correct": "opt-1",
                    "expl": "A utility patent grants the inventor exclusive commercial rights to prevent others from making, using, or selling the claimed invention.",
                },
                {
                    "q": f"In {topic}, what does achieving 'Product-Market Fit' indicate for a scaling enterprise?",
                    "options": [
                        ("opt-1", "The product satisfies strong market demand with repeatable retention and unit economics"),
                        ("opt-2", "The company has finalized its registration filings with governmental authorities"),
                        ("opt-3", "The enterprise has deployed its first print advertising campaign"),
                        ("opt-4", "The venture has hired its full executive management tier"),
                    ],
                    "correct": "opt-1",
                    "expl": "Product-Market Fit confirms that the venture's offering solves a high-priority problem for a viable, expanding customer segment.",
                },
                {
                    "q": f"Which metric in {topic} compares the gross profit generated from a customer over time against the expenditure required to acquire them?",
                    "options": [
                        ("opt-1", "LTV / CAC Ratio (Customer Lifetime Value to Customer Acquisition Cost)"),
                        ("opt-2", "Current Liquidity Asset Ratio"),
                        ("opt-3", "Inventory Turnover Velocity Index"),
                        ("opt-4", "Depreciation Amortization Schedule"),
                    ],
                    "correct": "opt-1",
                    "expl": "The LTV/CAC ratio evaluates venture unit economics sustainability; healthy business models typically maintain a ratio of 3:1 or higher.",
                },
            ]
        elif is_commerce:
            q_bank = [
                {
                    "q": f"Under standard accrual accounting in {topic}, when must revenue be recognized?",
                    "options": [
                        ("opt-1", "When performance obligations are satisfied, regardless of cash receipt timing"),
                        ("opt-2", "Only when physical currency has cleared the commercial bank account"),
                        ("opt-3", "At the conclusion of the fiscal year audit cycle unconditionally"),
                        ("opt-4", "When preliminary customer inquiries are formally logged"),
                    ],
                    "correct": "opt-1",
                    "expl": "The accrual principle mandates recognizing revenue when earned and realizable upon delivering contracted goods or services.",
                },
                {
                    "q": f"Which financial ratio in {topic} measures a firm's ability to cover short-term liabilities using its most liquid quick assets?",
                    "options": [
                        ("opt-1", "Acid-Test (Quick) Ratio"),
                        ("opt-2", "Debt-to-Equity Solvency Ratio"),
                        ("opt-3", "Price-to-Earnings Valuation Multiple"),
                        ("opt-4", "Gross Profit Contribution Margin"),
                    ],
                    "correct": "opt-1",
                    "expl": "The Quick Ratio excludes illiquid inventory from current assets to test immediate solvency against current liabilities.",
                },
                {
                    "q": f"In {topic}, what is the fundamental balance sheet equation enforced across double-entry bookkeeping?",
                    "options": [
                        ("opt-1", "Assets = Liabilities + Equity"),
                        ("opt-2", "Assets + Liabilities = Net Revenue"),
                        ("opt-3", "Equity = Gross Revenue - Operational Overhead"),
                        ("opt-4", "Cash Flow = Retained Earnings / Debt Capital"),
                    ],
                    "correct": "opt-1",
                    "expl": "The foundational accounting equation mandates that total economic assets equal the combined claims of creditors and owners.",
                },
                {
                    "q": f"Which budgeting mechanism in {topic} requires every single operational expenditure to be justified from a zero base each cycle?",
                    "options": [
                        ("opt-1", "Zero-Based Budgeting (ZBB)"),
                        ("opt-2", "Incremental Baseline Extrapolation"),
                        ("opt-3", "Historical Cost Rolling Forecast"),
                        ("opt-4", "Static Master Capital Appropriation"),
                    ],
                    "correct": "opt-1",
                    "expl": "Zero-Based Budgeting builds expenditure allocations from scratch rather than adjusting prior period baselines.",
                },
                {
                    "q": f"In financial valuation under {topic}, how does Discounted Cash Flow (DCF) determine enterprise intrinsic value?",
                    "options": [
                        ("opt-1", "By discounting projected future free cash flows to present value using WACC"),
                        ("opt-2", "By summing historical book asset costs without depreciation"),
                        ("opt-3", "By multiplying current revenue by trailing inflation indexes"),
                        ("opt-4", "By computing the liquidation price of physical fixtures"),
                    ],
                    "correct": "opt-1",
                    "expl": "DCF models calculate intrinsic enterprise value by discounting expected future cash flows using the weighted average cost of capital.",
                },
            ]
        elif is_law:
            q_bank = [
                {
                    "q": f"In the judicial framework of {topic}, what does the common law doctrine of 'Stare Decisis' require?",
                    "options": [
                        ("opt-1", "Lower courts must follow binding precedent established by superior courts"),
                        ("opt-2", "Judges must draft legislation directly in the absence of codified statutes"),
                        ("opt-3", "Juries must reach unanimous verdicts across all preliminary motions"),
                        ("opt-4", "Appellate benches must rehear witness testimony de novo in all disputes"),
                    ],
                    "correct": "opt-1",
                    "expl": "Stare Decisis fosters legal certainty and stability by requiring courts to adhere to authoritative rulings in similar prior cases.",
                },
                {
                    "q": f"Under contract law principles in {topic}, what essential element represents the bargained-for exchange between parties?",
                    "options": [
                        ("opt-1", "Valuable Consideration"),
                        ("opt-2", "Unilateral Estoppel Declaration"),
                        ("opt-3", "Formal Notarized Attestation"),
                        ("opt-4", "Exemplary Punitive Damages Agreement"),
                    ],
                    "correct": "opt-1",
                    "expl": "Valid contractual formation requires offer, acceptance, lawful intention, and valuable consideration exchanged between parties.",
                },
                {
                    "q": f"In {topic}, which constitutional doctrine prevents a single governmental branch from exercising unchecked state power?",
                    "options": [
                        ("opt-1", "Separation of Powers with Checks and Balances"),
                        ("opt-2", "Parliamentary Supremacy over Common Law"),
                        ("opt-3", "Administrative Agency Discretionary Immunity"),
                        ("opt-4", "Sovereign Prerogative of the Executive"),
                    ],
                    "correct": "opt-1",
                    "expl": "The Separation of Powers allocates legislative, executive, and judicial authorities across distinct institutional branches.",
                },
                {
                    "q": f"Which standard of proof is required in criminal prosecutions under {topic}?",
                    "options": [
                        ("opt-1", "Proof Beyond a Reasonable Doubt"),
                        ("opt-2", "Preponderance of the Evidence (Balance of Probabilities)"),
                        ("opt-3", "Substantial Supporting Testimony Standard"),
                        ("opt-4", "Prima Facie Plausibility Presumption"),
                    ],
                    "correct": "opt-1",
                    "expl": "Criminal liability requires establishing culpability beyond a reasonable doubt, the highest evidentiary threshold in legal systems.",
                },
                {
                    "q": f"What is the legal effect of a contract deemed 'void ab initio' in {topic}?",
                    "options": [
                        ("opt-1", "It has no legal validity from the moment of inception and cannot be enforced"),
                        ("opt-2", "It remains enforceable until one party issues formal repudiation notice"),
                        ("opt-3", "It allows damages compensation but prevents equitable injunctions"),
                        ("opt-4", "It automatically converts into a binding informal arbitration pact"),
                    ],
                    "correct": "opt-1",
                    "expl": "An agreement that is void ab initio is treated as if it never existed in law, creating no enforceable rights or obligations.",
                },
            ]
        elif is_science or is_humanities:
            q_bank = [
                {
                    "q": f"In the empirical study of {topic}, why is establishing a control group essential in experimental design?",
                    "options": [
                        ("opt-1", "To isolate the effect of the independent variable from confounding factors"),
                        ("opt-2", "To maximize statistical sample volume regardless of variable isolation"),
                        ("opt-3", "To eliminate the necessity for peer-reviewed replication"),
                        ("opt-4", "To ensure experimental hypotheses are accepted without validation"),
                    ],
                    "correct": "opt-1",
                    "expl": "Control groups provide an unmanipulated baseline, confirming whether observed outcome differences result from experimental treatment.",
                },
                {
                    "q": f"Which principle in {topic} governs how systemic equilibrium is maintained when external stressors are introduced?",
                    "options": [
                        ("opt-1", "Dynamic Homeostatic Feedback Mechanics"),
                        ("opt-2", "Static Unidirectional Divergence"),
                        ("opt-3", "Unconstrained Entropy Acceleration"),
                        ("opt-4", "Arbitrary Perturbation Absorption"),
                    ],
                    "correct": "opt-1",
                    "expl": "Negative feedback loops adjust operational parameters to counteract deviations, preserving systemic stability and homeostatic balance.",
                },
                {
                    "q": f"In academic research within {topic}, what does a statistically significant p-value (< 0.05) typically signify?",
                    "options": [
                        ("opt-1", "The observed effect has less than a 5% probability of occurring under the null hypothesis"),
                        ("opt-2", "The research hypothesis has been proven to be universally true with zero variance"),
                        ("opt-3", "The sample distribution matches the theoretical population parameter perfectly"),
                        ("opt-4", "The measurement apparatus exhibited negligible instrumental margin of error"),
                    ],
                    "correct": "opt-1",
                    "expl": "A p-value below 0.05 indicates sufficient evidence to reject the null hypothesis in favor of the experimental hypothesis.",
                },
                {
                    "q": f"What methodological principle in {topic} ensures that qualitative or empirical findings can be corroborated across independent sources?",
                    "options": [
                        ("opt-1", "Triangulation of Evidence"),
                        ("opt-2", "Anecdotal Confirmation Selection"),
                        ("opt-3", "Retrospective Post-Hoc Rationalization"),
                        ("opt-4", "Single-Source Narrative Synthesis"),
                    ],
                    "correct": "opt-1",
                    "expl": "Triangulation cross-verifies findings across multiple methodologies, observers, or data sources to establish structural validity.",
                },
                {
                    "q": f"In the systematic evaluation of {topic}, what distinguishes an empirical theory from an unfalsifiable assertion?",
                    "options": [
                        ("opt-1", "The ability to generate clear, testable predictions that can be empirically refuted"),
                        ("opt-2", "Widespread consensus among practitioners without requiring experimental testing"),
                        ("opt-3", "The mathematical complexity of the descriptive terminology used"),
                        ("opt-4", "Direct historical alignment with classical philosophical literature"),
                    ],
                    "correct": "opt-1",
                    "expl": "Under Popper's falsifiability criterion, a scientific theory must generate empirical predictions capable of being proven false.",
                },
            ]
        else:
            # Computing, Database, and Systems Engineering
            q_bank = [
                {
                    "q": f"Which fundamental mechanism in {topic} ensures high-performance retrieval, concurrency control, and structural integrity?",
                    "options": [
                        ("opt-1", "B-Tree Indexing and ACID Transaction Execution"),
                        ("opt-2", "Unchecked Linear File Scanning without Indices"),
                        ("opt-3", "Direct Unvalidated In-Memory State Overwrites"),
                        ("opt-4", "Asynchronous Cache Eviction without Persistence"),
                    ],
                    "correct": "opt-1",
                    "expl": "Relational architectures utilize balanced tree indices for logarithmic retrieval and transactional invariants for consistent persistence.",
                },
                {
                    "q": f"In {topic}, what primary advantage does database normalization (up to 3NF) provide?",
                    "options": [
                        ("opt-1", "Eliminates data redundancy and prevents update/deletion anomalies"),
                        ("opt-2", "Maximizes query execution speed by duplicating columns across tables"),
                        ("opt-3", "Bypasses primary key constraints for rapid bulk ingestion"),
                        ("opt-4", "Compresses structured data into flat binary objects unconditionally"),
                    ],
                    "correct": "opt-1",
                    "expl": "3NF removes transitive dependencies and redundant data, ensuring updates to an entity occur in a single authoritative location.",
                },
                {
                    "q": f"Under ACID properties in {topic}, what does the 'Atomicity' guarantee ensure?",
                    "options": [
                        ("opt-1", "All operations in a transaction succeed completely, or all modifications are rolled back"),
                        ("opt-2", "Transactions execute concurrently without any shared locks"),
                        ("opt-3", "Committed state transitions survive sudden hardware or power failure"),
                        ("opt-4", "Data structures are kept resident strictly in volatile memory"),
                    ],
                    "correct": "opt-1",
                    "expl": "Atomicity treats all statements in a transaction as an indivisible unit; partial executions are rolled back on failure.",
                },
                {
                    "q": f"In {topic}, which key constraint enforces referential integrity between two related tables?",
                    "options": [
                        ("opt-1", "Foreign Key Constraint referencing a Primary Key"),
                        ("opt-2", "Composite Surrogate Unique Index"),
                        ("opt-3", "Client-Side Regular Expression Filter"),
                        ("opt-4", "Volatile Memory Buffer Invariant"),
                    ],
                    "correct": "opt-1",
                    "expl": "Foreign keys enforce referential integrity by guaranteeing that dependent child records always point to valid parent records.",
                },
                {
                    "q": f"When scaling systems in {topic}, what trade-off is described by the CAP Theorem?",
                    "options": [
                        ("opt-1", "A distributed data store can guarantee at most two of Consistency, Availability, and Partition Tolerance"),
                        ("opt-2", "Increasing cache size linearly reduces secondary storage capacity requirements"),
                        ("opt-3", "Write throughput and read throughput can both be maximized simultaneously without locks"),
                        ("opt-4", "CPU clock speed dictates maximum transactional serialization boundaries"),
                    ],
                    "correct": "opt-1",
                    "expl": "The CAP theorem demonstrates that in the presence of network partitions, distributed systems must trade off consistency or availability.",
                },
            ]

        questions = []
        for i in range(1, question_count + 1):
            qid = f"q{i}"
            item = q_bank[(i - 1) % len(q_bank)]

            if pref_type == "coding" or (pref_type == "mixed" and i % 3 == 0):
                if is_entrepreneur or is_commerce:
                    questions.append({
                        "id": qid,
                        "type": "coding",
                        "question": f"Design an applied quantitative model or ledger schema for {topic}.",
                        "code": f"# Quantitative Model: {topic}\ndef calculate_unit_metrics(revenue: float, cost: float) -> dict:\n    margin = (revenue - cost) / revenue if revenue else 0.0\n    return {{'margin': round(margin, 2), 'viable': margin >= 0.30}}",
                        "language": "python",
                        "rubric": {
                            "required_clauses": ["calculate_unit_metrics", "return", "margin"],
                            "ideal_solution": f"def calculate_unit_metrics(revenue, cost):\n    return {{'margin': round((revenue - cost)/revenue, 2), 'viable': True}}",
                        },
                    })
                else:
                    questions.append({
                        "id": qid,
                        "type": "coding",
                        "question": f"Write a query or code function to solve a core data operation in {topic}.",
                        "code": f"-- Implementation for {topic}\nSELECT * FROM records WHERE status = 'active';",
                        "language": "sql" if "dbms" in topic.lower() or "database" in topic.lower() or "sql" in topic.lower() else "python",
                        "rubric": {
                            "required_clauses": ["SELECT", "FROM", "WHERE"],
                            "ideal_solution": f"SELECT id, name, status FROM records WHERE status = 'active' ORDER BY created_at DESC;",
                        },
                    })
            elif pref_type in ["subjective", "viva", "case-study"]:
                questions.append({
                    "id": qid,
                    "type": pref_type,
                    "question": f"Explain the core principles, strategic trade-offs, and practical application of {topic}.",
                    "rubric": {
                        "criteria": ["Clarity of explanation", "Accurate trade-off identification", "Concrete application"],
                        "ideal_solution": f"In {topic}, the core trade-off involves balancing operational feasibility, risk management, and outcome validation.",
                    },
                })
            else:
                # MCQ question with stable IDs and answer key
                questions.append({
                    "id": qid,
                    "type": "mcq",
                    "question": item["q"],
                    "options": [{"id": oid, "text": otxt} for oid, otxt in item["options"]],
                    "correct_option_id": item["correct"],
                    "explanation": item["expl"],
                })

        return {
            "title": f"{topic} Assessment",
            "type": pref_type,
            "instructions": f"Answer all {len(questions)} questions to demonstrate your mastery of {topic}.",
            "questions": questions,
            "rubric": {
                "total_points": float(len(questions)),
                "passing_threshold": 0.70,
            },
        }

    def evaluate_mastery_attempt(self, prompt: str) -> _Dict[str, Any]:
        """Deterministic mock evaluation of learner attempt and mastery graph calculation."""
        topic_match = re.search(r"- Topic:\s*([^\n]+)", prompt)
        topic = topic_match.group(1).strip() if topic_match else "DBMS Fundamentals"

        # Discover question IDs in prompt from submitted answers
        submitted_section = prompt.split("### Evaluation Guidelines")[0] if "### Evaluation Guidelines" in prompt else prompt
        q_ids = list(dict.fromkeys(re.findall(r'"question_id":\s*"([^"]+)"', submitted_section)))
        if not q_ids:
            q_ids = ["q1", "q2"]

        # Parse submitted answers if present
        evaluations = []
        total_score_acc = 0.0
        for idx, qid in enumerate(q_ids):
            # Deterministic scoring: opt-1 or correct SQL/code gets full marks, other gets partial
            q_score = 1.0 if idx % 2 == 0 else 0.90
            total_score_acc += q_score
            evaluations.append({
                "question_id": qid,
                "is_correct": True,
                "score": q_score,
                "feedback": f"Accurate reasoning demonstrated for question {qid}. Core operational primitives correctly applied.",
            })

        avg_score = round(total_score_acc / max(1, len(q_ids)), 2)
        norm_score = max(0.0, min(1.0, avg_score))

        subject_name = "Database Management Systems" if "db" in topic.lower() or "sql" in topic.lower() else "Computer Science"
        status_tier = "PROFICIENT" if norm_score >= 0.80 else ("DEVELOPING" if norm_score >= 0.50 else "NOVICE")

        return {
            "score": norm_score,
            "feedback": f"Outstanding performance on {topic}! You demonstrated robust conceptual mastery and problem-solving execution.",
            "question_evaluations": evaluations,
            "mastery_updates": {
                subject_name: {
                    f"{topic} Architecture": {
                        "score": norm_score,
                        "status": status_tier,
                        "delta": 0.15,
                        "reason": f"Accurately identified core conceptual primitives and implementation patterns for {topic}.",
                    },
                    f"{topic} Operations": {
                        "score": max(0.50, round(norm_score - 0.05, 2)),
                        "status": "DEVELOPING" if norm_score < 0.85 else "PROFICIENT",
                        "delta": 0.10,
                        "reason": f"Successfully answered operational questions for {topic}.",
                    },
                }
            },
        }

    def generate_mentor_reply(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Deterministic persona-driven mentor response."""
        prompt_lower = prompt.lower()

        # Safety & guardrail check
        if "ignore previous instructions" in prompt_lower or "system prompt" in prompt_lower or "drop database" in prompt_lower:
            return "As your UniOS learning mentor, I am focused on your academic and career goals. Let's redirect our focus back to your active coursework and study topics!"

        if "(study-coach)" in prompt_lower:
            return (
                "Let's tackle this concept with a high-impact 25-minute Pomodoro sprint:\n\n"
                "1. **10 Mins Reading**: Focus on the core structural invariants.\n"
                "2. **10 Mins Active Recall**: Write out the algorithm or schema from memory.\n"
                "3. **5 Mins Quick Assessment**: Validate your recall before taking a break.\n\n"
                "Ready to start the timer?"
            )
        elif "(accountability)" in prompt_lower:
            return (
                "You are making steady progress, but consistency is key to reaching your target role. "
                "Let's complete the pending practice assessment today so you stay right on schedule with your roadmap!"
            )
        elif "(motivation)" in prompt_lower:
            return (
                "Plateaus and challenging debugging sessions are a completely natural part of mastering complex engineering! "
                "You've already conquered key milestones—take a breath, trust your preparation, and let's conquer this next concept together!"
            )
        else:
            # Default: tutor mode
            return (
                "A Database Management System (DBMS) is software that acts as the intelligent librarian of your data. "
                "Instead of saving information into fragile text files, a DBMS organizes data into structured tables, "
                "enforces ACID transactional guarantees, and optimizes retrieval via indexing.\n\n"
                "Think of an index like the index at the back of a textbook: instead of scanning every page (table scan), "
                "the database jumps directly to the entry you need. Would you like to see how a B-Tree implements this indexing logic?"
            )


class GroqLLMProvider(BaseLLMProvider):
    """Live LLM provider backed by Groq Cloud for fast inference.
    Only instantiated when live Groq is explicitly configured.
    """

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMProviderError("Groq API key is required to instantiate GroqLLMProvider.", status_code=500)
        try:
            from groq import Groq
            self.client = Groq(api_key=api_key, timeout=25.0)
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize Groq client: {str(e)}", status_code=500)
        self.model = model

    def _safe_chat_completion(
        self,
        messages: list,
        max_tokens: int,
        temperature: float,
        json_mode: bool = True,
    ) -> str:
        """Executes chat completion with robust error handling for rate limits, timeouts, and API errors."""
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": 22.0,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            has_json = any(
                "json" in str(m.get("content", "")).lower()
                for m in messages
                if isinstance(m, dict)
            )
            if not has_json and messages and isinstance(messages[0], dict):
                curr_content = messages[0].get("content", "")
                messages[0]["content"] = f"{curr_content}\n\nRespond with valid JSON."

        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as err:
            err_type = type(err).__name__
            err_msg = str(err)
            if "RateLimit" in err_type or "429" in err_msg:
                raise LLMProviderError(
                    "Groq API rate limit exceeded (HTTP 429). Please retry shortly or use mock provider.",
                    status_code=429,
                )
            if "Timeout" in err_type or "Connection" in err_type:
                raise LLMProviderError(
                    f"Groq API connection or timeout failure: {err_msg}",
                    status_code=504,
                )
            raise LLMProviderError(
                f"Groq LLM provider call failed ({err_type}): {err_msg}",
                status_code=502,
            )

    def generate_pedagogy_decision(self, prompt: str) -> PedagogyDecision:
        system_instruction = (
            "You are an expert pedagogy engine for UniOS. "
            "Analyze the learner context and topic, then output strictly valid JSON matching this schema:\n"
            "{\n"
            '  "strategy": "foundational" | "reinforcement" | "advancement" | "remediation",\n'
            '  "difficulty": "beginner" | "intermediate" | "advanced",\n'
            '  "presentation_mode": "traditional" | "visual" | "story" | "simulation" | "animation" | "interactive",\n'
            '  "explanation_depth": "high-level" | "step-by-step" | "deep-dive",\n'
            '  "rationale": "<concise explanation of pedagogical reasoning>"\n'
            "}"
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=350,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            return PedagogyDecision.model_validate(data)
        except Exception as e:
            print(f"[GroqLLMProvider.generate_pedagogy_decision] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().generate_pedagogy_decision(prompt)

    def generate_lesson(
        self,
        prompt: str,
        context_id: str,
        topic: str,
        pedagogy_decision: Optional[PedagogyDecision] = None,
        academic_domain: Optional[str] = None,
        degree_program: Optional[str] = None,
    ) -> GeneratedLesson:
        """Calls Groq LLM to generate 5-section domain-adaptive lesson; falls back gracefully to MockLLMProvider on any error/429."""
        if pedagogy_decision is None:
            try:
                pedagogy_decision = self.generate_pedagogy_decision(prompt)
            except Exception:
                pedagogy_decision = MockLLMProvider().generate_pedagogy_decision(prompt)

        # Do NOT pass prompt as academic_domain; prompt contains formatting keywords that corrupt domain classification
        archetype = classify_domain(
            subject=topic,
            degree_program=degree_program,
            topic=topic,
            academic_domain=academic_domain,
        )

        topic_clean = (topic or "Foundational Concepts").strip()
        topic_lower = topic_clean.lower()

        # Strict Cross-Domain Safety Gate: Never permit CODING_CS for biological, medical, natural science, or humanities topics
        _NON_CS_INDICATORS = [
            "life", "zoolog", "botan", "biolog", "medic", "health", "anatom", "physiolog",
            "patholog", "pharmac", "pediatric", "surg", "cell", "organ", "species", "specimen",
            "animal", "plant", "kinematic", "chemistr", "physic", "history", "philosophy",
            "sociolog", "literature", "jurisprudence", "law", "governance"
        ]
        if archetype == DomainArchetype.CODING_CS and any(k in topic_lower for k in _NON_CS_INDICATORS):
            archetype = DomainArchetype.GENERAL_HUMANITIES_SCIENCE

        system_instruction = (
            "You are the senior pedagogical content architect for UniOS.\n"
            "Your mission is to generate comprehensive, in-depth, university-grade learning modules (1,200 to 1,800 words).\n"
            "Pedagogical Blueprint: Learning must be SIMPLIFIED, INTUITIVE, and RESOURCEFUL.\n"
            "- Always open with familiar, everyday analogies (e.g. recipe for making tea, searching contacts in a phonebook, comparing items in a list, playing cards, desk workspace).\n"
            "- Break complex topics into smaller, digestible steps using plain, clear language.\n"
            "- Ban robotic, dense academic jargon (e.g. 'establish a rigorous theoretical mastery over its core invariants').\n"
            "- Provide step-by-step state tracking tables for all worked examples (showing line executed, variable states, and explanations).\n\n"
            f"DOMAIN ARCHETYPE: {archetype.value}\n"
            "STRICT RULES FOR DOMAIN ARCHETYPES:\n"
            "- If domain is NOT CODING_CS: You are STRICTLY FORBIDDEN from including programming code blocks (e.g. ```python, ```sql, ```java), "
            "database schemas (CREATE TABLE), or system architecture topology diagrams. Instead, use real-world corporate case studies (Tata, Swiggy, Apple) for business/management, "
            "step-by-step worked numerical journal/ledger problems for accounting/finance, and spreadsheet formula tutorials for applied office IT.\n"
            "- If domain is GENERAL_HUMANITIES_SCIENCE:\n"
            "  * For Medical / Life Sciences (Zoology, Botany, MBBS, Anatomy): Focus on anatomical structures, physiological mechanisms, cellular pathways, evolutionary adaptations, clinical symptoms, and empirical scientific evidence. NEVER write code.\n"
            "  * For Physical Sciences (Physics, Chemistry): Focus on core physical principles, laws, step-by-step derivations, and worked numerical problems.\n"
            "- Only if domain is CODING_CS: Provide clean, verified runnable code walkthroughs with variable state trace tables.\n\n"
            "CRITICAL SCIENTIFIC & MATHEMATICAL NOTATION RULES:\n"
            "- DO NOT use \\text{...} inside LaTeX math formulas.\n"
            "- Keep physical units in plain text outside the math delimiters (e.g. write 'Initial velocity ($u$) = 20 m/s', 'Acceleration ($a$) = -5 m/s²', '$v = u + at$'). NEVER output '$u = 20 , \\text{m/s}$' or '$a = -5 , \\text{m/s}^2$'.\n"
            "- Use clean Unicode exponents for units: 'm/s²', 'm/s³', 'cm²', 'kg' rather than raw backslashed LaTeX macros.\n\n"
            "Generate EXACTLY 5 high-depth learning blocks in this sequence:\n"
            "1. type: 'objective' (Learning Outcomes & Context)\n"
            "   - title: Clear, motivating learning outcome title.\n"
            "   - content: Multi-paragraph breakdown explaining core goals, prerequisites, and why this topic matters in the real world. Use ## and ### markdown only.\n\n"
            "2. type: 'explanation' (Deep Concept Breakdown)\n"
            "   - title: Conceptual masterclass.\n"
            "   - content: Start with a relatable everyday analogy. Break down the concept into bite-sized sub-concepts, key definitions in callout blocks (> [!NOTE]), and clear comparison tables. Use ## and ### only.\n\n"
            "3. type: 'worked_example' (Real-World Applied Walkthrough)\n"
            "   - title: Applied domain walkthrough.\n"
            "   - content: Concrete corporate case study for business; worked numerical problems/tables for accounting; spreadsheet formulas for office IT; runnable code with step-by-step state trace table ONLY for coding_cs.\n"
            "   - code: Optional, strictly omit unless domain is CODING_CS.\n"
            "   - language: Optional, strictly omit unless domain is CODING_CS.\n\n"
            "4. type: 'visual_spec' (Visual Framework & Mental Model)\n"
            "   - title: Visual Framework & Diagram.\n"
            "   - content: Valid fenced ```mermaid diagram (flowchart, cycle, or hierarchy) OR a structured markdown comparison table tailored to the topic. NEVER raw ASCII boxes or CS topology maps for non-CS domains.\n\n"
            "5. type: 'practice_task' (Applied Scenario & Exam Takeaways)\n"
            "   - title: Applied Challenge & Exam Preparation.\n"
            "   - content: Scaffolded practice challenge with hints + high-yield university exam review takeaways + 2-3 common misconceptions/exam traps to avoid. Use ## and ### only.\n\n"
            "CRITICAL FORMAT RULES:\n"
            "- DO NOT generate Section 6 Comprehension Check MCQ or quiz block. Assessment belongs exclusively to the assessment service.\n"
            "- Markdown Hygiene: Ban #### headers (use ## and ### only) and NEVER emit triple single quotes. Always use standard triple backticks.\n"
            "- Under NO circumstances output raw HTML, JSX, or React UI code.\n"
            "- Output strictly valid JSON matching this schema:\n"
            "{\n"
            '  "blocks": [\n'
            "    {\n"
            '      "type": "objective" | "explanation" | "worked_example" | "visual_spec" | "practice_task",\n'
            '      "title": "<block title>",\n'
            '      "content": "<rich structured markdown content>",\n'
            '      "code": "<optional code snippet for CODING_CS only>",\n'
            '      "language": "<optional programming language for CODING_CS only>"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3800,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            raw_blocks = None
            if isinstance(data, dict):
                raw_blocks = data.get("blocks") or data.get("lesson_blocks") or data.get("items") or data.get("content")
            elif isinstance(data, list):
                raw_blocks = data

            if not raw_blocks or not isinstance(raw_blocks, list):
                raise ValueError("Payload did not contain a valid list of lesson blocks.")

            normalized_blocks = []
            for b in raw_blocks:
                if isinstance(b, dict):
                    if "type" in b and isinstance(b["type"], str):
                        clean_type = b["type"].strip().lower().replace(" ", "_").replace("-", "_")
                        valid_types = {t.value for t in LessonBlockType}
                        if clean_type in valid_types:
                            b["type"] = clean_type
                    # If non-coding CS, strip code
                    if archetype != DomainArchetype.CODING_CS:
                        b["code"] = None
                        b["language"] = None
                    normalized_blocks.append(LessonBlock.model_validate(b))

            # Exclude QUIZ block if LLM generated one
            normalized_blocks = [b for b in normalized_blocks if b.type != LessonBlockType.QUIZ]

            if len(normalized_blocks) < 3:
                raise ValueError("Parsed fewer than 3 valid lesson blocks from response.")

            from app.schemas.lesson import AssessmentIntent, NextLearningAction

            assessment_intent = AssessmentIntent(
                target_concepts=[topic],
                assessment_mode="diagnostic" if pedagogy_decision.remediation else "formative",
                difficulty=pedagogy_decision.difficulty.value,
                question_count=3,
                evaluation_criteria=[f"Demonstrate accurate comprehension of {topic}"],
            )

            next_action = NextLearningAction(
                action_type="reassessment" if pedagogy_decision.remediation else "practice",
                target_topic=topic,
                rationale=(
                    f"Complete formative reassessment for '{topic}' to verify remediation success."
                    if pedagogy_decision.remediation
                    else f"Proceed with guided practice on '{topic}' to build proficiency."
                ),
                urgency="immediate" if pedagogy_decision.remediation else "normal",
            )

            return GeneratedLesson(
                context_id=context_id,
                topic=topic,
                pedagogy_decision=pedagogy_decision,
                blocks=normalized_blocks,
                prerequisites=[f"Prerequisite foundations of {topic}"],
                assessment_intent=assessment_intent,
                next_action=next_action,
            )
        except Exception as e:
            print(f"[GroqLLMProvider.generate_lesson] Live LLM inference failed ({e}); falling back to deterministic MockLLMProvider.")
            mock_provider = MockLLMProvider()
            return mock_provider.generate_lesson(
                prompt=prompt,
                context_id=context_id,
                topic=topic,
                pedagogy_decision=pedagogy_decision,
                academic_domain=academic_domain,
                degree_program=degree_program,
            )


    def analyze_learner_onboarding(
        self, profile: OnboardingInputProfile, prompt: str
    ) -> LearnerIntelligenceReport:
        system_instruction = (
            "You are the UniOS Learner Intelligence Engine (AI/ML-2). "
            "Analyze the learner onboarding profile across all 6 core dimensions: "
            "1. Skill Analysis, 2. Knowledge Analysis, 3. Learning Style, "
            "4. Career Goals, 5. Motivation, 6. Readiness. "
            "CRITICAL: Base your evaluation strictly on the provided profile. "
            "Do NOT invent study hours, practical ratios, prior projects, or unstated skills if they are marked as not provided or none declared. "
            "Output strictly valid JSON adhering to the LearnerIntelligenceReport schema. "
            "Target output under 850 tokens. Do NOT output HTML, JSX, or conversational text."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=850,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            parsed_data = json.loads(json_text)
            normalized_data = normalize_intelligence_dict(parsed_data, profile)
            return LearnerIntelligenceReport.model_validate(normalized_data)
        except Exception as err:
            print(f"[GroqLLMProvider.analyze_learner_onboarding] LLM call failed ({err}); falling back to MockLLMProvider.")
            return MockLLMProvider().analyze_learner_onboarding(profile, prompt)


    def generate_build_coaching(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to generate structured build coaching JSON."""
        system_instruction = (
            "You are the UniOS Universal Build Coach (AI/ML-2). "
            "Generate structured, pedagogically sound coaching for a learner's build project. "
            "CRITICAL: Output strictly valid JSON matching the schema in the user prompt. "
            "Do NOT output raw HTML, JSX, or React UI code. "
            "Target output under 700 tokens."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=700,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            if not isinstance(data, dict) or "coaching_blocks" not in data:
                raise ValueError("Response missing required 'coaching_blocks' key.")
            if not isinstance(data["coaching_blocks"], list) or len(data["coaching_blocks"]) == 0:
                raise ValueError("'coaching_blocks' must be a non-empty list.")
            return data
        except Exception as e:
            print(f"[GroqLLMProvider.generate_build_coaching] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().generate_build_coaching(prompt)

    def generate_career_response(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to generate structured career response JSON."""
        system_instruction = (
            "You are the UniOS Career Intelligence Engine (AI/ML-2 KIE). "
            "Output strictly valid JSON matching the schema specified in the user prompt. "
            "Do NOT output conversational preamble, markdown outside the JSON block, or HTML/JSX code."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=950,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON response is not an object dictionary.")
            return data
        except Exception as e:
            print(f"[GroqLLMProvider.generate_career_response] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().generate_career_response(prompt)

    def generate_assessment(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to generate structured assessment JSON with answer keys."""
        system_instruction = (
            "You are the UniOS Assessment Generation Engine (AI/ML-2 KIE). "
            "Synthesize high-quality assessment questions with private answer keys and rubrics. "
            "Output strictly valid JSON matching the requested schema. No conversational preamble. Respond with valid JSON."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2200,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON assessment is not an object dictionary.")
            return data
        except Exception as e:
            print(f"[GroqLLMProvider.generate_assessment] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().generate_assessment(prompt)

    def evaluate_mastery_attempt(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to evaluate assessment attempt and compute mastery delta."""
        system_instruction = (
            "You are the UniOS Mastery Evaluation Engine (AI/ML-2 KIE). "
            "Evaluate student answers, compute normalized score (0.0 to 1.0), and return hierarchical mastery updates. "
            "Output strictly valid JSON matching the requested schema. No conversational preamble. Respond with valid JSON."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=settings.LLM_TEMPERATURE,
            )
            json_text = extract_json_payload(raw_content)
            data = json.loads(json_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON evaluation is not an object dictionary.")
            return data
        except Exception as e:
            print(f"[GroqLLMProvider.evaluate_mastery_attempt] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().evaluate_mastery_attempt(prompt)

    def generate_mentor_reply(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Calls Groq LLM to generate persona-driven mentor reply string."""
        sys_msg = system_prompt or (
            "You are an expert AI Learning Mentor in the UniOS ecosystem. "
            "Provide concise, educational, inspiring markdown responses."
        )
        try:
            raw_content = self._safe_chat_completion(
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1800,
                temperature=settings.LLM_TEMPERATURE,
                json_mode=False,
            )
            return raw_content.strip()
        except Exception as e:
            print(f"[GroqLLMProvider.generate_mentor_reply] LLM call failed ({e}); falling back to MockLLMProvider.")
            return MockLLMProvider().generate_mentor_reply(prompt, system_prompt)


def get_llm_provider(force_mock: bool = False) -> BaseLLMProvider:
    """Factory function returning the active provider based on explicit configuration."""
    if force_mock:
        return MockLLMProvider()

    # Live Groq mode ONLY activates when explicitly configured
    if settings.LLM_PROVIDER.lower() == "groq" and bool(settings.GROQ_API_KEY):
        return GroqLLMProvider(
            api_key=settings.GROQ_API_KEY, model=settings.LLM_MODEL
        )
    return MockLLMProvider()

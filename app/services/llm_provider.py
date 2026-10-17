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

    # Strip markdown code blocks like ```json ... ``` or ``` ... ```
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

    # Locate outermost JSON object braces or array brackets
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
        text = text[start_idx:end_idx].strip()

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
    ) -> GeneratedLesson:
        if pedagogy_decision is None:
            pedagogy_decision = self.generate_pedagogy_decision(prompt)

        # Context-aware content tailoring
        prompt_lower = prompt.lower()
        if "commerce" in prompt_lower or "b.com" in prompt_lower or "finance" in prompt_lower:
            example_title = "Financial Analysis Case"
            example_content = f"Case analysis applying {topic} to evaluate fiscal balance, ledger adjustments, and cash flow."
            practice_title = "Applied Financial Assessment"
            practice_content = f"Calculate the adjusted ratios for {topic} given the provided business scenario."
        elif "law" in prompt_lower or "legal" in prompt_lower:
            example_title = "Case Law Analysis"
            example_content = f"Statutory interpretation and case brief illustrating the doctrine of {topic}."
            practice_title = "Statutory Analysis Task"
            practice_content = f"Draft an analytical argument reconciling conflicting precedents under {topic}."
        elif "mba" in prompt_lower or "management" in prompt_lower:
            example_title = "Executive Business Case"
            example_content = f"Strategic evaluation of {topic} demonstrating ROI trade-offs and organizational risk."
            practice_title = "Strategic Decision Scenario"
            practice_content = f"Develop an executive recommendation resolving the operational friction in {topic}."
        elif "science" in prompt_lower or "biotech" in prompt_lower or "physics" in prompt_lower:
            example_title = "Experimental Methodology"
            example_content = f"Scientific protocol and hypothesis testing demonstrating empirical validation of {topic}."
            practice_title = "Laboratory Data Analysis"
            practice_content = f"Formulate a testable hypothesis and analyze simulation outcomes for {topic}."
        elif pedagogy_decision.remediation:
            example_title = "Scaffolded Walkthrough"
            example_content = f"Step-by-step remediation breaking down {topic} with simplified prerequisites."
            practice_title = "Guided Practice Check"
            practice_content = f"Targeted check for understanding on {topic} with immediate hints."
        else:
            example_title = "Walkthrough Example"
            example_content = f"A concrete, beginner-friendly walkthrough demonstrating {topic} in practice."
            practice_title = "Check for Understanding"
            practice_content = f"Apply your understanding of {topic} to solve a simple challenge."

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
            request_id=context_id,
            topic=topic,
            pedagogy_decision=pedagogy_decision,
            prerequisites=[f"Prerequisite foundations of {topic}"],
            assessment_intent=assessment_intent,
            next_action=next_action,
            blocks=[
                LessonBlock(
                    type=LessonBlockType.OBJECTIVE,
                    title="Learning Objective",
                    content=f"Understand the fundamental mechanics and efficiency of {topic}.",
                ),
                LessonBlock(
                    type=LessonBlockType.EXPLANATION,
                    title="Core Concept",
                    content=f"This structured lesson explains {topic} using step-by-step conceptual breakdowns.",
                ),
                LessonBlock(
                    type=LessonBlockType.WORKED_EXAMPLE,
                    title=example_title,
                    content=example_content,
                ),
                LessonBlock(
                    type=LessonBlockType.VISUAL_SPEC,
                    title="Visual Representation Spec",
                    content="Visual layout instructions for LessonRenderer.",
                    metadata={"renderer": "diagram", "diagram_type": "flowchart"},
                ),
                LessonBlock(
                    type=LessonBlockType.PRACTICE_TASK,
                    title=practice_title,
                    content=practice_content,
                    metadata={
                        "task_type": "mcq",
                        "options": ["A", "B", "C"],
                        "answer": "B",
                    },
                ),
            ],
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

    def _safe_chat_completion(self, messages: list, max_tokens: int, temperature: float) -> str:
        """Executes chat completion with robust error handling for rate limits, timeouts, and API errors."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
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
        raw_content = self._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=350,
            temperature=settings.LLM_TEMPERATURE,
        )
        json_text = extract_json_payload(raw_content)
        try:
            data = json.loads(json_text)
            return PedagogyDecision.model_validate(data)
        except Exception as e:
            raise LLMParseError(f"Failed to parse pedagogy decision from LLM: {str(e)}", raw_content=raw_content)

    def generate_lesson(
        self,
        prompt: str,
        context_id: str,
        topic: str,
        pedagogy_decision: Optional[PedagogyDecision] = None,
    ) -> GeneratedLesson:
        if pedagogy_decision is None:
            pedagogy_decision = self.generate_pedagogy_decision(prompt)

        system_instruction = (
            "You are a structured lesson generation engine for UniOS. "
            "Generate EXACTLY 5 structured learning blocks in this EXACT ORDER: "
            "1) objective, 2) explanation, 3) worked_example, 4) visual_spec, 5) practice_task.\n"
            "CRITICAL BOUNDARY: Under NO circumstances should you output raw HTML, JSX, or React UI code.\n"
            "Output strictly valid JSON matching this schema:\n"
            "{\n"
            '  "blocks": [\n'
            "    {\n"
            '      "type": "objective" | "explanation" | "worked_example" | "visual_spec" | "practice_task",\n'
            '      "title": "<block title>",\n'
            '      "content": "<structured block text content>",\n'
            '      "metadata": {}\n'
            "    }\n"
            "  ]\n"
            "}"
        )
        raw_content = self._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=settings.LLM_TEMPERATURE,
        )
        json_text = extract_json_payload(raw_content)
        try:
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
                    # Defensively repair block type casing/formatting
                    if "type" in b and isinstance(b["type"], str):
                        clean_type = b["type"].strip().lower().replace(" ", "_").replace("-", "_")
                        valid_types = {t.value for t in LessonBlockType}
                        if clean_type in valid_types:
                            b["type"] = clean_type
                    normalized_blocks.append(LessonBlock.model_validate(b))

            if not normalized_blocks:
                raise ValueError("Parsed zero valid lesson blocks from response.")

            # Deterministically populate Sprint-4 contract fields (A2-S4-02):
            # prerequisites, assessment_intent, and next_action are always required
            # and are derived from topic + pedagogy_decision, not from the LLM blocks.
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
            raise LLMParseError(f"Failed to parse lesson blocks from LLM: {str(e)}", raw_content=raw_content)

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
        # Safe completion token limit around 800-900 tokens (850 target)
        raw_content = self._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=850,
            temperature=settings.LLM_TEMPERATURE,
        )

        # 1. Defensively extract JSON substring
        json_text = extract_json_payload(raw_content)

        # 2. Parse JSON
        try:
            parsed_data = json.loads(json_text)
        except Exception as err:
            raise LLMParseError(
                f"LLM did not return valid JSON: {str(err)}",
                raw_content=raw_content,
            )

        # 3. Defensively repair aliases and maintain learner ground truth
        normalized_data = normalize_intelligence_dict(parsed_data, profile)

        # 4. Strict Pydantic validation
        try:
            return LearnerIntelligenceReport.model_validate(normalized_data)
        except Exception as err:
            raise LLMParseError(
                f"LearnerIntelligenceReport validation failed on repaired LLM output: {str(err)}",
                raw_content=raw_content,
            )


    def generate_build_coaching(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to generate structured build coaching JSON."""
        system_instruction = (
            "You are the UniOS Universal Build Coach (AI/ML-2). "
            "Generate structured, pedagogically sound coaching for a learner's build project. "
            "CRITICAL: Output strictly valid JSON matching the schema in the user prompt. "
            "Do NOT output raw HTML, JSX, or React UI code. "
            "Target output under 700 tokens."
        )
        raw_content = self._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
            temperature=settings.LLM_TEMPERATURE,
        )
        json_text = extract_json_payload(raw_content)
        try:
            data = json.loads(json_text)
            if not isinstance(data, dict) or "coaching_blocks" not in data:
                raise ValueError("Response missing required 'coaching_blocks' key.")
            if not isinstance(data["coaching_blocks"], list) or len(data["coaching_blocks"]) == 0:
                raise ValueError("'coaching_blocks' must be a non-empty list.")
            return data
        except Exception as e:
            raise LLMParseError(
                f"Failed to parse build coaching response from LLM: {str(e)}",
                raw_content=raw_content,
            )

    def generate_career_response(self, prompt: str) -> _Dict[str, Any]:
        """Calls Groq LLM to generate structured career response JSON."""
        system_instruction = (
            "You are the UniOS Career Intelligence Engine (AI/ML-2 KIE). "
            "Output strictly valid JSON matching the schema specified in the user prompt. "
            "Do NOT output conversational preamble, markdown outside the JSON block, or HTML/JSX code."
        )
        raw_content = self._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=settings.LLM_TEMPERATURE,
        )
        json_text = extract_json_payload(raw_content)
        try:
            data = json.loads(json_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON response is not an object dictionary.")
            return data
        except Exception as e:
            raise LLMParseError(
                f"Failed to parse career response from LLM: {str(e)}",
                raw_content=raw_content,
            )


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

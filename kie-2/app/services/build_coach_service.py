"""
Sprint 5 — Universal Build Coach Service (AI/ML-2)
Task A2-S5-01: Contextual Build Coach
Task A2-S5-02: Project Recommendations

Business logic is isolated here; all route handlers are thin wrappers.
Reuses existing LLM provider, memory engine, and pedagogy engine.
Does NOT introduce an independent learner database.
"""

import uuid
from typing import Any, Dict, List, Optional

from app.schemas.build import (
    ActionItem,
    ArtifactType,
    BuildCoachPublicResponse,
    BuildCoachRequest,
    BuildCoachResponse,
    BuildDifficulty,
    BuildRecommendContext,
    BuildRecommendResponse,
    CoachingBlock,
    CoachingTone,
    ProjectRecommendation,
)
from app.services.build_prompt_builder import (
    build_coach_prompt,
    build_recommend_prompt,
)
from app.services.llm_provider import (
    BaseLLMProvider,
    LLMParseError,
    LLMProviderError,
    get_llm_provider,
)
from app.services.memory_engine import get_memory_engine
from app.services.domain_classifier import classify_domain, DomainArchetype


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _coaching_tone_from_str(raw: Any) -> CoachingTone:
    """Safely parse coaching tone from LLM response; default to instructive."""
    if isinstance(raw, str):
        try:
            return CoachingTone(raw.strip().lower())
        except ValueError:
            pass
    return CoachingTone.INSTRUCTIVE


def _difficulty_from_str(raw: Any) -> BuildDifficulty:
    if isinstance(raw, str):
        try:
            return BuildDifficulty(raw.strip().lower())
        except ValueError:
            pass
    return BuildDifficulty.INTERMEDIATE


def _artifact_type_from_str(raw: Any) -> ArtifactType:
    if isinstance(raw, str):
        cleaned = raw.strip()
        for candidate in (cleaned, cleaned.upper(), cleaned.lower()):
            try:
                return ArtifactType(candidate)
            except ValueError:
                pass
    return ArtifactType.GENERAL


def _sanitize_coaching_blocks(raw_blocks: Any) -> List[CoachingBlock]:
    """Parse and validate LLM-returned coaching blocks defensively."""
    if not isinstance(raw_blocks, list):
        return []
    result = []
    for item in raw_blocks:
        if not isinstance(item, dict):
            continue
        block_type = str(item.get("block_type", "guidance")).strip()
        title = str(item.get("title", "")).strip()
        content = str(item.get("content", "")).strip()
        if not content:
            continue
        # UI boundary enforcement: reject any block containing raw HTML / JSX
        forbidden = ["<html", "<div", "<script", "import React", "export default", "className="]
        if any(tag in content for tag in forbidden):
            content = "[Coaching block redacted: contained forbidden UI code.]"
        result.append(
            CoachingBlock(
                block_type=block_type,
                title=title,
                content=content,
                metadata=item.get("metadata", {}),
            )
        )
    return result


def _determine_coaching_tone_from_mastery(request: BuildCoachRequest) -> CoachingTone:
    """Deterministic fallback tone when LLM tone is unavailable."""
    if not request.concept_mastery and not request.weak_topics:
        return CoachingTone.INSTRUCTIVE
    weak_count = len(request.weak_topics or [])
    mastery_scores = list((request.concept_mastery or {}).values())
    if weak_count > 0 or (mastery_scores and min(mastery_scores) < 0.50):
        return CoachingTone.ENCOURAGING
    if mastery_scores and all(s >= 0.80 for s in mastery_scores):
        return CoachingTone.CHALLENGING
    return CoachingTone.INSTRUCTIVE


# ---------------------------------------------------------------------------
# Public response mapper
# ---------------------------------------------------------------------------

def coaching_response_to_public(internal: BuildCoachResponse) -> BuildCoachPublicResponse:
    """
    Maps the internal rich BuildCoachResponse to the Backend-approved public
    wire format (reply, suggestions, action_items).

    Mapping strategy:
      reply        ← orientation block content + gap_summary (or first substantive block)
      suggestions  ← content of guidance and next_step blocks (as list items)
      action_items ← next_milestone_hint as NEXT_STEP, remediation as REMEDIATION,
                     weak topics as DOCUMENTATION_LINK stubs
    """
    # 1. Build reply: orientation + gap summary (or fallback to first block)
    reply_parts = []
    for block in internal.coaching_blocks:
        if block.block_type in ("orientation", "gap_analysis"):
            if block.content:
                reply_parts.append(block.content)
    if not reply_parts and internal.coaching_blocks:
        reply_parts.append(internal.coaching_blocks[0].content)
    if internal.gap_summary:
        reply_parts.append(internal.gap_summary)
    reply = "\n\n".join(reply_parts) if reply_parts else "Coaching is ready. Please see suggestions below."

    # 2. Build suggestions: guidance, example, encouragement, next_step block contents
    suggestions: List[str] = []
    for block in internal.coaching_blocks:
        if block.block_type in ("guidance", "example", "encouragement", "next_step"):
            text = block.content.strip()
            if text:
                suggestions.append(text)

    # 3. Build action_items
    action_items: List[ActionItem] = []

    # Next milestone hint → NEXT_STEP
    if internal.next_milestone_hint:
        action_items.append(
            ActionItem(
                type="NEXT_STEP",
                label=internal.next_milestone_hint,
                url=None,
            )
        )

    # Remediation flag → REMEDIATION action
    if internal.remediation_recommended:
        action_items.append(
            ActionItem(
                type="REMEDIATION",
                label=(
                    f"Complete remediation for '{internal.project_title}' before advancing. "
                    "A targeted lesson will be generated for your weak topics."
                ),
                url=None,
            )
        )

    # Coaching blocks with block_type=next_step title → NEXT_STEP actions
    for block in internal.coaching_blocks:
        if block.block_type == "next_step" and block.title:
            # Avoid duplicate if already captured from next_milestone_hint
            if not any(ai.label == block.title for ai in action_items):
                action_items.append(
                    ActionItem(
                        type="NEXT_STEP",
                        label=block.title,
                        url=None,
                    )
                )

    return BuildCoachPublicResponse(
        reply=reply,
        suggestions=suggestions,
        action_items=action_items,
    )


# ---------------------------------------------------------------------------
# Build Coach Service
# ---------------------------------------------------------------------------

class BuildCoachService:
    """
    Universal Build Coach — AI/ML-2 Sprint 5.

    Generates domain-adaptive, evidence-driven coaching for any academic
    build artifact (code project, essay, lab report, business plan, etc.).

    Follows the same backend-boundary contract as all Sprint 1-4 services:
    - Backend owns learner records and project persistence.
    - AI/ML-2 owns coaching intelligence only.
    - Memory engine is queried for friction context; not mutated here.
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None) -> None:
        self._provider = provider or get_llm_provider()
        self._memory_engine = get_memory_engine()

    def generate_coaching(self, request: BuildCoachRequest) -> BuildCoachResponse:
        """
        Produce structured coaching for a learner's active build project.

        Pipeline:
          1. Optionally enrich with memory friction context.
          2. Build a token-budgeted LLM prompt.
          3. Call LLM provider.
          4. Defensively validate and parse the response.
          5. Return a fully typed BuildCoachResponse.
        """
        # 1. Enrich request with memory friction if not already supplied
        if not request.relevant_friction:
            try:
                from app.schemas.memory_context import RelevantMemoryQuery
                query = RelevantMemoryQuery(
                    learner_id=request.learner_id,
                    topic=request.project_title,
                    objective=f"Build coaching for {request.artifact_type.value}",
                )
                mem_ctx = self._memory_engine.retrieve_relevant_context(query)
                friction_topics = [f.topic for f in mem_ctx.relevant_friction if f.unresolved]
                if friction_topics:
                    # Build a mutable copy by constructing a new object with enriched friction
                    request = BuildCoachRequest(
                        **{
                            **request.model_dump(),
                            "relevant_friction": friction_topics,
                        }
                    )
            except Exception:
                # Memory enrichment is best-effort; proceed without it
                pass

        # 2. Build prompt
        prompt = build_coach_prompt(request)

        # 3. Call LLM provider (raises LLMProviderError / LLMParseError on failure)
        raw: Dict[str, Any] = self._provider.generate_build_coaching(prompt)

        # 4. Parse and validate
        coaching_blocks = _sanitize_coaching_blocks(raw.get("coaching_blocks", []))
        if not coaching_blocks:
            # Fallback: at minimum return a single orientation block
            coaching_blocks = [
                CoachingBlock(
                    block_type="orientation",
                    title="Coaching Unavailable",
                    content=(
                        f"Build coaching for '{request.project_title}' is being prepared. "
                        "Please retry shortly."
                    ),
                )
            ]

        raw_tone = raw.get("coaching_tone", "")
        tone = _coaching_tone_from_str(raw_tone)
        # Cross-check with mastery evidence for accuracy
        if not raw_tone:
            tone = _determine_coaching_tone_from_mastery(request)

        remediation = bool(raw.get("remediation_recommended", False))
        # Override: if weak topics present and LLM said False, trust mastery evidence
        if not remediation and request.weak_topics:
            mastery_scores = list((request.concept_mastery or {}).values())
            if mastery_scores and min(mastery_scores) < 0.50:
                remediation = True

        return BuildCoachResponse(
            request_id=request.request_id,
            learner_id=request.learner_id,
            project_title=request.project_title,
            artifact_type=request.artifact_type,
            coaching_tone=tone,
            coaching_blocks=coaching_blocks,
            gap_summary=raw.get("gap_summary") or None,
            next_milestone_hint=raw.get("next_milestone_hint") or None,
            remediation_recommended=remediation,
        )

    # ------------------------------------------------------------------
    # Project Recommendations
    # ------------------------------------------------------------------

    def generate_recommendations(
        self,
        context: BuildRecommendContext,
        request_id: str,
        count: int = 3,
    ) -> BuildRecommendResponse:
        """
        Generate domain-adaptive project recommendations for a learner.

        Unlike coaching, this is a deterministic-first approach:
        - Strong deterministic baseline recommendations are always generated.
        - If the LLM provider is live, it may enrich descriptions.
        - Falls back cleanly to deterministic output on LLM failure.
        """
        # Always generate deterministic baseline first
        deterministic = self._build_deterministic_recommendations(context, count)

        # Attempt LLM enrichment (best-effort)
        try:
            prompt = build_recommend_prompt(context, count=count)
            raw = self._provider.generate_build_coaching(prompt)  # reuse provider method for JSON
            llm_recs = self._parse_recommendations(raw, context)
            if llm_recs:
                rationale = str(raw.get("recommendation_rationale", "")) or deterministic.recommendation_rationale
                return BuildRecommendResponse(
                    request_id=request_id,
                    learner_id=context.learner_id,
                    recommendations=llm_recs,
                    recommendation_rationale=rationale,
                )
        except Exception:
            pass  # fall through to deterministic

        return BuildRecommendResponse(
            request_id=request_id,
            learner_id=context.learner_id,
            recommendations=deterministic.recommendations,
            recommendation_rationale=deterministic.recommendation_rationale,
        )

    # ------------------------------------------------------------------
    # Deterministic recommendation engine (domain-adaptive, no LLM needed)
    # ------------------------------------------------------------------

    def _build_deterministic_recommendations(
        self,
        context: BuildRecommendContext,
        count: int,
    ) -> BuildRecommendResponse:
        """
        Produces evidence-grounded project recommendations without LLM.
        Ensures there is always a valid response even if the LLM is unavailable.
        """
        domain = (context.academic_domain or "general").lower()
        stage = (context.learner_stage or "bachelor").lower()
        role = context.target_role or "professional"
        weak_topics = context.current_weak_topics or []

        # Determine overall difficulty from mastery
        mastery_scores = list((context.concept_mastery or {}).values())
        if mastery_scores:
            avg_mastery = sum(mastery_scores) / len(mastery_scores)
            if avg_mastery >= 0.80:
                primary_difficulty = BuildDifficulty.ADVANCED
            elif avg_mastery >= 0.50:
                primary_difficulty = BuildDifficulty.INTERMEDIATE
            else:
                primary_difficulty = BuildDifficulty.FOUNDATIONAL
        else:
            primary_difficulty = BuildDifficulty.FOUNDATIONAL

        recs: List[ProjectRecommendation] = []

        # --- Domain-specific recommendation banks ---
        rec_bank = self._get_domain_rec_bank(
            domain,
            role,
            weak_topics,
            stage,
            degree_program=context.degree_program,
            syllabus_subjects=context.syllabus_subjects,
            syllabus_topics=context.syllabus_topics,
        )

        for i, rec_data in enumerate(rec_bank[:count]):
            rec_id = f"rec_{uuid.uuid4().hex[:6]}"
            artifact = rec_data["artifact_type"]
            recs.append(
                ProjectRecommendation(
                    recommendation_id=rec_id,
                    title=rec_data["title"],
                    type=artifact.value if hasattr(artifact, "value") else str(artifact),
                    difficulty=rec_data.get("difficulty", primary_difficulty),
                    academic_domain=domain,
                    description=rec_data["description"],
                    rationale=rec_data["rationale"],
                    skills=rec_data.get("skills", []),
                    estimated_effort_hours=rec_data.get("hours"),
                    prerequisite_topics=rec_data.get("prerequisites", []),
                )
            )

        if not recs:
            recs = [self._generic_recommendation(domain, role, primary_difficulty)]

        rationale = (
            f"Recommendations tailored to a {stage} learner targeting '{role}' "
            f"in the {domain} domain. "
            + (f"Addresses weak topics: {', '.join(weak_topics[:3])}." if weak_topics else "")
        )

        return BuildRecommendResponse(
            request_id="",
            learner_id=context.learner_id,
            recommendations=recs,
            recommendation_rationale=rationale,
        )

    def _get_domain_rec_bank(
        self,
        domain: str,
        role: str,
        weak_topics: List[str],
        stage: str,
        degree_program: Optional[str] = None,
        syllabus_subjects: Optional[List[str]] = None,
        syllabus_topics: Optional[List[str]] = None,
    ) -> List[dict]:
        """Returns ordered list of recommendation dicts for a given domain."""
        archetype = classify_domain(
            subject=" ".join(syllabus_subjects or []),
            degree_program=degree_program,
            topic=" ".join(syllabus_topics or weak_topics or []),
            academic_domain=domain,
        )

        if archetype == DomainArchetype.BUSINESS_MANAGEMENT or any(k in domain for k in ["bba", "management", "business", "mba"]) or (degree_program and any(k in degree_program.lower() for k in ["bba", "mba", "management"])):
            return [
                {
                    "title": "Small Venture Business Plan & PESTLE Analysis",
                    "artifact_type": ArtifactType.BUSINESS,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": (
                        "Develop an actionable business plan for a new commercial venture, incorporating "
                        "detailed PESTLE environmental scanning, market opportunity assessment, and projected unit economics."
                    ),
                    "rationale": "Applies business management, entrepreneurship, and environmental scanning in a domain-authentic capstone format.",
                    "skills": ["Business Planning", "PESTLE Analysis", "Market Opportunity Assessment", "Financial Forecasting"],
                    "hours": 16.0,
                    "prerequisites": weak_topics[:2] if weak_topics else ["Principles of Management", "Business Environment"],
                },
                {
                    "title": "Retail Financial Ledger & Trial Balance Workbook",
                    "artifact_type": ArtifactType.ANALYSIS,
                    "difficulty": BuildDifficulty.FOUNDATIONAL,
                    "description": (
                        "Construct a comprehensive business accounting ledger recording 20+ commercial transactions, "
                        "posting journal entries to T-accounts, and compiling a verified Trial Balance."
                    ),
                    "rationale": "Builds foundational financial accounting and ledger balancing competencies essential for business management.",
                    "skills": ["General Ledger", "Journal Entries", "Trial Balance", "Financial Statements"],
                    "hours": 12.0,
                    "prerequisites": ["Basic Accounting Principles", "Double Entry System"],
                },
                {
                    "title": "Local Product Demand & Pricing Elasticity Study",
                    "artifact_type": ArtifactType.RESEARCH,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": (
                        "Conduct an empirical demand and pricing analysis for a consumer product or service, "
                        "evaluating price elasticity coefficients, consumer sensitivity, and market equilibrium."
                    ),
                    "rationale": "Connects microeconomic principles with real-world managerial pricing decisions.",
                    "skills": ["Demand Estimation", "Price Elasticity", "Managerial Economics", "Market Survey"],
                    "hours": 14.0,
                    "prerequisites": ["Law of Demand", "Elasticity Fundamentals"],
                },
                {
                    "title": "Corporate Governance & Ethics Case Brief",
                    "artifact_type": ArtifactType.CASE_ANALYSIS,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": (
                        "Analyze a real-world corporate governance and ethics dilemma, evaluating board oversight failures "
                        "and formulating an organizational compliance framework."
                    ),
                    "rationale": "Develops critical thinking in corporate ethics, human values, and executive governance.",
                    "skills": ["Corporate Governance", "Business Ethics", "Stakeholder Analysis"],
                    "hours": 10.0,
                    "prerequisites": ["Business Ethics Basics", "Corporate Stakeholder Theory"],
                },
            ]

        elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT or any(k in domain for k in ["commerce", "finance", "accounting", "b.com", "bcom"]):
            return [
                {
                    "title": "Retail Financial Ledger & Trial Balance Workbook",
                    "artifact_type": ArtifactType.ANALYSIS,
                    "difficulty": BuildDifficulty.FOUNDATIONAL,
                    "description": "Construct a full-cycle financial ledger workbook covering journalizing, ledger posting, and trial balance verification.",
                    "rationale": "Directly develops core double-entry accounting and financial statement compilation skills.",
                    "skills": ["Financial Accounting", "General Ledger", "Trial Balance", "Reconciliation"],
                    "hours": 12.0,
                    "prerequisites": weak_topics[:2] if weak_topics else ["Journal Entries", "Debit/Credit Rules"],
                },
                {
                    "title": "Small Business Financial Health Analysis",
                    "artifact_type": ArtifactType.ANALYSIS,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": "Analyse the financial statements of an enterprise, identify key ratios, and recommend strategic improvements.",
                    "rationale": "Applies accounting fundamentals in a realistic business scenario.",
                    "skills": ["Financial Ratios", "Balance Sheet Analysis", "Recommendations"],
                    "hours": 10.0,
                    "prerequisites": weak_topics[:2] if weak_topics else ["Financial Statements", "Ratio Analysis"],
                },
                {
                    "title": "SME Working Capital & Cash Flow Forecast",
                    "artifact_type": ArtifactType.ANALYSIS,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": "Develop a multi-month working capital and cash budget model evaluating liquidity and operational cash flow requirements.",
                    "rationale": "Applies quantitative financial planning to practical business solvency management.",
                    "skills": ["Cash Flow Modeling", "Working Capital", "Financial Ratios"],
                    "hours": 14.0,
                    "prerequisites": ["Cash Flow Concepts", "Ratio Analysis"],
                },
                {
                    "title": "Corporate Financial Statement Ratio Analysis",
                    "artifact_type": ArtifactType.RESEARCH,
                    "difficulty": BuildDifficulty.ADVANCED,
                    "description": "Perform comprehensive comparative ratio analysis across profitability, liquidity, and solvency metrics.",
                    "rationale": "Synthesizes advanced accounting analysis and corporate finance evaluation.",
                    "skills": ["Ratio Analysis", "DuPont Analysis", "Financial Performance"],
                    "hours": 18.0,
                    "prerequisites": ["Financial Statement Analysis", "Corporate Finance"],
                },
            ]

        elif archetype == DomainArchetype.APPLIED_OFFICE_IT:
            return [
                {
                    "title": "Executive Dashboard & PivotTable Analytics Workbook",
                    "artifact_type": ArtifactType.ANALYSIS,
                    "difficulty": BuildDifficulty.FOUNDATIONAL,
                    "description": "Design an automated business analytics workbook using modern spreadsheet formulas (XLOOKUP, SUMIFS), data validation, and dynamic PivotTables.",
                    "rationale": "Develops high-demand spreadsheet and office analytics capabilities for modern workplace readiness.",
                    "skills": ["Spreadsheets", "PivotTables", "Data Validation", "XLOOKUP/VLOOKUP"],
                    "hours": 10.0,
                    "prerequisites": weak_topics[:2] if weak_topics else ["Spreadsheet Basics", "Data Entry"],
                },
                {
                    "title": "Office Automation & Business Reporting System",
                    "artifact_type": ArtifactType.PORTFOLIO,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": "Create an integrated business documentation and presentation suite automating recurring weekly operational summaries.",
                    "rationale": "Builds applied IT productivity and professional reporting competencies.",
                    "skills": ["Document Automation", "Executive Presentation", "Office IT"],
                    "hours": 12.0,
                    "prerequisites": ["Business Documentation", "Presentation Design"],
                },
            ]

        elif archetype == DomainArchetype.GENERAL_HUMANITIES_SCIENCE:
            if any(k in domain for k in ["law", "legal", "jurisprudence"]):
                return [
                    {
                        "title": "Constitutional Law Landmark Case Brief",
                        "artifact_type": ArtifactType.CASE_ANALYSIS,
                        "difficulty": BuildDifficulty.INTERMEDIATE,
                        "description": "Draft an authoritative IRAC-structured case brief on a landmark constitutional ruling, analyzing judicial ratio and doctrine.",
                        "rationale": "Builds rigorous legal analysis and statutory interpretation skills.",
                        "skills": ["IRAC Framework", "Case Law Analysis", "Judicial Precedent"],
                        "hours": 10.0,
                        "prerequisites": weak_topics[:2] if weak_topics else ["Constitutional Principles"],
                    },
                    {
                        "title": "Contract Dispute Moot Argument",
                        "artifact_type": ArtifactType.ORAL_VIVA,
                        "difficulty": BuildDifficulty.ADVANCED,
                        "description": "Prepare and deliver an oral argument for a simulated contract dispute, applying offer, acceptance, and consideration doctrine.",
                        "rationale": "Integrates oral advocacy with substantive contract law knowledge.",
                        "skills": ["Oral Advocacy", "Contract Law", "Argumentation"],
                        "hours": 12.0,
                        "prerequisites": ["Contract Law Fundamentals"],
                    },
                ]
            else:
                return [
                    {
                        "title": "Environmental Impact Assessment & Sustainability Audit",
                        "artifact_type": ArtifactType.RESEARCH,
                        "difficulty": BuildDifficulty.INTERMEDIATE,
                        "description": "Conduct a structured sustainability audit and environmental impact report evaluating campus or local resource consumption.",
                        "rationale": "Grounds environmental science and policy concepts in empirical investigation.",
                        "skills": ["Environmental Impact Assessment", "Data Collection", "Policy Evaluation"],
                        "hours": 12.0,
                        "prerequisites": weak_topics[:2] if weak_topics else ["Ecosystem Principles", "Environmental Policy"],
                    },
                    {
                        "title": "Critical Discourse & Applied Ethics Essay",
                        "artifact_type": ArtifactType.ESSAY,
                        "difficulty": BuildDifficulty.FOUNDATIONAL,
                        "description": "Author an academic essay examining moral philosophy, human values, and societal implications in contemporary institutions.",
                        "rationale": "Strengthens argumentative clarity, critical analysis, and scholarly writing.",
                        "skills": ["Critical Thinking", "Scholarly Writing", "Applied Ethics"],
                        "hours": 8.0,
                        "prerequisites": ["Foundations of Ethics", "Academic Writing"],
                    },
                ]

        elif archetype == DomainArchetype.CODING_CS or any(k in domain for k in ["engineering", "computer", "software", "tech"]):
            clean_role = role if role and "software" not in role.lower() and "professional" not in role.lower() else "Software Engineering"
            return [
                {
                    "title": f"End-to-End {clean_role} Portfolio Implementation",
                    "artifact_type": ArtifactType.CODE_PROJECT,
                    "difficulty": BuildDifficulty.INTERMEDIATE,
                    "description": (
                        f"Design and implement an end-to-end {clean_role} system demonstrating "
                        "clean architecture, test automation, and robust error handling."
                    ),
                    "rationale": f"Demonstrates concrete production capabilities in {clean_role}.",
                    "skills": [clean_role, "Software Architecture", "Unit Testing"],
                    "hours": 20.0,
                    "prerequisites": weak_topics[:2] if weak_topics else ["Data Structures", "OOP"],
                },
                {
                    "title": "Algorithm Benchmark & Optimization Report",
                    "artifact_type": ArtifactType.RESEARCH_REPORT,
                    "difficulty": BuildDifficulty.FOUNDATIONAL,
                    "description": "Analyze and compare the empirical runtime and memory characteristics of algorithmic solutions across varied workloads.",
                    "rationale": "Reinforces algorithmic problem-solving and empirical profiling.",
                    "skills": ["Performance Profiling", "Algorithmic Analysis", "Benchmarking"],
                    "hours": 8.0,
                    "prerequisites": ["Algorithms", "Data Structures"],
                },
                {
                    "title": "Modular Service Architecture Specification",
                    "artifact_type": ArtifactType.DESIGN_ARTIFACT,
                    "difficulty": BuildDifficulty.ADVANCED,
                    "description": "Produce a comprehensive architecture document with component diagrams, API specifications, and database schema models.",
                    "rationale": "Prepares learners for large-scale systems thinking and technical documentation.",
                    "skills": ["System Design", "API Design", "Data Modeling"],
                    "hours": 15.0,
                    "prerequisites": ["Databases", "Distributed Systems Basics"],
                },
            ]

        # Generic fallback
        return []

    def _generic_recommendation(
        self, domain: str, role: str, difficulty: BuildDifficulty
    ) -> ProjectRecommendation:
        archetype = classify_domain(academic_domain=domain)
        if archetype == DomainArchetype.BUSINESS_MANAGEMENT:
            return ProjectRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Small Venture Business Plan & PESTLE Analysis",
                type=ArtifactType.BUSINESS.value,
                difficulty=difficulty,
                academic_domain=domain,
                description="Develop an actionable business plan for a new commercial venture incorporating PESTLE scanning and financial forecasting.",
                rationale="Applies management principles and market analysis in a practical capstone project.",
                skills=["Business Planning", "PESTLE Analysis", "Management"],
                estimated_effort_hours=16.0,
                prerequisite_topics=[],
            )
        elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT:
            return ProjectRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Retail Financial Ledger & Trial Balance Workbook",
                type=ArtifactType.ANALYSIS.value,
                difficulty=difficulty,
                academic_domain=domain,
                description="Construct an accounting ledger recording commercial transactions, posting journal entries, and compiling a Trial Balance.",
                rationale="Builds foundational financial accounting and ledger balancing competencies.",
                skills=["General Ledger", "Trial Balance", "Financial Statements"],
                estimated_effort_hours=12.0,
                prerequisite_topics=[],
            )
        elif archetype == DomainArchetype.APPLIED_OFFICE_IT:
            return ProjectRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Executive Dashboard & PivotTable Analytics Workbook",
                type=ArtifactType.ANALYSIS.value,
                difficulty=difficulty,
                academic_domain=domain,
                description="Design an automated business analytics workbook using modern spreadsheet formulas and dynamic PivotTables.",
                rationale="Builds high-demand spreadsheet and office analytics capabilities.",
                skills=["Spreadsheets", "PivotTables", "Data Modeling"],
                estimated_effort_hours=10.0,
                prerequisite_topics=[],
            )
        elif archetype == DomainArchetype.GENERAL_HUMANITIES_SCIENCE:
            return ProjectRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="Environmental Sustainability Impact Study",
                type=ArtifactType.RESEARCH.value,
                difficulty=difficulty,
                academic_domain=domain,
                description="Conduct a structured sustainability audit and environmental impact report evaluating local resource usage.",
                rationale="Grounds empirical investigation in scientific research methodology.",
                skills=["Research Methodology", "Environmental Impact", "Data Analysis"],
                estimated_effort_hours=12.0,
                prerequisite_topics=[],
            )
        else:
            return ProjectRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:6]}",
                title="End-to-End Implementation Project",
                type=ArtifactType.CODE_PROJECT.value,
                difficulty=difficulty,
                academic_domain=domain,
                description="Design and implement a modular software solution demonstrating test coverage and clean architecture.",
                rationale="Targeted at building core software development and architectural competency.",
                skills=["Software Engineering", "System Design", "Testing"],
                estimated_effort_hours=15.0,
                prerequisite_topics=[],
            )

    def _parse_recommendations(
        self, raw: Dict[str, Any], context: BuildRecommendContext
    ) -> List[ProjectRecommendation]:
        """Defensively parse LLM recommendation list. Handles both old and new field names."""
        raw_recs = raw.get("recommendations", [])
        if not isinstance(raw_recs, list):
            return []
        result = []
        for item in raw_recs:
            if not isinstance(item, dict):
                continue
            try:
                # Accept both 'type' (new contract) and 'artifact_type' (LLM legacy)
                raw_type = item.get("type") or item.get("artifact_type")
                artifact = _artifact_type_from_str(raw_type)
                # Accept both 'skills' (new contract) and 'key_skills_targeted' (LLM legacy)
                skills = item.get("skills") or item.get("key_skills_targeted") or []
                result.append(
                    ProjectRecommendation(
                        recommendation_id=str(item.get("recommendation_id", uuid.uuid4().hex[:6])),
                        title=str(item.get("title", "Project")).strip(),
                        type=artifact.value,
                        difficulty=_difficulty_from_str(item.get("difficulty")),
                        academic_domain=str(item.get("academic_domain", context.academic_domain or "general")).strip(),
                        description=str(item.get("description", "")).strip(),
                        rationale=str(item.get("rationale", "")).strip(),
                        skills=skills if isinstance(skills, list) else [],
                        estimated_effort_hours=float(item["estimated_effort_hours"]) if item.get("estimated_effort_hours") else None,
                        prerequisite_topics=item.get("prerequisite_topics", []),
                    )
                )
            except Exception:
                continue
        return result


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_build_coach_service: Optional[BuildCoachService] = None


def get_build_coach_service() -> BuildCoachService:
    """Singleton provider for BuildCoachService."""
    global _build_coach_service
    if _build_coach_service is None:
        _build_coach_service = BuildCoachService()
    return _build_coach_service

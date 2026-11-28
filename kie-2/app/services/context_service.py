import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import settings
from app.schemas.context_v2 import (
    ContextQuestion,
    WebhookQuestionsPayload,
    WebhookResolvedPayload,
)
from app.services.llm_provider import extract_json_payload, get_llm_provider
from app.services.domain_classifier import classify_domain, DomainArchetype

logger = logging.getLogger(__name__)


class ContextService:
    """
    KIE Context Engine:
    Handles Onboarding Context Analysis (clarifying questions) and Context Resolution
    with asynchronous outbound webhook delivery to Backend.
    """

    def generate_questions(self, context_data: Dict[str, Any]) -> List[ContextQuestion]:
        """
        Analyzes ContextV2 payload and produces 2-5 targeted clarifying questions.
        Uses LLM with deterministic high-quality fallback.
        """
        # If live LLM is configured, attempt smart contextual questions
        if settings.LLM_PROVIDER.lower() != "mock":
            try:
                llm_questions = self._generate_questions_via_llm(context_data)
                if llm_questions and len(llm_questions) >= 2:
                    return llm_questions
            except Exception as e:
                logger.warning(f"[ContextService] LLM question generation failed ({e}), using rule-based questions.")

        return self._generate_questions_deterministic(context_data)

    def _generate_questions_via_llm(self, context_data: Dict[str, Any]) -> Optional[List[ContextQuestion]]:
        provider = get_llm_provider()
        learner = context_data.get("learner") or {}
        education = context_data.get("education") or {}

        domain = education.get("domain") or education.get("academic_domain") or "General Academics"
        degree = education.get("degree_program") or "Undergraduate Degree"
        archetype = classify_domain(subject=degree, degree_program=degree, academic_domain=domain)

        default_goal = (
            "Medical / Healthcare Practitioner or Biological Researcher"
            if archetype == DomainArchetype.GENERAL_HUMANITIES_SCIENCE
            else (
                "Business Executive / Management Consultant"
                if archetype == DomainArchetype.BUSINESS_MANAGEMENT
                else (
                    "Financial Analyst / Professional Accountant"
                    if archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT
                    else "Technical Mastery & Software Engineering"
                )
            )
        )

        system_instruction = (
            "You are the UniOS Learner Context Engine. "
            "Analyze the learner's profile, academic degree, and discipline. "
            "Generate 2 to 4 domain-adaptive clarifying multiple-choice questions "
            "to assess their primary subject focus, practical/experimental experience tier, and learning objectives. "
            "CRITICAL: Tailor questions strictly to their academic field (e.g., biological/clinical topics for medical/sciences, "
            "managerial/analytical topics for business, financial tools for accounting). "
            "NEVER ask programming questions unless the learner is explicitly in Computer Science or Software Engineering. "
            "Output strictly valid JSON matching this schema:\n"
            "[\n"
            "  {\n"
            '    "question_id": "q_001",\n'
            '    "text": "<domain-appropriate question>",\n'
            '    "type": "multi_select" | "single_select",\n'
            '    "options": ["<opt 1>", "<opt 2>", "<opt 3>", "<opt 4>"]\n'
            "  }\n"
            "]"
        )

        user_prompt = f"""LEARNER PROFILE:
Goal: {learner.get('primary_goal') or default_goal}
Current Skills: {learner.get('skills', [])}
Target Skills: {learner.get('target_skills', [])}
Academic: {degree} ({education.get('academic_status', 'BACHELOR')})
Domain: {domain} (Archetype: {archetype.value})
"""
        raw = provider._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
            temperature=0.3,
        )
        json_text = extract_json_payload(raw)
        data = json.loads(json_text)
        if isinstance(data, list):
            return [ContextQuestion.model_validate(q) for q in data]
        if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
            return [ContextQuestion.model_validate(q) for q in data["questions"]]
        return None

    def _generate_questions_deterministic(self, context_data: Dict[str, Any]) -> List[ContextQuestion]:
        learner = context_data.get("learner") or {}
        education = context_data.get("education") or {}
        skills = learner.get("skills") or learner.get("target_skills") or []
        experience = learner.get("experience")

        domain = education.get("domain") or education.get("academic_domain") or "General Academics"
        degree = education.get("degree_program") or "Undergraduate Degree"
        archetype = classify_domain(subject=degree, degree_program=degree, academic_domain=domain)

        questions: List[ContextQuestion] = []

        if archetype == DomainArchetype.GENERAL_HUMANITIES_SCIENCE:
            # Q1: Medical, Life Sciences, or Scientific Focus Areas
            questions.append(
                ContextQuestion(
                    question_id="q_001",
                    text="Which core scientific, biological, or clinical disciplines are you primarily focusing on?",
                    type="multi_select",
                    options=[
                        "Anatomical & Physiological Systems",
                        "Cellular & Molecular Biology",
                        "Zoological Scope & Animal Diversity",
                        "Clinical Diagnosis & Patient Care",
                        "Pharmacology, Therapeutics & Pathology",
                        "Physical Sciences & Laboratory Research",
                    ],
                )
            )
            # Q2: Laboratory, Clinical, or Research Tier
            questions.append(
                ContextQuestion(
                    question_id="q_002",
                    text="What is your current level of practical laboratory, clinical, or field research experience?",
                    type="single_select",
                    options=[
                        "< 1 year (Foundational/Coursework)",
                        "1-2 years (Developing Lab/Clinical Experience)",
                        "3-5 years (Intermediate Field/Hospital Practice)",
                        "5+ years (Advanced Clinical/Research Fellow)",
                    ],
                )
            )
            # Q3: Career Goal
            questions.append(
                ContextQuestion(
                    question_id="q_003",
                    text="What is your primary learning and career objective for this academic curriculum?",
                    type="single_select",
                    options=[
                        "Medical Practice, Clinical Healthcare & Hospital Care",
                        "Scientific Research, Laboratory Investigation & Publishing",
                        "University Examination Excellence & Full Syllabus Mastery",
                        "Public Health, Epidemiology & Healthcare Policy",
                    ],
                )
            )
            # Q4: Learning Style
            questions.append(
                ContextQuestion(
                    question_id="q_004",
                    text="What is your preferred learning cadence and pedagogical format?",
                    type="single_select",
                    options=[
                        "Visual anatomical and cellular models with structured takeaways",
                        "Standard pacing with real-world clinical and empirical case studies",
                        "Deep foundational derivations with academic research literature",
                    ],
                )
            )

        elif archetype == DomainArchetype.BUSINESS_MANAGEMENT:
            questions.append(
                ContextQuestion(
                    question_id="q_001",
                    text="Which primary business and managerial functional areas are you targeting?",
                    type="multi_select",
                    options=[
                        "Marketing & Brand Management",
                        "Human Resource & Organizational Behavior",
                        "Operations & Supply Chain Management",
                        "Strategic Management & Business Environment",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_002",
                    text="What is your practical experience level in business operations or project management?",
                    type="single_select",
                    options=[
                        "< 1 year (Entry-Level)",
                        "1-2 years (Associate / Analyst)",
                        "3-5 years (Mid-Management)",
                        "5+ years (Senior Executive)",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_003",
                    text="What is your primary career goal for this roadmap?",
                    type="single_select",
                    options=[
                        "Corporate Management & Executive Leadership",
                        "Management Consulting & Strategic Advisory",
                        "Entrepreneurship & Small Venture Launch",
                        "University Examination Distinction & Academic Mastery",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_004",
                    text="What is your preferred learning format?",
                    type="single_select",
                    options=[
                        "Corporate case study walkthroughs (e.g. Tata, Zomato, Apple)",
                        "Structured executive frameworks and visual flowcharts",
                        "Interactive managerial problem-solving scenarios",
                    ],
                )
            )

        elif archetype == DomainArchetype.ACCOUNTING_FINANCE_QUANT:
            questions.append(
                ContextQuestion(
                    question_id="q_001",
                    text="Which accounting, financial, or quantitative areas are you primarily mastering?",
                    type="multi_select",
                    options=[
                        "Financial Accounting & Journal Entries",
                        "Cost & Management Accounting",
                        "Corporate Finance & Capital Budgeting",
                        "Business Statistics & Quantitative Analysis",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_002",
                    text="What is your numerical and financial problem-solving experience level?",
                    type="single_select",
                    options=[
                        "< 1 year (Foundational)",
                        "1-2 years (Developing Ledger/Tax Skills)",
                        "3-5 years (Intermediate Financial Analyst)",
                        "5+ years (Advanced / Audit Readiness)",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_003",
                    text="What is your primary career goal for this roadmap?",
                    type="single_select",
                    options=[
                        "Chartered Accounting (CA) / CPA Certification",
                        "Corporate Financial Planning & Analysis (FP&A)",
                        "Investment Banking & Financial Modeling",
                        "University Examination Distinction & Ledger Mastery",
                    ],
                )
            )
            questions.append(
                ContextQuestion(
                    question_id="q_004",
                    text="What is your preferred learning cadence?",
                    type="single_select",
                    options=[
                        "Step-by-step worked numerical ledgers and journal entries",
                        "Spreadsheet financial models and balance sheet templates",
                        "Formula derivations with exam problem walkthroughs",
                    ],
                )
            )

        else: # CODING_CS / APPLIED_OFFICE_IT
            if not skills or len(skills) < 2:
                questions.append(
                    ContextQuestion(
                        question_id="q_001",
                        text="Which programming languages or technical tools do you primarily work with?",
                        type="multi_select",
                        options=["Python", "JavaScript", "TypeScript", "Java", "Go", "C++", "Rust", "SQL"],
                    )
                )

            if not experience or str(experience).strip().lower() in ["", "none", "null"]:
                questions.append(
                    ContextQuestion(
                        question_id="q_002",
                        text="How many years of technical or programming experience do you have?",
                        type="single_select",
                        options=["< 1 year (Beginner)", "1-2 years (Developing)", "3-5 years (Intermediate)", "5+ years (Advanced)"],
                    )
                )

            questions.append(
                ContextQuestion(
                    question_id="q_003",
                    text="What is your primary learning and career goal for this roadmap?",
                    type="single_select",
                    options=[
                        "Crack technical interviews at top engineering companies",
                        "Build hands-on production-ready portfolio projects",
                        "Achieve high academic grades and syllabus mastery",
                        "Transition into AI / Machine Learning and Data Engineering",
                    ],
                )
            )

            questions.append(
                ContextQuestion(
                    question_id="q_004",
                    text="What is your preferred learning pace and feedback cadence?",
                    type="single_select",
                    options=[
                        "Fast-paced with frequent coding challenges",
                        "Standard balanced pacing with worked examples",
                        "Deep foundational pacing with visual concept walkthroughs",
                    ],
                )
            )

        return questions[:4]

    def resolve_answers(self, answers: List[Any]) -> Dict[str, Any]:
        """
        Transforms question answers into structured learner enrichment data.
        Ensures hardcoded backend keys 'primary_languages' and 'experience_level' are populated.
        """
        new_context: Dict[str, Any] = {
            "primary_languages": ["Python"],
            "experience_level": "intermediate",
            "preferred_learning_style": "hands-on",
            "career_readiness": "moderate",
        }

        for item in answers:
            q_id = getattr(item, "question_id", None) or (item.get("question_id") if isinstance(item, dict) else None)
            ans = getattr(item, "answer", None) if hasattr(item, "answer") else (item.get("answer") if isinstance(item, dict) else None)

            if not q_id or ans is None:
                continue

            if q_id == "q_001":
                if isinstance(ans, list):
                    new_context["primary_languages"] = [str(x) for x in ans]
                elif isinstance(ans, str):
                    new_context["primary_languages"] = [x.strip() for x in ans.split(",") if x.strip()]
            elif q_id == "q_002":
                clean_ans = str(ans).lower()
                if "< 1" in clean_ans or "beginner" in clean_ans:
                    new_context["experience_level"] = "beginner"
                    new_context["career_readiness"] = "developing"
                elif "5+" in clean_ans or "advanced" in clean_ans or "senior" in clean_ans:
                    new_context["experience_level"] = "advanced"
                    new_context["career_readiness"] = "high"
                else:
                    new_context["experience_level"] = "intermediate"
                    new_context["career_readiness"] = "moderate"
            elif q_id == "q_003":
                new_context["career_goal"] = str(ans)
            elif q_id == "q_004":
                new_context["preferred_learning_style"] = str(ans)
            else:
                new_context[q_id] = ans

        return new_context

    def post_questions_webhook(self, user_id: str, questions: List[ContextQuestion]) -> bool:
        """Sends generated questions to Backend Webhook W1."""
        url = f"{settings.BACKEND_URL}/api/v1/onboarding/kie/webhook/questions"
        payload = WebhookQuestionsPayload(user_id=user_id, questions=questions).model_dump()
        headers = {
            "X-Kie-Signature": settings.KIE_WEBHOOK_SECRET,
            "Content-Type": "application/json",
        }

        logger.info(f"[ContextService] Delivering {len(questions)} questions for user '{user_id}' to webhook {url}")
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                logger.info(f"[ContextService] Webhook W1 successfully delivered for user '{user_id}' (Status {resp.status_code})")
                return True
        except Exception as e:
            logger.error(f"[ContextService] Failed delivering questions webhook W1 to {url}: {e}")
            return False

    def post_resolved_webhook(self, user_id: str, new_context: Dict[str, Any]) -> bool:
        """Sends resolved context to Backend Webhook W2."""
        url = f"{settings.BACKEND_URL}/api/v1/onboarding/kie/webhook/resolved"
        payload = WebhookResolvedPayload(user_id=user_id, new_context=new_context).model_dump()
        headers = {
            "X-Kie-Signature": settings.KIE_WEBHOOK_SECRET,
            "Content-Type": "application/json",
        }

        logger.info(f"[ContextService] Delivering resolved context for user '{user_id}' to webhook {url}")
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                logger.info(f"[ContextService] Webhook W2 successfully delivered for user '{user_id}' (Status {resp.status_code})")
                return True
        except Exception as e:
            logger.error(f"[ContextService] Failed delivering resolved webhook W2 to {url}: {e}")
            return False


_context_service_instance: Optional[ContextService] = None


def get_context_service() -> ContextService:
    global _context_service_instance
    if _context_service_instance is None:
        _context_service_instance = ContextService()
    return _context_service_instance


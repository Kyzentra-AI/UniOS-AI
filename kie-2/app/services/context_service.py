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

        system_instruction = (
            "You are the UniOS Learner Context Engine. "
            "Analyze the learner's profile and generate 2 to 4 clarifying multiple-choice questions "
            "to assess their primary programming skills, experience tier, and learning objectives. "
            "Output strictly valid JSON matching this schema:\n"
            "[\n"
            "  {\n"
            '    "question_id": "q_001",\n'
            '    "text": "What are your primary programming languages?",\n'
            '    "type": "multi_select",\n'
            '    "options": ["Python", "Java", "Go", "C++", "JavaScript", "Rust"]\n'
            "  }\n"
            "]"
        )

        user_prompt = f"""LEARNER PROFILE:
Goal: {learner.get('primary_goal', 'Software Engineer')}
Current Skills: {learner.get('skills', [])}
Target Skills: {learner.get('target_skills', [])}
Academic: {education.get('degree_program', 'Computer Science')} ({education.get('academic_status', 'BACHELOR')})
Domain: {education.get('domain', 'Technology')}
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
        skills = learner.get("skills") or learner.get("target_skills") or []
        experience = learner.get("experience")

        questions: List[ContextQuestion] = []

        # Q1: Primary Languages (multi_select)
        if not skills or len(skills) < 2:
            questions.append(
                ContextQuestion(
                    question_id="q_001",
                    text="Which programming languages or core technical tools do you primarily work with?",
                    type="multi_select",
                    options=["Python", "JavaScript", "TypeScript", "Java", "Go", "C++", "Rust", "SQL"],
                )
            )

        # Q2: Experience level (single_select)
        if not experience or str(experience).strip().lower() in ["", "none", "null"]:
            questions.append(
                ContextQuestion(
                    question_id="q_002",
                    text="How many years of programming experience do you have?",
                    type="single_select",
                    options=["< 1 year (Beginner)", "1-2 years (Developing)", "3-5 years (Intermediate)", "5+ years (Advanced)"],
                )
            )

        # Q3: Target Career Objective (single_select)
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

        # Q4: Preferred Learning Pace (single_select)
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


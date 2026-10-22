import json
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.schemas.interpretation import (
    InterpretRequest,
    InterpretResponse,
    IntentCategory,
    PedagogicalStrategy,
)
from app.services.llm_provider import extract_json_payload, get_llm_provider, LLMProviderError


class InterpretEngine:
    """Pedagogical Interpreter Engine (AI-1) implementing Section 14.1.
    Analyzes learner intent, ContextV2, and syllabus references to determine instructional strategy.
    """

    def interpret(self, request: InterpretRequest) -> InterpretResponse:
        # If live LLM is configured, attempt intelligent inference
        if settings.LLM_PROVIDER.lower() != "mock":
            try:
                llm_response = self._interpret_via_llm(request)
                if llm_response:
                    return llm_response
            except Exception as e:
                print(f">>> [AI-1 InterpretEngine] LLM interpret failed ({e}), using deterministic rules.")

        # Deterministic rule-based interpretation (100% reliable fallback)
        return self._interpret_deterministic(request)

    def _interpret_via_llm(self, request: InterpretRequest) -> Optional[InterpretResponse]:
        provider = get_llm_provider()
        system_instruction = (
            "You are the UniOS Pedagogical Interpreter Engine (AI-1). "
            "Analyze the learner's intent, multi-dimensional ContextV2, and syllabus references. "
            "Output strictly valid JSON matching this schema:\n"
            "{\n"
            '  "intent_category": "CONCEPTUAL_EXPLANATION" | "CODE_WALKTHROUGH" | "REVISION" | "EXAM_PREP" | "PROBLEM_SOLVING",\n'
            '  "pedagogical_strategy": "ANALOGY_THEN_CODE" | "SOCRATIC_INQUIRY" | "HANDS_ON_FIRST" | "STEP_BY_STEP_DERIVATION",\n'
            '  "knowledge_gaps_identified": ["<gap 1>", "<gap 2>"],\n'
            '  "target_difficulty": "BEGINNER" | "INTERMEDIATE" | "ADVANCED",\n'
            '  "recommended_block_flow": ["TEXT", "CODE", "INTERACTIVE", "QUIZ"],\n'
            '  "key_concepts_to_cover": ["<concept 1>", "<concept 2>", "<concept 3>"],\n'
            '  "metadata": {\n'
            '    "scaffolding_level": "HIGH" | "MEDIUM" | "LOW",\n'
            '    "estimated_read_minutes": 10,\n'
            '    "emphasis": "<key pedagogical focus>"\n'
            "  }\n"
            "}"
        )

        user_prompt = f"""TOPIC: {request.topic}
USER INTENT: {request.user_intent or 'Master fundamentals and application'}
REFERENCES: {json.dumps(request.references[:3]) if request.references else 'Standard syllabus'}
LEARNER CONTEXT:
- Learner ID: {request.learner_id}
- Goal: {request.context.get('learner', {}).get('primary_goal', 'Technical mastery')}
- Target Skills: {request.context.get('learner', {}).get('target_skills', [])}
- Academic: {request.context.get('education', {}).get('degree_program', 'Undergraduate')} ({request.context.get('education', {}).get('academic_status', 'BACHELOR')})
- Memory Summary: {json.dumps(request.context.get('memory_summary', {}))}
"""
        raw_content = provider._safe_chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=650,
            temperature=0.2,
        )
        json_text = extract_json_payload(raw_content)
        data = json.loads(json_text)
        return InterpretResponse.model_validate(data)

    def _interpret_deterministic(self, request: InterpretRequest) -> InterpretResponse:
        intent_lower = (request.user_intent or "").lower()
        topic_lower = request.topic.lower()
        context = request.context or {}
        learner = context.get("learner") or {}
        education = context.get("education") or {}
        memory_summary = context.get("memory_summary") or {}
        inferred_context = learner.get("inferred_context") or {}

        # 1. Intent Categorization
        if any(w in intent_lower for w in ["code", "walkthrough", "syntax", "snippet", "implementation", "traversal"]):
            intent_category = IntentCategory.CODE_WALKTHROUGH.value
        elif any(w in intent_lower for w in ["exam", "test", "gate", "interview", "prep"]):
            intent_category = IntentCategory.EXAM_PREP.value
        elif any(w in intent_lower for w in ["revise", "revision", "recap", "review", "summary"]):
            intent_category = IntentCategory.REVISION.value
        elif any(w in intent_lower for w in ["solve", "problem", "challenge", "exercise", "practice", "debug"]):
            intent_category = IntentCategory.PROBLEM_SOLVING.value
        else:
            intent_category = IntentCategory.CONCEPTUAL_EXPLANATION.value

        # 2. Pedagogical Strategy
        if intent_category == IntentCategory.CODE_WALKTHROUGH.value or any(w in intent_lower for w in ["analogy", "visual", "analogies"]):
            strategy = PedagogicalStrategy.ANALOGY_THEN_CODE.value
        elif any(w in intent_lower for w in ["socratic", "question", "why"]):
            strategy = PedagogicalStrategy.SOCRATIC_INQUIRY.value
        elif any(w in intent_lower for w in ["hands on", "practical", "build", "interactive"]):
            strategy = PedagogicalStrategy.HANDS_ON_FIRST.value
        else:
            strategy = PedagogicalStrategy.STEP_BY_STEP_DERIVATION.value

        # 3. Knowledge Gaps Identification
        knowledge_gaps: List[str] = []
        if isinstance(inferred_context.get("weakness"), str):
            knowledge_gaps.append(inferred_context["weakness"].lower().replace(" ", "_"))
        if isinstance(memory_summary.get("struggling_concepts"), list):
            for sc in memory_summary["struggling_concepts"]:
                clean_gap = str(sc).lower().replace(" ", "_")
                if clean_gap not in knowledge_gaps:
                    knowledge_gaps.append(clean_gap)

        if not knowledge_gaps:
            if "tree" in topic_lower:
                knowledge_gaps = ["recursion_call_stack_frames", "tree_pointer_mutation"]
            elif "graph" in topic_lower:
                knowledge_gaps = ["visited_set_tracking", "queue_stack_choice"]
            elif "dynamic" in topic_lower or "dp" in topic_lower:
                knowledge_gaps = ["overlapping_subproblem_identification", "state_transition_formulation"]
            else:
                knowledge_gaps = [f"{request.topic.lower().replace(' ', '_')}_prerequisites"]

        # 4. Target Difficulty
        academic_status = str(education.get("academic_status") or "BACHELOR").upper()
        if "MASTER" in academic_status or "GRADUATE" in academic_status:
            difficulty = "ADVANCED"
        elif any(w in intent_lower for w in ["basic", "simple", "beginner", "intro"]):
            difficulty = "BEGINNER"
        else:
            difficulty = "INTERMEDIATE"

        # 5. Recommended Block Flow
        if any(w in intent_lower for w in ["video", "animation"]):
            block_flow = ["TEXT", "CODE", "INTERACTIVE", "QUIZ", "VIDEO"]
        else:
            block_flow = ["TEXT", "CODE", "INTERACTIVE", "QUIZ"]

        # 6. Key Concepts to Cover
        key_concepts: List[str] = []
        if request.references:
            for ref in request.references[:3]:
                if isinstance(ref, dict):
                    h = ref.get("heading")
                    if h and h not in key_concepts:
                        key_concepts.append(h)

        if not key_concepts:
            if "tree" in topic_lower:
                key_concepts = [
                    "BST ordering invariant (Left < Node < Right)",
                    "In-order DFS traversal yields sorted output",
                    "Recursive vs iterative stack implementation",
                ]
            else:
                key_concepts = [
                    f"Core principles of {request.topic}",
                    f"Implementation mechanics and edge cases",
                    f"Time and space complexity trade-offs",
                ]

        # 7. Metadata
        metadata = {
            "scaffolding_level": "HIGH" if difficulty == "BEGINNER" else "MEDIUM",
            "estimated_read_minutes": 10,
            "emphasis": f"{strategy.lower().replace('_', ' ')} with visual reinforcement",
        }

        return InterpretResponse(
            intent_category=intent_category,
            pedagogical_strategy=strategy,
            knowledge_gaps_identified=knowledge_gaps,
            target_difficulty=difficulty,
            recommended_block_flow=block_flow,
            key_concepts_to_cover=key_concepts,
            metadata=metadata,
        )


_interpret_engine_instance: Optional[InterpretEngine] = None


def get_interpret_engine() -> InterpretEngine:
    global _interpret_engine_instance
    if _interpret_engine_instance is None:
        _interpret_engine_instance = InterpretEngine()
    return _interpret_engine_instance

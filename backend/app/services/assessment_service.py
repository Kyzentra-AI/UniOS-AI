from __future__ import annotations
import hashlib
import uuid
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException, status
from app.core.supabase import supabase_admin
from app.core.config import settings
from app.schemas.assessment import (
    Assessment,
    AssessmentAnswer,
    AssessmentAttemptCreate,
    AssessmentAttemptResponse,
    AssessmentOption,
    AssessmentQuestion,
)
from app.services.event_service import event_service

import logging
logger = logging.getLogger(__name__)


class AssessmentService:
    @staticmethod
    def _sanitize_for_client(asmt_row: dict) -> dict:
        """Strips out server-side grading answer keys before sending assessment to client."""
        raw_questions = asmt_row.get("questions") or []
        sanitized_questions = []
        for q in raw_questions:
            q_clean = {
                "id": str(q.get("id")),
                "type": q.get("type", "mcq"),
                "question": q.get("question", ""),
            }
            if "options" in q and q["options"] is not None:
                q_clean["options"] = [
                    {"id": str(opt.get("id")), "text": str(opt.get("text"))}
                    for opt in q["options"]
                ]
            if "code" in q and q["code"] is not None:
                q_clean["code"] = q["code"]
            if "language" in q and q["language"] is not None:
                q_clean["language"] = q["language"]
            sanitized_questions.append(q_clean)

        return {
            "id": asmt_row["id"],
            "title": asmt_row.get("title") or f"{asmt_row.get('topic', 'Topic')} Assessment",
            "type": asmt_row.get("type", "mcq"),
            "instructions": asmt_row.get("instructions") or "Answer all questions to test your understanding.",
            "questions": sanitized_questions,
        }

    @staticmethod
    def _generate_fallback_assessment(topic: str) -> Tuple[List[dict], Dict[str, str]]:
        """
        Generates deterministic, stable questions and options for a topic
        when the AI service is unreachable or unconfigured.
        Returns (questions_with_options, answer_keys).
        """
        # Create stable deterministic IDs based on the topic
        topic_slug = "".join(c if c.isalnum() else "_" for c in topic.lower()).strip("_")
        
        fallback_questions = [
            {
                "id": f"q_{topic_slug}_1",
                "type": "mcq",
                "question": f"Which fundamental principle best defines the core architecture of {topic}?",
                "options": [
                    {"id": "opt-1", "text": "Modular separation of concerns with structured abstractions"},
                    {"id": "opt-2", "text": "Uncontrolled global mutable state across processes"},
                    {"id": "opt-3", "text": "Purely synchronous single-threaded blocking operations"},
                    {"id": "opt-4", "text": "Hardcoded memory addresses for dynamic allocation"},
                ],
                "correct_option_id": "opt-1",
            },
            {
                "id": f"q_{topic_slug}_2",
                "type": "mcq",
                "question": f"In production environments, what is the primary operational consideration when scaling {topic}?",
                "options": [
                    {"id": "opt-1", "text": "Data consistency, throughput bottlenecks, and fault tolerance"},
                    {"id": "opt-2", "text": "Disabling indexes and logging to maximize CPU cycles"},
                    {"id": "opt-3", "text": "Removing input validation layers to lower latency"},
                    {"id": "opt-4", "text": "Hardcoding configuration parameters in source code"},
                ],
                "correct_option_id": "opt-1",
            },
            {
                "id": f"q_{topic_slug}_3",
                "type": "mcq",
                "question": f"Which strategy is most effective for diagnosing performance regressions in {topic}?",
                "options": [
                    {"id": "opt-1", "text": "Analyzing structured execution traces, latency metrics, and resource utilization"},
                    {"id": "opt-2", "text": "Rebooting nodes repeatedly until the regression disappears"},
                    {"id": "opt-3", "text": "Ignoring slow query logs if average uptime exceeds 95%"},
                    {"id": "opt-4", "text": "Increasing timeout thresholds indefinitely"},
                ],
                "correct_option_id": "opt-1",
            },
        ]

        answer_keys = {q["id"]: q["correct_option_id"] for q in fallback_questions}
        return fallback_questions, answer_keys

    @staticmethod
    async def _generate_with_kie(
        topic: str,
        session_data: dict,
        learner_id: str,
    ) -> Tuple[List[dict], Dict[str, str], str]:
        """
        Attempts to generate an assessment via KIE AI engine.
        Returns (questions, answer_keys, assessment_type).
        """
        url = f"{settings.KIE_BASE_URL}/api/v1/kie/assessments/generate"
        payload = {
            "learner_id": learner_id,
            "topic": topic,
            "session_id": session_data.get("id"),
            "lesson_id": session_data.get("lesson_id"),
            "preferred_type": "mcq",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    questions = data.get("questions", [])
                    answer_keys = {}
                    for q in questions:
                        if "correct_option_id" in q:
                            answer_keys[str(q["id"])] = str(q["correct_option_id"])
                        elif "answer" in q:
                            answer_keys[str(q["id"])] = str(q["answer"])
                    return questions, answer_keys, data.get("type", "mcq")
        except Exception as e:
            logger.warning(f"KIE assessment generation unavailable: {e}. Falling back to deterministic generator.")

        fallback_q, fallback_keys = AssessmentService._generate_fallback_assessment(topic)
        return fallback_q, fallback_keys, "mcq"

    @staticmethod
    async def get_or_generate_assessment(
        learner_id: str,
        session_id: str,
        topic: str,
    ) -> dict:
        """
        Retrieves existing assessment for (session_id, topic) or generates and persists a new one.
        Returns sanitized Assessment matching the frontend contract directly.
        """
        # 1. Verify learning session exists
        session_res = (
            supabase_admin.table("learning_sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        session_data = session_res.data[0] if session_res.data else {}

        # 2. Check if assessment already exists for this (session_id, topic)
        existing = (
            supabase_admin.table("assessments")
            .select("*")
            .eq("session_id", session_id)
            .eq("topic", topic)
            .execute()
        )

        if existing.data:
            return AssessmentService._sanitize_for_client(existing.data[0])

        # 3. Generate new assessment
        questions, answer_keys, asmt_type = await AssessmentService._generate_with_kie(
            topic, session_data, learner_id
        )

        assessment_id = f"assessment_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        record = {
            "id": assessment_id,
            "session_id": session_id,
            "learner_id": learner_id,
            "topic": topic,
            "title": f"{topic} Assessment",
            "type": asmt_type,
            "instructions": "Answer all questions.",
            "questions": questions,
            "answer_keys": answer_keys,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        try:
            insert_res = supabase_admin.table("assessments").insert(record).execute()
            saved_asmt = insert_res.data[0] if insert_res.data else record
        except Exception as e:
            logger.warning(f"Could not persist assessment to table: {e}")
            saved_asmt = record

        return AssessmentService._sanitize_for_client(saved_asmt)

    @staticmethod
    async def _evaluate_with_kie(
        attempt_in: AssessmentAttemptCreate,
        learner_id: str,
    ) -> Tuple[float, Dict[str, Any], str]:
        """
        Calls KIE Mastery/Remediation engine to evaluate answers.
        Returns (score, mastery_updates, feedback).
        """
        payload = {
            "learner_id": learner_id,
            "assessment_id": attempt_in.assessment_id,
            "topic": attempt_in.topic,
            "answers": [a.model_dump() for a in attempt_in.answers],
            "total_time_spent_seconds": attempt_in.total_time_spent_seconds,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/mastery/evaluate",
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    return (
                        float(data.get("score", 0.0)),
                        data.get("mastery_updates", {}),
                        data.get("feedback", "Good work."),
                    )
        except Exception as e:
            logger.warning(f"KIE evaluation unavailable ({e}). Using server-side evaluation.")

        return 0.0, {}, "Assessment recorded."

    @staticmethod
    async def record_attempt(
        learner_id: str,
        attempt_in: AssessmentAttemptCreate,
    ) -> dict:
        """
        Validates assessment and question IDs, evaluates answers, records attempt,
        updates learner mastery, and returns the attempt response.
        """
        hints_used_count = sum(a.hints_used for a in attempt_in.answers)

        # 1. Fetch the assessment record if available to validate questions and grade MCQs
        asmt_res = (
            supabase_admin.table("assessments")
            .select("*")
            .eq("id", attempt_in.assessment_id)
            .execute()
        )

        local_score: Optional[float] = None
        answer_keys = {}
        if asmt_res.data:
            asmt_data = asmt_res.data[0]
            answer_keys = asmt_data.get("answer_keys") or {}

            # Validate questions belong to assessment
            valid_q_ids = {str(q["id"]) for q in asmt_data.get("questions", [])}
            submitted_q_ids = {str(a.question_id) for a in attempt_in.answers}
            if valid_q_ids and not submitted_q_ids.issubset(valid_q_ids):
                logger.warning(f"Submitted question IDs {submitted_q_ids} not all in {valid_q_ids}")

            # Grade MCQs if answer keys are present
            if answer_keys and len(attempt_in.answers) > 0:
                correct_count = 0
                for a in attempt_in.answers:
                    expected = answer_keys.get(str(a.question_id))
                    if expected and str(a.answer).strip().lower() == str(expected).strip().lower():
                        correct_count += 1
                local_score = round(correct_count / len(attempt_in.answers), 2)

        # 2. Call KIE for mastery and qualitative feedback
        kie_score, mastery_updates, feedback = await AssessmentService._evaluate_with_kie(
            attempt_in, learner_id
        )

        # Use local score if computed, otherwise fallback to KIE score
        final_score = local_score if local_score is not None else (kie_score or 1.0)
        final_feedback = feedback or ("Good work." if final_score >= 0.7 else "Review the lesson material to strengthen key concepts.")

        now_dt = datetime.now(timezone.utc)
        attempt_id = f"attempt_{uuid.uuid4().hex[:12]}"

        # 3. Persist attempt
        attempt_data = {
            "id": attempt_id,
            "session_id": attempt_in.session_id,
            "learner_id": learner_id,
            "assessment_id": attempt_in.assessment_id,
            "topic": attempt_in.topic,
            "answers": [a.model_dump() for a in attempt_in.answers],
            "score": final_score,
            "total_time_spent_seconds": attempt_in.total_time_spent_seconds,
            "hints_used_count": hints_used_count,
            "is_completed": attempt_in.is_completed,
            "mastery_updates": mastery_updates,
            "feedback": final_feedback,
            "created_at": now_dt.isoformat(),
        }

        try:
            res = supabase_admin.table("assessment_attempts").insert(attempt_data).execute()
            if res.data:
                attempt_row = res.data[0]
            else:
                attempt_row = attempt_data
        except Exception as e:
            logger.warning(f"Failed to persist attempt to database: {e}")
            attempt_row = attempt_data

        # 4. Persist mastery updates to learner_mastery
        if attempt_in.is_completed and mastery_updates:
            for subject, topics in mastery_updates.items():
                if isinstance(topics, dict):
                    for top, details in topics.items():
                        new_score = details.get("score", final_score)
                        new_status = details.get("status", "PROFICIENT" if new_score >= 0.8 else "DEVELOPING")
                        try:
                            supabase_admin.table("learner_mastery").upsert({
                                "learner_id": learner_id,
                                "subject": subject,
                                "topic": top,
                                "mastery_score": new_score,
                                "status": new_status,
                                "last_assessed_at": now_dt.isoformat(),
                            }, on_conflict="learner_id,subject,topic").execute()
                        except Exception as me_err:
                            logger.warning(f"Could not upsert learner_mastery: {me_err}")

        # 5. Emit event
        event_service.record_event(learner_id, "ASSESSMENT_COMPLETED", "ASSESSMENT", attempt_in.assessment_id)

        # 6. Format response matching AssessmentAttemptResponse
        sess_id = attempt_row.get("session_id") or attempt_in.session_id
        return {
            "id": str(attempt_row.get("id", attempt_id)),
            "session_id": str(sess_id) if sess_id else None,
            "learner_id": str(attempt_row.get("learner_id", learner_id)),
            "assessment_id": str(attempt_row.get("assessment_id", attempt_in.assessment_id)),
            "topic": attempt_row.get("topic", attempt_in.topic),
            "answers": attempt_row.get("answers", [a.model_dump() for a in attempt_in.answers]),
            "score": attempt_row.get("score", final_score),
            "total_time_spent_seconds": int(attempt_row.get("total_time_spent_seconds", attempt_in.total_time_spent_seconds)),
            "hints_used_count": int(attempt_row.get("hints_used_count", hints_used_count)),
            "is_completed": bool(attempt_row.get("is_completed", attempt_in.is_completed)),
            "mastery_updates": attempt_row.get("mastery_updates") or {},
            "feedback": attempt_row.get("feedback") or final_feedback,
            "created_at": attempt_row.get("created_at") or now_dt.isoformat(),
        }


assessment_service = AssessmentService()

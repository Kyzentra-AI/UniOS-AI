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
    MasteryStatus,
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
        # 1. Verify learning session exists and belongs to learner
        session_res = (
            supabase_admin.table("learning_sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        if not session_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Learning session '{session_id}' not found",
            )
        session_data = session_res.data[0]
        if session_data.get("learner_id") and str(session_data["learner_id"]) != str(learner_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Learning session does not belong to the authenticated learner",
            )

        # 2. Check if assessment already exists for this (session_id, topic)
        existing = (
            supabase_admin.table("assessments")
            .select("*")
            .eq("session_id", session_id)
            .eq("topic", topic)
            .execute()
        )

        if existing.data:
            asmt_row = existing.data[0]
            if asmt_row.get("learner_id") and str(asmt_row["learner_id"]) != str(learner_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Assessment does not belong to the authenticated learner",
                )
            return AssessmentService._sanitize_for_client(asmt_row)

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
            if insert_res and insert_res.data:
                saved_asmt = insert_res.data[0]
            else:
                saved_asmt = record
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Could not persist assessment to table: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist assessment: {str(e)}",
            )

        return AssessmentService._sanitize_for_client(saved_asmt)

    @staticmethod
    async def _evaluate_with_kie(
        attempt_in: AssessmentAttemptCreate,
        learner_id: str,
    ) -> Tuple[Optional[float], Dict[str, Any], Optional[str], bool]:
        """
        Calls KIE Mastery/Remediation engine to evaluate answers.
        Returns (score, mastery_updates, feedback, success).
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
                    raw_score = data.get("score")
                    score = float(raw_score) if raw_score is not None else 0.0
                    score = max(0.0, min(1.0, score))
                    return (
                        score,
                        data.get("mastery_updates", {}),
                        data.get("feedback"),
                        True,
                    )
                else:
                    logger.warning(f"KIE evaluation returned status {response.status_code}: {response.text}")
                    return (None, {}, None, False)
        except Exception as e:
            logger.warning(f"KIE evaluation unavailable ({e}). Using server-side evaluation.")
            return (None, {}, None, False)

    @staticmethod
    def _persist_mastery_updates(
        learner_id: str,
        default_topic: str,
        mastery_updates: Dict[str, Any],
        final_score: Optional[float],
        now_dt: datetime,
    ) -> None:
        """
        Parses and persists mastery updates into learner_mastery table.
        Ensures score is bounded [0.0, 1.0] and status conforms to enum.
        """
        valid_statuses = {"NOVICE", "DEVELOPING", "PROFICIENT", "MASTERED"}

        def _calculate_status(score: float) -> str:
            if score >= 0.9:
                return "MASTERED"
            if score >= 0.8:
                return "PROFICIENT"
            if score >= 0.5:
                return "DEVELOPING"
            return "NOVICE"

        def _save_mastery_record(subject: str, topic: str, raw_score: Any, raw_status: Optional[str]):
            try:
                score_val = float(raw_score) if raw_score is not None else (final_score or 0.0)
            except (ValueError, TypeError):
                score_val = final_score or 0.0
            score_val = max(0.0, min(1.0, score_val))

            status_str = str(raw_status).upper() if raw_status else _calculate_status(score_val)
            if status_str not in valid_statuses:
                status_str = _calculate_status(score_val)

            try:
                supabase_admin.table("learner_mastery").upsert({
                    "learner_id": learner_id,
                    "subject": subject,
                    "topic": topic,
                    "mastery_score": score_val,
                    "status": status_str,
                    "last_assessed_at": now_dt.isoformat(),
                }, on_conflict="learner_id,subject,topic").execute()
            except Exception as me_err:
                logger.warning(f"Could not upsert learner_mastery for {subject}/{topic}: {me_err}")

        for k1, v1 in mastery_updates.items():
            if isinstance(v1, dict):
                if "score" in v1 or "status" in v1 or "mastery_score" in v1:
                    _save_mastery_record("General", k1, v1.get("score") or v1.get("mastery_score"), v1.get("status"))
                else:
                    for k2, v2 in v1.items():
                        if isinstance(v2, dict):
                            _save_mastery_record(k1, k2, v2.get("score") or v2.get("mastery_score"), v2.get("status"))
                        elif isinstance(v2, (int, float)):
                            _save_mastery_record(k1, k2, v2, None)
            elif isinstance(v1, (int, float)):
                _save_mastery_record("General", k1, v1, None)

    @staticmethod
    async def record_attempt(
        learner_id: str,
        attempt_in: AssessmentAttemptCreate,
    ) -> dict:
        """
        Validates assessment and question IDs, evaluates answers, records attempt,
        updates learner mastery, and returns the attempt response.
        """
        # 1. Answer validation: Prevent duplicate question IDs
        submitted_q_ids = [str(a.question_id) for a in attempt_in.answers]
        if len(submitted_q_ids) != len(set(submitted_q_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate question IDs in submitted answers",
            )

        # 2. Assessment existence check
        asmt_res = (
            supabase_admin.table("assessments")
            .select("*")
            .eq("id", attempt_in.assessment_id)
            .execute()
        )
        if not asmt_res.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment '{attempt_in.assessment_id}' not found",
            )
        asmt_data = asmt_res.data[0]

        # 3. Ownership validation: Verify assessment belongs to authenticated learner
        asmt_learner_id = asmt_data.get("learner_id")
        if asmt_learner_id and str(asmt_learner_id) != str(learner_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assessment does not belong to the authenticated learner",
            )

        # 4. Session validation & ownership
        asmt_session_id = asmt_data.get("session_id")
        if attempt_in.session_id and asmt_session_id and str(attempt_in.session_id) != str(asmt_session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment does not belong to the specified session",
            )

        target_session_id = attempt_in.session_id or asmt_session_id
        if target_session_id:
            session_res = (
                supabase_admin.table("learning_sessions")
                .select("id, learner_id")
                .eq("id", target_session_id)
                .execute()
            )
            if session_res.data:
                session_data = session_res.data[0]
                if session_data.get("learner_id") and str(session_data["learner_id"]) != str(learner_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Learning session does not belong to the authenticated learner",
                    )

        # 5. Question & Answer validation against assessment questions
        asmt_questions = asmt_data.get("questions") or []
        valid_q_map = {str(q.get("id")): q for q in asmt_questions if isinstance(q, dict)}
        valid_q_ids = set(valid_q_map.keys())

        if valid_q_ids:
            invalid_q_ids = set(submitted_q_ids) - valid_q_ids
            if invalid_q_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid question ID(s): {', '.join(sorted(invalid_q_ids))}",
                )

        for a in attempt_in.answers:
            q_obj = valid_q_map.get(str(a.question_id))
            if q_obj and q_obj.get("type") == "mcq" and q_obj.get("options"):
                valid_opts = {str(opt.get("id")) for opt in q_obj["options"] if isinstance(opt, dict)}
                valid_opt_texts = {str(opt.get("text")).strip().lower() for opt in q_obj["options"] if isinstance(opt, dict)}
                ans_str = str(a.answer).strip() if a.answer is not None else ""
                if ans_str and ans_str not in valid_opts and ans_str.lower() not in valid_opt_texts:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid option '{a.answer}' submitted for question '{a.question_id}'",
                    )

        # 6. Local grading for MCQs with answer keys
        local_score: Optional[float] = None
        answer_keys = asmt_data.get("answer_keys") or {}
        total_questions = len(asmt_questions) if asmt_questions else len(attempt_in.answers)

        if answer_keys and total_questions > 0:
            correct_count = 0
            for a in attempt_in.answers:
                expected = answer_keys.get(str(a.question_id))
                if expected is not None and str(a.answer).strip().lower() == str(expected).strip().lower():
                    correct_count += 1
            local_score = round(correct_count / total_questions, 2)

        # 7. Evaluate with KIE (mastery, qualitative feedback)
        kie_score, mastery_updates, kie_feedback, kie_success = await AssessmentService._evaluate_with_kie(
            attempt_in, learner_id
        )

        # 8. Score & Feedback resolution
        # Avoid assigning a false perfect score (1.0) when KIE fails or returns 0.0
        if local_score is not None:
            final_score = local_score
        elif kie_success and kie_score is not None:
            final_score = kie_score
        else:
            final_score = 0.0 if attempt_in.is_completed else None

        if kie_success and kie_feedback:
            final_feedback = kie_feedback
        elif not attempt_in.is_completed:
            final_feedback = "Assessment progress saved. Complete all questions to see final evaluation."
        elif final_score is not None:
            final_feedback = "Good work." if final_score >= 0.7 else "Review the lesson material to strengthen key concepts."
        else:
            final_feedback = "Evaluation service is currently unavailable. Your attempt has been recorded."

        hints_used_count = sum(a.hints_used for a in attempt_in.answers)
        now_dt = datetime.now(timezone.utc)
        attempt_id = f"attempt_{uuid.uuid4().hex[:12]}"

        # 9. Persist attempt (explicitly raise on DB error instead of returning in-memory record silently)
        attempt_data = {
            "id": attempt_id,
            "session_id": target_session_id,
            "learner_id": learner_id,
            "assessment_id": attempt_in.assessment_id,
            "topic": attempt_in.topic,
            "answers": [a.model_dump() for a in attempt_in.answers],
            "score": final_score,
            "total_time_spent_seconds": attempt_in.total_time_spent_seconds,
            "hints_used_count": hints_used_count,
            "is_completed": attempt_in.is_completed,
            "mastery_updates": mastery_updates if kie_success else {},
            "feedback": final_feedback,
            "created_at": now_dt.isoformat(),
        }

        try:
            res = supabase_admin.table("assessment_attempts").insert(attempt_data).execute()
            if res and res.data:
                attempt_row = res.data[0]
            else:
                attempt_row = attempt_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to persist assessment attempt to database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to persist assessment attempt: {str(e)}",
            )

        # 10. Persist mastery updates only for completed attempts and verified evaluations
        if attempt_in.is_completed and kie_success and mastery_updates:
            AssessmentService._persist_mastery_updates(learner_id, attempt_in.topic, mastery_updates, final_score, now_dt)

        # 11. Emit event only on completion
        if attempt_in.is_completed:
            event_service.record_event(learner_id, "ASSESSMENT_COMPLETED", "ASSESSMENT", attempt_in.assessment_id)

        # 12. Format response matching AssessmentAttemptResponse
        sess_id = attempt_row.get("session_id") or target_session_id
        return {
            "id": str(attempt_row.get("id", attempt_id)),
            "session_id": str(sess_id) if sess_id else None,
            "learner_id": str(attempt_row.get("learner_id", learner_id)),
            "assessment_id": str(attempt_row.get("assessment_id", attempt_in.assessment_id)),
            "topic": attempt_row.get("topic", attempt_in.topic),
            "answers": attempt_row.get("answers", [a.model_dump() for a in attempt_in.answers]),
            "score": attempt_row.get("score"),
            "total_time_spent_seconds": int(attempt_row.get("total_time_spent_seconds", attempt_in.total_time_spent_seconds)),
            "hints_used_count": int(attempt_row.get("hints_used_count", hints_used_count)),
            "is_completed": bool(attempt_row.get("is_completed", attempt_in.is_completed)),
            "mastery_updates": attempt_row.get("mastery_updates") or {},
            "feedback": attempt_row.get("feedback") or final_feedback,
            "created_at": attempt_row.get("created_at") or now_dt.isoformat(),
        }


assessment_service = AssessmentService()

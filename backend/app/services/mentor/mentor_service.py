from __future__ import annotations
import logging
import uuid
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.supabase import supabase_admin
from app.schemas.mentor import MentorChatRequest, MentorChatResponse, MentorMode
from app.schemas.billing import CreditOperation
from app.services.billing.billing_guard import billing_guard
from app.services.billing.billing_service import billing_service

logger = logging.getLogger(__name__)


class MentorService:
    @staticmethod
    def _generate_fallback_reply(mode: str, message: str, topic: Optional[str]) -> str:
        """
        Generates contextual persona-aligned mentor guidance when the KIE engine
        is offline or during testing.
        """
        topic_label = topic or "this topic"
        lower_msg = message.lower()

        if mode == MentorMode.TUTOR.value or mode == "tutor":
            if "explain" in lower_msg or "what is" in lower_msg:
                return (
                    f"In simple terms, {topic_label} focuses on breaking complex logic into manageable, "
                    f"structured components. Think of it as a blueprint that coordinates actions, handles "
                    f"storage efficiently, and ensures reliable execution without manual intervention."
                )
            return (
                f"Great question regarding {topic_label}! To master this concept, start by understanding the "
                f"underlying data flow, test edge cases, and verify how changes impact overall system performance."
            )

        elif mode == MentorMode.STUDY_COACH.value or mode == "study-coach":
            return (
                f"For mastering {topic_label}, I recommend a 25-minute focused sprint (Pomodoro): "
                f"1. Review key terminology for 5 mins. "
                f"2. Solve 2 practice questions. "
                f"3. Summarize your takeaways. Let's make steady progress today!"
            )

        elif mode == MentorMode.ACCOUNTABILITY.value or mode == "accountability":
            return (
                f"You're currently working on {topic_label}. Every concept you master today brings you "
                f"closer to completing your roadmap milestones. Have you attempted the lesson assessment yet?"
            )

        elif mode == MentorMode.MOTIVATION.value or mode == "motivation":
            return (
                f"Learning technical subjects like {topic_label} can feel challenging at first, but with "
                f"each question you explore, you're building real engineering intuition. Keep pushing forward—you've got this!"
            )

        return f"I'm here to assist you with {topic_label}. What specific aspect would you like to explore?"

    @staticmethod
    def _resolve_step_context_fallback(
        learner_id: str,
        chat_request: MentorChatRequest,
    ) -> Dict[str, Any]:
        """
        Server-Side Fallback Resolution (Web BUG-05).
        If client omitted stepIndex or stepContent, look up the active
        public.learning_sessions row using (learner_id, lesson_id) or (learner_id, mission_id).
        """
        ctx_dict = chat_request.context.model_dump(by_alias=True) if chat_request.context else {}

        has_step = bool(ctx_dict.get("stepIndex") is not None or ctx_dict.get("step_index") is not None)
        has_content = bool(ctx_dict.get("stepContent") or ctx_dict.get("step_content"))

        lesson_id = ctx_dict.get("lessonId") or ctx_dict.get("lesson_id")
        mission_id = ctx_dict.get("missionId") or ctx_dict.get("mission_id")

        if (not has_step or not has_content) and (lesson_id or mission_id):
            try:
                query = supabase_admin.table("learning_sessions").select("*").eq("learner_id", learner_id)
                if lesson_id:
                    query = query.eq("lesson_id", lesson_id)
                elif mission_id:
                    query = query.eq("mission_id", mission_id)
                session_res = query.order("updated_at", desc=True).limit(1).execute()

                if session_res and isinstance(session_res.data, list) and session_res.data:
                    session = session_res.data[0]
                    lesson_data = session.get("lesson_data") or {}
                    blocks = lesson_data.get("blocks", []) if isinstance(lesson_data, dict) else []

                    if blocks:
                        target_block_id = (
                            ctx_dict.get("currentBlockId")
                            or ctx_dict.get("current_block_id")
                            or session.get("checkpoint_block_id")
                        )
                        matched_idx = 0
                        matched_block = blocks[0]
                        for i, blk in enumerate(blocks):
                            bid = blk.get("id") if isinstance(blk, dict) else getattr(blk, "id", None)
                            if bid and bid == target_block_id:
                                matched_idx = i
                                matched_block = blk
                                break

                        b_title = matched_block.get("title") if isinstance(matched_block, dict) else getattr(matched_block, "title", None)
                        b_content = matched_block.get("content") if isinstance(matched_block, dict) else getattr(matched_block, "content", None)

                        if not has_step:
                            ctx_dict["step_index"] = matched_idx + 1
                            ctx_dict["stepIndex"] = matched_idx + 1
                        if not ctx_dict.get("step_title") and not ctx_dict.get("stepTitle"):
                            ctx_dict["step_title"] = b_title or f"Step {matched_idx + 1}"
                            ctx_dict["stepTitle"] = b_title or f"Step {matched_idx + 1}"
                        if not has_content:
                            ctx_dict["step_content"] = b_content or ""
                            ctx_dict["stepContent"] = b_content or ""
                        if not ctx_dict.get("total_steps") and not ctx_dict.get("totalSteps"):
                            ctx_dict["total_steps"] = len(blocks)
                            ctx_dict["totalSteps"] = len(blocks)

                    if not ctx_dict.get("subject"):
                        subj = session.get("subject")
                        if not subj and session.get("mission_id"):
                            m_res = supabase_admin.table("missions").select("subject_name").eq("id", session["mission_id"]).execute()
                            if m_res and isinstance(m_res.data, list) and m_res.data and m_res.data[0].get("subject_name"):
                                subj = m_res.data[0]["subject_name"]
                        if subj:
                            ctx_dict["subject"] = subj
            except Exception as ex:
                logger.warning(f"Failed to resolve step context fallback: {ex}")

        # Ensure canonical snake_case and camelCase aliases are present for KIE-2 / frontend
        if "stepIndex" in ctx_dict and "step_index" not in ctx_dict:
            ctx_dict["step_index"] = ctx_dict["stepIndex"]
        elif "step_index" in ctx_dict and "stepIndex" not in ctx_dict:
            ctx_dict["stepIndex"] = ctx_dict["step_index"]

        if "stepTitle" in ctx_dict and "step_title" not in ctx_dict:
            ctx_dict["step_title"] = ctx_dict["stepTitle"]
        elif "step_title" in ctx_dict and "stepTitle" not in ctx_dict:
            ctx_dict["stepTitle"] = ctx_dict["step_title"]

        if "stepContent" in ctx_dict and "step_content" not in ctx_dict:
            ctx_dict["step_content"] = ctx_dict["stepContent"]
        elif "step_content" in ctx_dict and "stepContent" not in ctx_dict:
            ctx_dict["stepContent"] = ctx_dict["step_content"]

        if "totalSteps" in ctx_dict and "total_steps" not in ctx_dict:
            ctx_dict["total_steps"] = ctx_dict["totalSteps"]
        elif "total_steps" in ctx_dict and "totalSteps" not in ctx_dict:
            ctx_dict["totalSteps"] = ctx_dict["total_steps"]

        return ctx_dict

    @staticmethod
    async def _call_kie_mentor(
        learner_id: str,
        chat_request: MentorChatRequest,
    ) -> Optional[str]:
        """Calls the KIE AI mentor endpoint if available (Web BUG-06: 45s timeout)."""
        url = f"{settings.KIE_BASE_URL}/api/v1/kie/mentor/chat"
        context_payload = MentorService._resolve_step_context_fallback(learner_id, chat_request)
        payload = {
            "learner_id": learner_id,
            "mode": chat_request.mode,
            "message": chat_request.message,
            "context": context_payload,
            "history": [h.model_dump() for h in chat_request.history],
        }

        try:
            # 45s timeout to accommodate KIE-2 bumped 1800-token responses without premature cutoff
            async with httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=2.0)) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_reply = data.get("reply")
                    if raw_reply is not None:
                        # Beta BUG-02: Do not run HTML escaping or regex stripping; pass clean markdown
                        return str(raw_reply)
        except Exception as e:
            logger.warning(f"KIE mentor chat unavailable ({e}). Using server mentor persona.")

        return None

    @staticmethod
    async def chat(
        learner_id: str,
        chat_request: MentorChatRequest,
    ) -> MentorChatResponse:
        """
        Orchestrates mentor chat: enforces quotas for tutor mode,
        manages conversation lifecycle, invokes AI mentor, and persists messages.
        """
        # 1. Quota & credit enforcement for tutor / study coach modes
        ledger_id: Optional[str] = None
        if chat_request.mode in (MentorMode.TUTOR.value, "tutor"):
            msg_len = len((chat_request.message or "").strip())
            op = (
                CreditOperation.DETAILED_EXPLANATION
                if msg_len > 180 or "explain" in (chat_request.message or "").lower()
                else CreditOperation.SIMPLE_AI_QUESTION
            )
            ledger_id = billing_guard.authorize_and_consume(
                learner_id=learner_id,
                operation=op,
                reference_id=chat_request.conversation_id,
            )

        # 2. Conversation lifecycle
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        conversation_id = chat_request.conversation_id

        if conversation_id:
            conv_res = (
                supabase_admin.table("mentor_conversations")
                .select("*")
                .eq("id", conversation_id)
                .execute()
            )
            if not conv_res.data:
                # If conversation not found in DB, reuse the ID or create new
                conversation_id = conversation_id
                try:
                    supabase_admin.table("mentor_conversations").insert({
                        "id": conversation_id,
                        "learner_id": learner_id,
                        "mode": chat_request.mode,
                        "context": chat_request.context.model_dump(by_alias=True) if chat_request.context else {},
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }).execute()
                except Exception as e:
                    logger.warning(f"Could not insert mentor_conversation: {e}")
            else:
                try:
                    supabase_admin.table("mentor_conversations").update({
                        "updated_at": now_iso,
                    }).eq("id", conversation_id).execute()
                except Exception as e:
                    logger.warning(f"Could not update mentor_conversation: {e}")
        else:
            conversation_id = f"conversation_{uuid.uuid4().hex[:12]}"
            try:
                supabase_admin.table("mentor_conversations").insert({
                    "id": conversation_id,
                    "learner_id": learner_id,
                    "mode": chat_request.mode,
                    "context": chat_request.context.model_dump(by_alias=True) if chat_request.context else {},
                    "created_at": now_iso,
                    "updated_at": now_iso,
                }).execute()
            except Exception as e:
                logger.warning(f"Could not insert mentor_conversation: {e}")

        # 3. Persist incoming user message
        try:
            supabase_admin.table("mentor_messages").insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": chat_request.message,
                "created_at": now_iso,
            }).execute()
        except Exception as e:
            logger.warning(f"Could not insert user mentor_message: {e}")

        # 4. Generate AI reply
        reply = await MentorService._call_kie_mentor(learner_id, chat_request)
        if not reply:
            topic_str = chat_request.context.topic if chat_request.context else None
            reply = MentorService._generate_fallback_reply(
                chat_request.mode, chat_request.message, topic_str
            )

        # 5. Persist mentor reply
        reply_dt = datetime.now(timezone.utc)
        try:
            supabase_admin.table("mentor_messages").insert({
                "conversation_id": conversation_id,
                "role": "mentor",
                "content": reply,
                "created_at": reply_dt.isoformat(),
            }).execute()
        except Exception as e:
            logger.warning(f"Could not insert mentor response message: {e}")

        return MentorChatResponse(
            reply=reply,
            conversation_id=conversation_id,
            created_at=reply_dt,
        )


mentor_service = MentorService()

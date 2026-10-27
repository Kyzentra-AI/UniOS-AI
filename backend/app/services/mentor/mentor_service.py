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
    async def _call_kie_mentor(
        learner_id: str,
        chat_request: MentorChatRequest,
    ) -> Optional[str]:
        """Calls the KIE AI mentor endpoint if available."""
        url = f"{settings.KIE_BASE_URL}/api/v1/kie/mentor/chat"
        payload = {
            "learner_id": learner_id,
            "mode": chat_request.mode,
            "message": chat_request.message,
            "context": chat_request.context.model_dump(by_alias=True) if chat_request.context else {},
            "history": [h.model_dump() for h in chat_request.history],
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("reply")
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
        # 1. Quota enforcement for tutor mode
        if chat_request.mode in (MentorMode.TUTOR.value, "tutor"):
            try:
                usage = billing_service.get_or_create_usage(learner_id)
                tutor_quota = usage.quotas.get("aiTutorRequests")
                if tutor_quota and tutor_quota.remaining <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Daily AI tutor request quota reached. Please upgrade your plan or wait for the daily reset at 00:00 IST.",
                    )

                # Increment used quota
                q_res = (
                    supabase_admin.table("billing_usage_quotas")
                    .select("ai_tutor_requests")
                    .eq("learner_id", learner_id)
                    .execute()
                )
                current_used = q_res.data[0]["ai_tutor_requests"] if q_res.data else 0
                supabase_admin.table("billing_usage_quotas").update({
                    "ai_tutor_requests": current_used + 1,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("learner_id", learner_id).execute()
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Quota check skipped or unconfigured: {e}")

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

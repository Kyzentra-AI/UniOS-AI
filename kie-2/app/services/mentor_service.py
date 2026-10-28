"""
UniOS — Mentor Chat Service (AI/ML KIE)
Tasks:
  - Persona-Driven Interactive AI Mentor (POST /api/v1/kie/mentor/chat)
"""

import logging
from typing import Optional
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.services.mentor_prompt_builder import (
    build_mentor_chat_prompt,
    get_mentor_system_prompt,
)
from app.services.llm_provider import (
    BaseLLMProvider,
    LLMParseError,
    LLMProviderError,
    MockLLMProvider,
    get_llm_provider,
)

logger = logging.getLogger(__name__)


class MentorService:
    """Core orchestration service for persona-driven interactive AI mentor chat."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self._mock_provider = MockLLMProvider()

    def chat(self, request: MentorChatRequest) -> MentorChatResponse:
        """Processes student query within persona mode, context, and conversation history."""
        system_prompt = get_mentor_system_prompt(request.mode)
        prompt = build_mentor_chat_prompt(request)

        try:
            reply_text = self.provider.generate_mentor_reply(
                prompt=prompt, system_prompt=system_prompt
            )
        except (LLMProviderError, LLMParseError, Exception) as err:
            logger.warning(
                f"[MentorService] Provider failed for mode '{request.mode}' ({err}); falling back to deterministic mock."
            )
            reply_text = self._mock_provider.generate_mentor_reply(
                prompt=prompt, system_prompt=system_prompt
            )

        if not reply_text or not reply_text.strip():
            reply_text = self._mock_provider.generate_mentor_reply(
                prompt=prompt, system_prompt=system_prompt
            )

        return MentorChatResponse(reply=reply_text)


_mentor_service_instance: Optional[MentorService] = None


def get_mentor_service() -> MentorService:
    """Singleton accessor for MentorService."""
    global _mentor_service_instance
    if _mentor_service_instance is None:
        _mentor_service_instance = MentorService()
    return _mentor_service_instance

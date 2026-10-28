
from app.schemas.mentor import MentorChatRequest, MentorChatResponse


class MentorChatEngine:
    """Deterministic fallback for the mentor-chat API contract."""

    def generate(
        self,
        request: MentorChatRequest,
    ) -> MentorChatResponse:
        topic = request.context.topic or "your current learning goal"

        responses = {
            "tutor": (
                f"Let's understand {topic} step by step. Start by identifying "
                "the main concept, then work through a simple example. "
                "What part would you like to understand first?"
            ),
            "study-coach": (
                f"For {topic}, try a focused 25-minute study block: review "
                "the concept, practise one example, then recall the key ideas "
                "without looking at your notes."
            ),
            "accountability": (
                f"Let's make progress on {topic}. Choose one specific task "
                "you can complete now, and check it off before moving on."
            ),
            "motivation": (
                f"Learning {topic} takes practice. Small, consistent steps "
                "count. Focus on understanding one idea at a time and build "
                "from there."
            ),
        }

        return MentorChatResponse(reply=responses[request.mode])

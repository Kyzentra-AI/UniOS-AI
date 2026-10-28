
from typing import Literal

from pydantic import BaseModel, Field


MentorMode = Literal[
    "tutor",
    "study-coach",
    "accountability",
    "motivation",
]


class MentorContext(BaseModel):
    topic: str | None = None
    lesson_id: str | None = None
    roadmap_id: str | None = None
    mission_id: str | None = None


class MentorMessage(BaseModel):
    role: Literal["user", "mentor"]
    content: str


class MentorChatRequest(BaseModel):
    learner_id: str = Field(min_length=1)
    mode: MentorMode = "tutor"
    message: str = Field(min_length=1)
    context: MentorContext = Field(default_factory=MentorContext)
    history: list[MentorMessage] = Field(default_factory=list)


class MentorChatResponse(BaseModel):
    reply: str

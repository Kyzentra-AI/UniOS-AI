from pydantic import BaseModel
from typing import List, Any, Optional

class KIEQuestion(BaseModel):
    question_id: str
    text: str
    type: str
    options: List[str] = []

class KIEWebhookQuestionsPayload(BaseModel):
    user_id: str
    questions: List[KIEQuestion]

class KIEWebhookResolvedPayload(BaseModel):
    user_id: str
    new_context: dict

class AnswerItem(BaseModel):
    question_id: str
    answer: Any

class OnboardingAnswersRequest(BaseModel):
    answers: List[AnswerItem]

from pydantic import BaseModel
from datetime import datetime

class ConversationBase(BaseModel):
    session_id: str
    message_role: str
    content: str

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

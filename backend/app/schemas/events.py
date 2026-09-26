from pydantic import BaseModel
from typing import Any, Dict

class LearnerEventCreate(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str
    payload: Dict[str, Any] = {}

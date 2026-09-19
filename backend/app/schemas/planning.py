from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class MissionBase(BaseModel):
    title: str
    type: str
    content: Optional[str] = None
    status: str = "pending"
    xp_reward: int = 10

class MissionCreate(MissionBase):
    pass

class MissionResponse(MissionBase):
    id: str
    goal_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    title: str
    type: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: str = "pending"

class GoalCreate(GoalBase):
    pass

class GoalResponse(GoalBase):
    id: str
    roadmap_id: str
    user_id: str
    created_at: datetime
    missions: List[MissionResponse] = []

    class Config:
        from_attributes = True


class RoadmapBase(BaseModel):
    title: str
    type: str
    status: str = "active"

class RoadmapCreate(RoadmapBase):
    pass

class RoadmapResponse(RoadmapBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    goals: List[GoalResponse] = []

    class Config:
        from_attributes = True

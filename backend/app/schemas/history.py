from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class LearningHistoryBase(BaseModel):
    topic: str
    mastery_level: int = 0

class LearningHistoryCreate(LearningHistoryBase):
    pass

class LearningHistoryResponse(LearningHistoryBase):
    id: str
    user_id: str
    last_reviewed: datetime

    class Config:
        from_attributes = True


class ProjectHistoryBase(BaseModel):
    project_name: str
    description: Optional[str] = None
    repo_url: Optional[str] = None
    completed_date: Optional[date] = None

class ProjectHistoryCreate(ProjectHistoryBase):
    pass

class ProjectHistoryResponse(ProjectHistoryBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class CareerHistoryBase(BaseModel):
    company: str
    role: str
    start_date: date
    end_date: Optional[date] = None

class CareerHistoryCreate(CareerHistoryBase):
    pass

class CareerHistoryResponse(CareerHistoryBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class AchievementBase(BaseModel):
    badge_name: str
    description: Optional[str] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementResponse(AchievementBase):
    id: str
    user_id: str
    unlocked_at: datetime

    class Config:
        from_attributes = True

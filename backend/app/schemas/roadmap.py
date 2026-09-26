from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RoadmapScope(str, Enum):
    ACADEMIC = "ACADEMIC"
    CAREER = "CAREER"
    BOTH = "BOTH"

class RoadmapRequest(BaseModel):
    syllabus_id: str
    scope: RoadmapScope

class MissionType(str, Enum):
    LEARNING = "LEARNING"
    REVISION = "REVISION"
    ASSIGNMENT = "ASSIGNMENT"
    PRACTICAL = "PRACTICAL"
    ARTIFACT = "ARTIFACT"
    CAREER = "CAREER"

class RoadmapMission(BaseModel):
    title: str
    type: MissionType
    description: str
    priority: str
    estimated_minutes: int
    subject: Optional[str] = None
    week: int
    sequence: int

class RoadmapSubject(BaseModel):
    name: str
    topics: List[str]

class RoadmapSemester(BaseModel):
    name: str
    subjects: List[RoadmapSubject]

class RoadmapCareer(BaseModel):
    goals: List[str] = []

class AIMLRoadmapResponse(BaseModel):
    scope: str
    semesters: List[RoadmapSemester] = []
    career: Optional[RoadmapCareer] = None
    goals: List[str] = []
    milestones: List[str] = []
    missions: List[RoadmapMission] = []

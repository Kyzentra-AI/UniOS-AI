from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class RoadmapScope(str, Enum):
    ACADEMIC = "ACADEMIC"
    CAREER = "CAREER"
    BOTH = "BOTH"

class RoadmapRequest(BaseModel):
    syllabus_id: str
    scope: RoadmapScope
    subject: Optional[str] = None  # None = all subjects; "Operating Systems" = targeted roadmap

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
    priority: str = "MEDIUM"
    estimated_minutes: int = 60
    subject: Optional[str] = None
    week: int
    sequence: int

class RoadmapSubject(BaseModel):
    name: str
    topics: List[str] = []

class RoadmapSemester(BaseModel):
    name: str
    subjects: List[RoadmapSubject] = []

class RoadmapCareer(BaseModel):
    goals: List[str] = []

class SubjectTrack(BaseModel):
    subject_name: str
    mission_count: int
    estimated_total_minutes: int
    core_topics: List[str] = []

class AIMLRoadmapResponse(BaseModel):
    scope: str
    target_subject: Optional[str] = None
    subject_tracks: List[SubjectTrack] = []
    semesters: List[RoadmapSemester] = []
    career: Optional[RoadmapCareer] = None
    goals: List[str] = []
    milestones: List[str] = []
    missions: List[RoadmapMission] = []

class SubjectSummary(BaseModel):
    name: str
    total_missions: int
    completed_missions: int
    in_progress_missions: int
    progress_percentage: int

class RoadmapDetail(BaseModel):
    id: str
    version: int
    scope: str
    subject: Optional[str] = None
    status: str
    scope_data: dict = Field(default_factory=dict)
    missions: List[dict] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CurrentRoadmapResponse(BaseModel):
    roadmap: Optional[RoadmapDetail] = None
    available_subjects: List[SubjectSummary] = []
    active_subject: Optional[str] = None

from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Optional, List
from datetime import datetime

class AcademicStatus(str, Enum):
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    RECENT_GRADUATE = "RECENT_GRADUATE"

class DailyStudyHours(str, Enum):
    LESS_THAN_1 = "LESS_THAN_1"
    HOURS_1_2 = "1_2"
    HOURS_2_3 = "2_3"
    HOURS_3_4 = "3_4"
    HOURS_4_PLUS = "4_PLUS"

class LearningDepth(str, Enum):
    QUICK = "QUICK"
    BALANCED = "BALANCED"
    DEEP = "DEEP"

class LearnerProfileBase(BaseModel):
    primary_goal: Optional[str] = None
    target_skills: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    research: Optional[str] = None
    experience: Optional[str] = None

class AcademicProfileBase(BaseModel):
    academic_status: Optional[AcademicStatus] = None
    university: Optional[str] = None
    degree_program: Optional[str] = None
    domain: Optional[str] = None
    current_year: Optional[str] = None
    graduation_year: Optional[int] = None
    subjects: Optional[List[str]] = None

class LearningPreferencesBase(BaseModel):
    daily_study_hours: Optional[DailyStudyHours] = None
    learning_depth: Optional[LearningDepth] = None

class OnboardingRequest(BaseModel):
    learner_profile: Optional[LearnerProfileBase] = None
    academic_profile: Optional[AcademicProfileBase] = None
    learning_preferences: Optional[LearningPreferencesBase] = None

class OnboardingCompleteValidator(BaseModel):
    """
    This model is used internally to validate the state of the onboarding data 
    before marking it as completed.
    """
    primary_goal: str
    target_skills: List[str]
    skills: List[str]
    projects: List[str]
    research: Optional[str] = None
    experience: Optional[str] = None
    
    academic_status: AcademicStatus
    university: Optional[str] = None
    degree_program: str
    domain: str
    current_year: Optional[str] = None
    graduation_year: Optional[int] = None
    subjects: List[str]
    
    daily_study_hours: DailyStudyHours
    learning_depth: LearningDepth

    @model_validator(mode='after')
    def validate_academic_status_rules(self) -> 'OnboardingCompleteValidator':
        if self.academic_status == AcademicStatus.BACHELOR:
            if not self.university:
                raise ValueError("university is required for BACHELOR")
            if not self.current_year:
                raise ValueError("current_year is required for BACHELOR")
            if self.graduation_year is not None:
                raise ValueError("graduation_year should be null for BACHELOR")
                
        elif self.academic_status == AcademicStatus.RECENT_GRADUATE:
            if self.university is not None:
                raise ValueError("university should be null for RECENT_GRADUATE")
            if self.current_year is not None:
                raise ValueError("current_year should be null for RECENT_GRADUATE")
            if self.graduation_year is None:
                raise ValueError("graduation_year is required for RECENT_GRADUATE")
                
        elif self.academic_status == AcademicStatus.MASTER:
            # Assuming MASTER behaves like BACHELOR based on standard student profile
            if not self.university:
                raise ValueError("university is required for MASTER")
            if not self.current_year:
                raise ValueError("current_year is required for MASTER")
            if self.graduation_year is not None:
                raise ValueError("graduation_year should be null for MASTER")

        return self

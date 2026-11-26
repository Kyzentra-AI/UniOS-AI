from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with camelCase serialization and flexible alias parsing."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class FileCategory(str, Enum):
    ALL = "ALL"
    SYLLABUS = "SYLLABUS"
    BUILD_ARTIFACT = "BUILD_ARTIFACT"
    RESUME = "RESUME"
    ATS = "ATS"


# ------------------------------------------------------------------------------
# Profile & Academic Settings
# ------------------------------------------------------------------------------

class AccountProfileInfo(CamelModel):
    user_id: str
    full_name: str = ""
    email: str = ""
    email_verified: bool = False
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "Asia/Kolkata"
    registration_date: Optional[datetime] = None
    last_login: Optional[datetime] = None


class LearnerProfileInfo(CamelModel):
    learner_id: str
    primary_goal: Optional[str] = None
    target_skills: List[Any] = Field(default_factory=list)
    skills: List[Any] = Field(default_factory=list)
    experience: Optional[str] = None
    research: Optional[str] = None
    onboarding_status: str = "NOT_STARTED"


class AcademicProfileInfo(CamelModel):
    academic_status: Optional[str] = None
    university: Optional[str] = None
    degree_program: Optional[str] = None
    domain: Optional[str] = None
    current_year: Optional[str] = None
    graduation_year: Optional[int] = None
    subjects: List[Any] = Field(default_factory=list)


class LearningPreferencesInfo(CamelModel):
    daily_study_hours: Optional[str] = None
    learning_depth: Optional[str] = None


class SettingsProfileResponse(CamelModel):
    account: AccountProfileInfo
    learner: LearnerProfileInfo
    academic: AcademicProfileInfo
    learning_preferences: LearningPreferencesInfo


class AccountProfileUpdate(CamelModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=32)
    bio: Optional[str] = Field(default=None, max_length=1000)
    avatar_url: Optional[str] = None
    timezone: Optional[str] = Field(default=None, max_length=64)


class LearnerProfileUpdate(CamelModel):
    primary_goal: Optional[str] = Field(default=None, max_length=255)
    target_skills: Optional[List[Any]] = None
    skills: Optional[List[Any]] = None
    experience: Optional[str] = None
    research: Optional[str] = None


class AcademicProfileUpdate(CamelModel):
    academic_status: Optional[str] = Field(default=None, max_length=50)
    university: Optional[str] = Field(default=None, max_length=255)
    degree_program: Optional[str] = Field(default=None, max_length=255)
    domain: Optional[str] = Field(default=None, max_length=255)
    current_year: Optional[str] = Field(default=None, max_length=50)
    graduation_year: Optional[int] = Field(default=None, ge=1950, le=2100)
    subjects: Optional[List[Any]] = None


class LearningPreferencesUpdate(CamelModel):
    daily_study_hours: Optional[str] = Field(default=None, max_length=50)
    learning_depth: Optional[str] = Field(default=None, max_length=50)


class SettingsProfileUpdateRequest(CamelModel):
    account: Optional[AccountProfileUpdate] = None
    learner: Optional[LearnerProfileUpdate] = None
    academic: Optional[AcademicProfileUpdate] = None
    learning_preferences: Optional[LearningPreferencesUpdate] = None


class AvatarUploadResponse(CamelModel):
    avatar_url: str


# ------------------------------------------------------------------------------
# AI Context Inspection
# ------------------------------------------------------------------------------

class ActiveSyllabusSummary(CamelModel):
    id: Optional[str] = None
    file_name: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    subjects_count: int = 0
    subject_names: List[str] = Field(default_factory=list)


class ActiveRoadmapSummary(CamelModel):
    id: Optional[str] = None
    scope: Optional[str] = None
    version: Optional[int] = None
    total_missions: int = 0
    completed_missions: int = 0


class SettingsContextResponse(CamelModel):
    plan_tier: str = "FREE"
    ai_personalization_enabled: bool = True
    learner: Dict[str, Any] = Field(default_factory=dict)
    education: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    active_syllabus: Optional[ActiveSyllabusSummary] = None
    active_roadmap: Optional[ActiveRoadmapSummary] = None
    memory_summary: Dict[str, Any] = Field(default_factory=dict)


# ------------------------------------------------------------------------------
# Read-Only Files Management
# ------------------------------------------------------------------------------

class SettingsFileItem(CamelModel):
    id: str
    category: FileCategory
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: Optional[str] = None
    subject: Optional[str] = None
    project_title: Optional[str] = None
    artifact_title: Optional[str] = None
    version: Optional[int] = None
    overall_score: Optional[float] = None
    storage_key: Optional[str] = None
    download_endpoint: str
    created_at: Optional[datetime] = None


class SettingsFilesResponse(CamelModel):
    files: List[SettingsFileItem] = Field(default_factory=list)
    total: int = 0
    counts_by_category: Dict[str, int] = Field(default_factory=dict)


class SettingsFileDownloadResponse(CamelModel):
    url: str
    expires_in: Optional[int] = None
    is_api_export: bool = False
    file_name: str


# ------------------------------------------------------------------------------
# Notification & Privacy Preferences
# ------------------------------------------------------------------------------

class UserPreferencesResponse(CamelModel):
    email_notifications: bool = True
    study_reminders: bool = True
    product_updates: bool = False
    ai_personalization_enabled: bool = True
    updated_at: Optional[datetime] = None


class UserPreferencesUpdateRequest(CamelModel):
    email_notifications: Optional[bool] = None
    study_reminders: Optional[bool] = None
    product_updates: Optional[bool] = None
    ai_personalization_enabled: Optional[bool] = None


# ------------------------------------------------------------------------------
# Account Overview & Immediate Hard-Delete
# ------------------------------------------------------------------------------

class ActiveSubscriptionSummary(CamelModel):
    current_plan: str
    billing_cycle: Optional[str] = None
    status: str
    current_period_end: Optional[datetime] = None
    days_remaining: Optional[int] = None


class SettingsAccountResponse(CamelModel):
    user_id: str
    email: str = ""
    email_verified: bool = False
    mfa_enabled: bool = False
    auth_providers: List[str] = Field(default_factory=list)
    has_password_auth: bool = False
    active_subscription: Optional[ActiveSubscriptionSummary] = None


class DeleteAccountRequest(CamelModel):
    confirmation_text: str = Field(..., min_length=1)
    current_password: Optional[str] = None
    totp_code: Optional[str] = None


class DeleteAccountResponse(CamelModel):
    success: bool
    message: str


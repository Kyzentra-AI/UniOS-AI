from __future__ import annotations
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.deps import get_current_user
from app.schemas.settings import (
    AvatarUploadResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
    FileCategory,
    SettingsAccountResponse,
    SettingsContextResponse,
    SettingsFileDownloadResponse,
    SettingsFilesResponse,
    SettingsProfileResponse,
    SettingsProfileUpdateRequest,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
)
from app.services.settings_service import settings_service

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])
security = HTTPBearer()


@router.get("/profile", response_model=SettingsProfileResponse)
async def get_settings_profile(current_user: dict = Depends(get_current_user)):
    """Returns unified account, learner, academic, and learning preference profile."""
    return settings_service.get_profile(
        user_id=current_user["user_id"],
        fallback_email=current_user.get("email", ""),
    )


@router.patch("/profile", response_model=SettingsProfileResponse)
async def update_settings_profile(
    payload: SettingsProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Partially updates account, learner, academic, or learning preference fields."""
    return settings_service.update_profile(
        user_id=current_user["user_id"],
        fallback_email=current_user.get("email", ""),
        payload=payload,
    )


@router.post("/profile/avatar", response_model=AvatarUploadResponse)
async def upload_profile_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Uploads and sets a JPEG/PNG/WebP profile avatar (max 2 MB)."""
    file_bytes = await file.read()
    return settings_service.upload_avatar(
        user_id=current_user["user_id"],
        file_bytes=file_bytes,
        content_type=file.content_type or "",
    )


@router.get("/context", response_model=SettingsContextResponse)
async def get_settings_context(current_user: dict = Depends(get_current_user)):
    """Returns a read-only summary of the learner's assembled ContextV2."""
    return await settings_service.get_context_summary(current_user["user_id"])


@router.get("/files", response_model=SettingsFilesResponse)
async def list_settings_files(
    category: FileCategory = FileCategory.ALL,
    current_user: dict = Depends(get_current_user),
):
    """Read-only listing of user syllabi, build artifacts, resumes, and ATS analyses."""
    return settings_service.list_files(
        user_id=current_user["user_id"],
        category=category,
    )


@router.get("/files/{category}/{file_id}/download", response_model=SettingsFileDownloadResponse)
async def get_settings_file_download(
    category: FileCategory,
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Returns a short-lived signed download URL (or PDF export route) for an owned file."""
    return settings_service.get_file_download(
        user_id=current_user["user_id"],
        category=category,
        file_id=file_id,
    )


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_settings_preferences(current_user: dict = Depends(get_current_user)):
    """Returns notification and AI personalization privacy preferences."""
    return settings_service.get_preferences(current_user["user_id"])


@router.patch("/preferences", response_model=UserPreferencesResponse)
async def update_settings_preferences(
    payload: UserPreferencesUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Updates notification and AI personalization privacy preferences."""
    return settings_service.update_preferences(current_user["user_id"], payload)


@router.get("/account", response_model=SettingsAccountResponse)
async def get_settings_account(current_user: dict = Depends(get_current_user)):
    """Returns auth provider info, MFA status, and active subscription summary."""
    return settings_service.get_account_overview(
        user_id=current_user["user_id"],
        fallback_email=current_user.get("email", ""),
    )


@router.post("/account/delete", response_model=DeleteAccountResponse)
async def delete_account(
    payload: DeleteAccountRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: dict = Depends(get_current_user),
):
    """Permanently hard-deletes the user's account, DB rows, and Supabase Storage files."""
    return await settings_service.delete_account(
        user_id=current_user["user_id"],
        access_token=credentials.credentials,
        fallback_email=current_user.get("email", ""),
        payload=payload,
    )


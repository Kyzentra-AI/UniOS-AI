from __future__ import annotations
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from app.core.context_v2_assembler import ContextV2Assembler
from app.core.supabase import supabase_admin
from app.core.supabase_api import supabase_auth_api
from app.schemas.settings import (
    AcademicProfileInfo,
    AccountProfileInfo,
    ActiveRoadmapSummary,
    ActiveSubscriptionSummary,
    ActiveSyllabusSummary,
    AvatarUploadResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
    FileCategory,
    LearnerProfileInfo,
    LearningPreferencesInfo,
    SettingsAccountResponse,
    SettingsContextResponse,
    SettingsFileDownloadResponse,
    SettingsFileItem,
    SettingsFilesResponse,
    SettingsProfileResponse,
    SettingsProfileUpdateRequest,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
)
from app.services.billing.billing_service import billing_service
from app.services.event_service import event_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB


def _parse_dt(val: Any) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _validate_avatar_bytes(file_bytes: bytes, content_type: str) -> tuple[str, str]:
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded avatar file is empty.")
    if len(file_bytes) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar size exceeds 2 MB limit.")

    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "jpg", "image/jpeg"
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image/png"
    if len(file_bytes) >= 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return "webp", "image/webp"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported avatar format. Please upload a JPEG, PNG, or WebP image.",
    )


class SettingsService:
    """Service layer for Settings: Profile, AI Context, Read-Only Files, Preferences & Account Deletion."""

    @staticmethod
    def _get_or_create_learner(user_id: str) -> Dict[str, Any]:
        res = supabase_admin.table("learner_profiles").select("*").eq("user_id", user_id).execute()
        if res and isinstance(res.data, list) and res.data:
            return res.data[0]
        insert_res = supabase_admin.table("learner_profiles").insert({
            "user_id": user_id,
            "onboarding_status": "NOT_STARTED",
            "onboarding_version": 1,
        }).execute()
        if insert_res and isinstance(insert_res.data, list) and insert_res.data:
            return insert_res.data[0]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learner profile not found")

    @staticmethod
    def _get_user_row(user_id: str) -> Dict[str, Any]:
        res = supabase_admin.table("users").select("*").eq("user_id", user_id).execute()
        return res.data[0] if (res and isinstance(res.data, list) and res.data) else {}

    def get_profile(self, user_id: str, fallback_email: str = "") -> SettingsProfileResponse:
        user_row = self._get_user_row(user_id)
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])

        acad_res = supabase_admin.table("academic_profiles").select("*").eq("learner_profile_id", learner_id).execute()
        acad_row = acad_res.data[0] if (acad_res and isinstance(acad_res.data, list) and acad_res.data) else {}

        pref_res = supabase_admin.table("learning_preferences").select("*").eq("learner_profile_id", learner_id).execute()
        pref_row = pref_res.data[0] if (pref_res and isinstance(pref_res.data, list) and pref_res.data) else {}

        return SettingsProfileResponse(
            account=AccountProfileInfo(
                user_id=user_id,
                full_name=user_row.get("full_name") or "",
                email=user_row.get("email") or fallback_email or "",
                email_verified=bool(user_row.get("email_verified", False)),
                phone=user_row.get("phone"),
                bio=user_row.get("bio"),
                avatar_url=user_row.get("avatar_url"),
                timezone=user_row.get("timezone") or "Asia/Kolkata",
                registration_date=_parse_dt(user_row.get("registration_date")),
                last_login=_parse_dt(user_row.get("last_login")),
            ),
            learner=LearnerProfileInfo(
                learner_id=learner_id,
                primary_goal=learner_row.get("primary_goal"),
                target_skills=learner_row.get("target_skills") or [],
                skills=learner_row.get("skills") or [],
                experience=learner_row.get("experience"),
                research=learner_row.get("research"),
                onboarding_status=learner_row.get("onboarding_status") or "NOT_STARTED",
            ),
            academic=AcademicProfileInfo(
                academic_status=acad_row.get("academic_status"),
                university=acad_row.get("university"),
                degree_program=acad_row.get("degree_program"),
                domain=acad_row.get("domain"),
                current_year=acad_row.get("current_year"),
                graduation_year=acad_row.get("graduation_year"),
                subjects=acad_row.get("subjects") or [],
            ),
            learning_preferences=LearningPreferencesInfo(
                daily_study_hours=pref_row.get("daily_study_hours"),
                learning_depth=pref_row.get("learning_depth"),
            ),
        )

    def update_profile(
        self,
        user_id: str,
        fallback_email: str,
        payload: SettingsProfileUpdateRequest,
    ) -> SettingsProfileResponse:
        now_iso = datetime.now(timezone.utc).isoformat()
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])

        if payload.account:
            acc_updates = payload.account.model_dump(exclude_unset=True)
            if acc_updates:
                acc_updates["updated_at"] = now_iso
                supabase_admin.table("users").update(acc_updates).eq("user_id", user_id).execute()

        if payload.learner:
            lr_updates = payload.learner.model_dump(exclude_unset=True)
            if lr_updates:
                lr_updates["updated_at"] = now_iso
                supabase_admin.table("learner_profiles").update(lr_updates).eq("id", learner_id).execute()

        if payload.academic:
            ac_updates = payload.academic.model_dump(exclude_unset=True)
            if ac_updates:
                ac_updates["updated_at"] = now_iso
                existing_ac = supabase_admin.table("academic_profiles").select("id").eq("learner_profile_id", learner_id).execute()
                if existing_ac and existing_ac.data:
                    supabase_admin.table("academic_profiles").update(ac_updates).eq("learner_profile_id", learner_id).execute()
                else:
                    ac_updates["learner_profile_id"] = learner_id
                    supabase_admin.table("academic_profiles").insert(ac_updates).execute()

        if payload.learning_preferences:
            lp_updates = payload.learning_preferences.model_dump(exclude_unset=True)
            if lp_updates:
                lp_updates["updated_at"] = now_iso
                existing_lp = supabase_admin.table("learning_preferences").select("id").eq("learner_profile_id", learner_id).execute()
                if existing_lp and existing_lp.data:
                    supabase_admin.table("learning_preferences").update(lp_updates).eq("learner_profile_id", learner_id).execute()
                else:
                    lp_updates["learner_profile_id"] = learner_id
                    supabase_admin.table("learning_preferences").insert(lp_updates).execute()

        try:
            event_service.record_event(learner_id, "PROFILE_UPDATED", "LEARNER_PROFILE", learner_id)
        except Exception:
            pass

        return self.get_profile(user_id, fallback_email)

    def upload_avatar(self, user_id: str, file_bytes: bytes, content_type: str = "") -> AvatarUploadResponse:
        ext, mime = _validate_avatar_bytes(file_bytes, content_type)
        _, public_url = storage_service.upload_avatar(user_id, file_bytes, ext, mime)
        supabase_admin.table("users").update({
            "avatar_url": public_url,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("user_id", user_id).execute()
        return AvatarUploadResponse(avatar_url=public_url)

    def get_preferences(self, user_id: str) -> UserPreferencesResponse:
        res = supabase_admin.table("user_settings").select("*").eq("user_id", user_id).execute()
        if res and isinstance(res.data, list) and res.data:
            row = res.data[0]
        else:
            now_iso = datetime.now(timezone.utc).isoformat()
            defaults = {
                "user_id": user_id,
                "email_notifications": True,
                "study_reminders": True,
                "product_updates": False,
                "ai_personalization_enabled": True,
                "created_at": now_iso,
                "updated_at": now_iso,
            }
            ins = supabase_admin.table("user_settings").insert(defaults).execute()
            row = ins.data[0] if (ins and isinstance(ins.data, list) and ins.data) else defaults

        return UserPreferencesResponse(
            email_notifications=bool(row.get("email_notifications", True)),
            study_reminders=bool(row.get("study_reminders", True)),
            product_updates=bool(row.get("product_updates", False)),
            ai_personalization_enabled=bool(row.get("ai_personalization_enabled", True)),
            updated_at=_parse_dt(row.get("updated_at")),
        )

    def update_preferences(self, user_id: str, payload: UserPreferencesUpdateRequest) -> UserPreferencesResponse:
        # Ensure row exists first
        self.get_preferences(user_id)
        updates = payload.model_dump(exclude_unset=True)
        if updates:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            supabase_admin.table("user_settings").update(updates).eq("user_id", user_id).execute()
        return self.get_preferences(user_id)

    async def get_context_summary(self, user_id: str) -> SettingsContextResponse:
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])
        prefs = self.get_preferences(user_id)

        context = await ContextV2Assembler.assemble(learner_id, scope="ACADEMIC")

        # Syllabus summary
        active_syllabus = None
        try:
            syl_res = (
                supabase_admin.table("syllabus_documents")
                .select("id, file_name, confirmed_at, parsed_content")
                .eq("learner_id", learner_id)
                .eq("status", "CONFIRMED")
                .order("confirmed_at", desc=True)
                .limit(1)
                .execute()
            )
            if syl_res and isinstance(syl_res.data, list) and syl_res.data:
                s = syl_res.data[0]
                subjects = (s.get("parsed_content") or {}).get("subjects") or []
                subj_names = [str(item.get("name")) for item in subjects if isinstance(item, dict) and item.get("name")]
                active_syllabus = ActiveSyllabusSummary(
                    id=str(s["id"]),
                    file_name=s.get("file_name"),
                    confirmed_at=_parse_dt(s.get("confirmed_at")),
                    subjects_count=len(subj_names),
                    subject_names=subj_names,
                )
        except Exception:
            pass

        # Active roadmap summary
        active_roadmap = None
        try:
            rm_res = (
                supabase_admin.table("roadmaps")
                .select("id, scope, version")
                .eq("learner_id", learner_id)
                .eq("status", "ACTIVE")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if rm_res and isinstance(rm_res.data, list) and rm_res.data:
                r = rm_res.data[0]
                m_res = supabase_admin.table("missions").select("status").eq("roadmap_id", r["id"]).execute()
                missions = m_res.data if (m_res and isinstance(m_res.data, list)) else []
                active_roadmap = ActiveRoadmapSummary(
                    id=str(r["id"]),
                    scope=r.get("scope"),
                    version=r.get("version"),
                    total_missions=len(missions),
                    completed_missions=sum(1 for m in missions if m.get("status") == "COMPLETED"),
                )
        except Exception:
            pass

        return SettingsContextResponse(
            plan_tier=context.get("plan_tier", "FREE"),
            ai_personalization_enabled=prefs.ai_personalization_enabled,
            learner=context.get("learner") or {},
            education=context.get("education") or {},
            preferences=context.get("preferences") or {},
            active_syllabus=active_syllabus,
            active_roadmap=active_roadmap,
            memory_summary=context.get("memory_summary") or {},
        )

    def list_files(self, user_id: str, category: FileCategory = FileCategory.ALL) -> SettingsFilesResponse:
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])
        files: List[SettingsFileItem] = []

        # 1. Syllabi PDFs
        if category in (FileCategory.ALL, FileCategory.SYLLABUS):
            syl_res = (
                supabase_admin.table("syllabus_documents")
                .select("id, file_name, file_type, status, subject, storage_key, created_at")
                .eq("learner_id", learner_id)
                .order("created_at", desc=True)
                .execute()
            )
            for row in (syl_res.data or []) if syl_res else []:
                fid = str(row["id"])
                files.append(
                    SettingsFileItem(
                        id=fid,
                        category=FileCategory.SYLLABUS,
                        file_name=row.get("file_name") or "syllabus.pdf",
                        file_type=row.get("file_type") or "application/pdf",
                        status=row.get("status"),
                        subject=row.get("subject"),
                        storage_key=row.get("storage_key"),
                        download_endpoint=f"/api/v1/settings/files/SYLLABUS/{fid}/download",
                        created_at=_parse_dt(row.get("created_at")),
                    )
                )

        # 2. Build Project Artifact Versions
        if category in (FileCategory.ALL, FileCategory.BUILD_ARTIFACT):
            proj_res = supabase_admin.table("build_projects").select("id, title").eq("learner_id", learner_id).execute()
            proj_map = {str(p["id"]): p.get("title") for p in (proj_res.data or [])} if proj_res else {}
            if proj_map:
                art_res = supabase_admin.table("build_artifacts").select("id, project_id, title").in_("project_id", list(proj_map.keys())).execute()
                art_map = {str(a["id"]): a for a in (art_res.data or [])} if art_res else {}
                if art_map:
                    ver_res = (
                        supabase_admin.table("build_artifact_versions")
                        .select("id, artifact_id, version, file_name, file_size, storage_key, created_at")
                        .in_("artifact_id", list(art_map.keys()))
                        .order("created_at", desc=True)
                        .execute()
                    )
                    for row in (ver_res.data or []) if ver_res else []:
                        art = art_map.get(str(row.get("artifact_id")), {})
                        vid = str(row["id"])
                        files.append(
                            SettingsFileItem(
                                id=vid,
                                category=FileCategory.BUILD_ARTIFACT,
                                file_name=row.get("file_name") or f"{art.get('title', 'artifact')}_v{row.get('version', 1)}",
                                file_size=row.get("file_size"),
                                project_title=proj_map.get(str(art.get("project_id"))),
                                artifact_title=art.get("title"),
                                version=row.get("version"),
                                storage_key=row.get("storage_key"),
                                download_endpoint=f"/api/v1/settings/files/BUILD_ARTIFACT/{vid}/download",
                                created_at=_parse_dt(row.get("created_at")),
                            )
                        )

        # 3. Launch Resumes
        if category in (FileCategory.ALL, FileCategory.RESUME):
            res_list = (
                supabase_admin.table("launch_resumes")
                .select("id, title, status, created_at")
                .eq("learner_id", learner_id)
                .order("created_at", desc=True)
                .execute()
            )
            for row in (res_list.data or []) if res_list else []:
                rid = str(row["id"])
                title = row.get("title") or "Untitled Resume"
                files.append(
                    SettingsFileItem(
                        id=rid,
                        category=FileCategory.RESUME,
                        file_name=f"{title}.pdf",
                        file_type="application/pdf",
                        status=row.get("status"),
                        download_endpoint=f"/api/v1/settings/files/RESUME/{rid}/download",
                        created_at=_parse_dt(row.get("created_at")),
                    )
                )

        # 4. Launch ATS Analyses
        if category in (FileCategory.ALL, FileCategory.ATS):
            ats_res = (
                supabase_admin.table("launch_ats_analyses")
                .select("id, file_name, file_type, overall_score, created_at")
                .eq("learner_id", learner_id)
                .order("created_at", desc=True)
                .execute()
            )
            for row in (ats_res.data or []) if ats_res else []:
                aid = str(row["id"])
                files.append(
                    SettingsFileItem(
                        id=aid,
                        category=FileCategory.ATS,
                        file_name=row.get("file_name") or "resume_ats_check",
                        file_type=row.get("file_type"),
                        overall_score=float(row["overall_score"]) if row.get("overall_score") is not None else None,
                        download_endpoint=f"/api/v1/settings/files/ATS/{aid}/download",
                        created_at=_parse_dt(row.get("created_at")),
                    )
                )

        files.sort(
            key=lambda f: f.created_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        counts: Dict[str, int] = {
            "SYLLABUS": sum(1 for f in files if f.category == FileCategory.SYLLABUS),
            "BUILD_ARTIFACT": sum(1 for f in files if f.category == FileCategory.BUILD_ARTIFACT),
            "RESUME": sum(1 for f in files if f.category == FileCategory.RESUME),
            "ATS": sum(1 for f in files if f.category == FileCategory.ATS),
        }
        return SettingsFilesResponse(files=files, total=len(files), counts_by_category=counts)

    def get_file_download(self, user_id: str, category: FileCategory, file_id: str) -> SettingsFileDownloadResponse:
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])

        if category == FileCategory.SYLLABUS:
            res = supabase_admin.table("syllabus_documents").select("id, learner_id, file_name, storage_key").eq("id", file_id).execute()
            if not res or not res.data:
                raise HTTPException(status_code=404, detail="Syllabus file not found")
            row = res.data[0]
            if str(row["learner_id"]) != learner_id:
                raise HTTPException(status_code=403, detail="Forbidden")
            if not row.get("storage_key"):
                raise HTTPException(status_code=404, detail="No stored file object for this syllabus")
            signed_url = storage_service.create_signed_url(storage_service.BUCKET_NAME, row["storage_key"], expires_in=300)
            return SettingsFileDownloadResponse(
                url=signed_url,
                expires_in=300,
                is_api_export=False,
                file_name=row.get("file_name") or "syllabus.pdf",
            )

        if category == FileCategory.BUILD_ARTIFACT:
            ver_res = supabase_admin.table("build_artifact_versions").select("id, artifact_id, file_name, storage_key").eq("id", file_id).execute()
            if not ver_res or not ver_res.data:
                raise HTTPException(status_code=404, detail="Artifact version not found")
            ver = ver_res.data[0]
            art_res = supabase_admin.table("build_artifacts").select("project_id").eq("id", ver["artifact_id"]).execute()
            if not art_res or not art_res.data:
                raise HTTPException(status_code=404, detail="Parent artifact not found")
            proj_res = supabase_admin.table("build_projects").select("learner_id").eq("id", art_res.data[0]["project_id"]).execute()
            if not proj_res or not proj_res.data or str(proj_res.data[0]["learner_id"]) != learner_id:
                raise HTTPException(status_code=403, detail="Forbidden")
            if not ver.get("storage_key"):
                raise HTTPException(status_code=404, detail="No stored file object for this artifact version")
            signed_url = storage_service.create_signed_url(storage_service.BUCKET_NAME, ver["storage_key"], expires_in=300)
            return SettingsFileDownloadResponse(
                url=signed_url,
                expires_in=300,
                is_api_export=False,
                file_name=ver.get("file_name") or "artifact",
            )

        if category == FileCategory.RESUME:
            res = supabase_admin.table("launch_resumes").select("id, learner_id, title").eq("id", file_id).execute()
            if not res or not res.data:
                raise HTTPException(status_code=404, detail="Resume not found")
            row = res.data[0]
            if str(row["learner_id"]) != learner_id:
                raise HTTPException(status_code=403, detail="Forbidden")
            title = row.get("title") or "resume"
            return SettingsFileDownloadResponse(
                url=f"/api/v1/launch/resumes/{file_id}/export",
                expires_in=None,
                is_api_export=True,
                file_name=f"{title}.pdf",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Download URLs are supported for SYLLABUS, BUILD_ARTIFACT, and RESUME files.",
        )

    def _inspect_auth_user(self, user_id: str) -> tuple[List[str], bool, bool]:
        """Returns (auth_providers, has_password_auth, has_verified_totp)."""
        providers: List[str] = []
        has_verified_totp = False
        try:
            admin_res = supabase_admin.auth.admin.get_user_by_id(user_id)
            auth_user = getattr(admin_res, "user", None)
            if auth_user:
                for ident in getattr(auth_user, "identities", []) or []:
                    prov = getattr(ident, "provider", None) or (ident.get("provider") if isinstance(ident, dict) else None)
                    if prov and prov not in providers:
                        providers.append(prov)
                app_meta = getattr(auth_user, "app_metadata", {}) or {}
                if isinstance(app_meta, dict):
                    for prov in app_meta.get("providers") or []:
                        if prov not in providers:
                            providers.append(prov)
                factors = getattr(auth_user, "factors", []) or []
                has_verified_totp = any(
                    getattr(f, "factor_type", None) == "totp" and getattr(f, "status", None) == "verified"
                    for f in factors
                )
        except Exception as exc:
            logger.warning(f"Could not inspect Supabase auth user {user_id}: {exc}")

        if not providers:
            providers = ["email"]
        has_password_auth = "email" in providers
        return providers, has_password_auth, has_verified_totp

    def get_account_overview(self, user_id: str, fallback_email: str = "") -> SettingsAccountResponse:
        user_row = self._get_user_row(user_id)
        learner_row = self._get_or_create_learner(user_id)
        learner_id = str(learner_row["id"])

        providers, has_password_auth, has_verified_totp = self._inspect_auth_user(user_id)
        mfa_enabled = bool(user_row.get("mfa_enabled", False)) or has_verified_totp

        active_sub = None
        try:
            ent = billing_service.get_or_create_entitlement(learner_id)
            active_sub = ActiveSubscriptionSummary(
                current_plan=ent.current_plan.value,
                billing_cycle=ent.billing_cycle.value,
                status=ent.status.value,
                current_period_end=ent.current_period_end,
                days_remaining=ent.days_remaining,
            )
        except Exception:
            pass

        return SettingsAccountResponse(
            user_id=user_id,
            email=user_row.get("email") or fallback_email or "",
            email_verified=bool(user_row.get("email_verified", False)),
            mfa_enabled=mfa_enabled,
            auth_providers=providers,
            has_password_auth=has_password_auth,
            active_subscription=active_sub,
        )

    async def delete_account(
        self,
        user_id: str,
        access_token: str,
        fallback_email: str,
        payload: DeleteAccountRequest,
    ) -> DeleteAccountResponse:
        # 1. Typed confirmation check
        if payload.confirmation_text.strip() != "DELETE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation text must exactly match 'DELETE'.",
            )

        user_row = self._get_user_row(user_id)
        email = user_row.get("email") or fallback_email
        providers, has_password_auth, has_verified_totp = self._inspect_auth_user(user_id)
        mfa_enabled = bool(user_row.get("mfa_enabled", False)) or has_verified_totp

        # 2. Password verification for email/password accounts
        if has_password_auth:
            if not payload.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to delete an email/password account.",
                )
            try:
                await supabase_auth_api.sign_in(email, payload.current_password)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect.",
                )

        # 3. MFA TOTP verification when enabled
        if mfa_enabled:
            if not payload.totp_code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="MFA_REQUIRED: Please provide your 6-digit authenticator code (totpCode).",
                )
            try:
                admin_res = supabase_admin.auth.admin.get_user_by_id(user_id)
                factors = getattr(getattr(admin_res, "user", None), "factors", []) or []
                totp_factor = next(
                    (f for f in factors if getattr(f, "factor_type", None) == "totp" and getattr(f, "status", None) == "verified"),
                    None,
                )
                if totp_factor:
                    challenge = await supabase_auth_api.mfa_challenge(access_token, totp_factor.id)
                    await supabase_auth_api.mfa_verify(access_token, totp_factor.id, challenge.get("id"), payload.totp_code)
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid MFA verification code.",
                )

        # 4. Collect all Supabase Storage keys BEFORE DB cascade removes metadata
        storage_keys: List[str] = []
        avatar_keys: List[str] = []
        try:
            learner_res = supabase_admin.table("learner_profiles").select("id").eq("user_id", user_id).execute()
            if learner_res and isinstance(learner_res.data, list) and learner_res.data:
                learner_id = str(learner_res.data[0]["id"])
                syl_res = supabase_admin.table("syllabus_documents").select("storage_key").eq("learner_id", learner_id).execute()
                for row in (syl_res.data or []) if syl_res else []:
                    if row.get("storage_key"):
                        storage_keys.append(str(row["storage_key"]))

                proj_res = supabase_admin.table("build_projects").select("id").eq("learner_id", learner_id).execute()
                proj_ids = [str(p["id"]) for p in (proj_res.data or [])] if proj_res else []
                if proj_ids:
                    art_res = supabase_admin.table("build_artifacts").select("id").in_("project_id", proj_ids).execute()
                    art_ids = [str(a["id"]) for a in (art_res.data or [])] if art_res else []
                    if art_ids:
                        ver_res = supabase_admin.table("build_artifact_versions").select("storage_key").in_("artifact_id", art_ids).execute()
                        for row in (ver_res.data or []) if ver_res else []:
                            if row.get("storage_key"):
                                storage_keys.append(str(row["storage_key"]))
        except Exception as exc:
            logger.warning(f"Error collecting storage keys during account deletion for {user_id}: {exc}")

        avatar_url = user_row.get("avatar_url") or ""
        if "/avatars/" in avatar_url:
            rel_path = avatar_url.split("/avatars/", 1)[-1].split("?", 1)[0]
            avatar_keys.append(rel_path)

        # 5. Purge Storage objects immediately
        storage_service.delete_files(storage_service.BUCKET_NAME, storage_keys)
        storage_service.delete_files(storage_service.AVATARS_BUCKET, avatar_keys)

        # 6. Hard-delete auth.users (cascades public.users -> learner_profiles -> all child tables)
        try:
            supabase_admin.auth.admin.delete_user(user_id)
        except Exception as exc:
            logger.error(f"Failed to delete Supabase auth user {user_id}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to permanently delete user account.",
            )

        # Defensive fallback cleanup on public.users in case cascade trigger wasn't linked
        try:
            supabase_admin.table("users").delete().eq("user_id", user_id).execute()
        except Exception:
            pass

        return DeleteAccountResponse(
            success=True,
            message="Your account and all associated data have been permanently deleted.",
        )


settings_service = SettingsService()


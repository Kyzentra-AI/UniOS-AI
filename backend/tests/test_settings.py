from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.core.context_v2_assembler import ContextV2Assembler
from app.core.deps import get_current_user
from app.main import app


TEST_USER_ID = "00000000-0000-0000-0000-000000000101"
TEST_LEARNER_ID = "00000000-0000-0000-0000-000000000202"


@pytest.fixture
def auth_client():
    prev = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": TEST_USER_ID,
        "email": "student@unios.ai",
        "role": "learner",
        "payload": {},
    }
    with TestClient(app) as c:
        yield c
    if prev is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = prev


def test_get_and_patch_settings_profile(auth_client):
    user_row = {
        "user_id": TEST_USER_ID,
        "full_name": "Aarav Sharma",
        "email": "student@unios.ai",
        "email_verified": True,
        "phone": None,
        "bio": None,
        "avatar_url": None,
        "timezone": "Asia/Kolkata",
    }
    learner_row = {
        "id": TEST_LEARNER_ID,
        "user_id": TEST_USER_ID,
        "primary_goal": "Business Analyst",
        "target_skills": ["Excel"],
        "skills": ["Management"],
        "onboarding_status": "COMPLETED",
    }
    acad_row = {
        "learner_profile_id": TEST_LEARNER_ID,
        "academic_status": "BACHELOR",
        "university": "Delhi University",
        "degree_program": "BBA",
        "domain": "Business Management",
        "current_year": "1",
        "graduation_year": 2029,
        "subjects": ["Principles of Management"],
    }
    pref_row = {
        "learner_profile_id": TEST_LEARNER_ID,
        "daily_study_hours": "2_3",
        "learning_depth": "BALANCED",
    }

    with patch("app.services.settings_service.supabase_admin") as mock_db, \
         patch("app.services.settings_service.event_service.record_event"):
        def table_router(name):
            t = MagicMock()
            if name == "users":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[user_row])
                def upd_user(vals):
                    user_row.update({k: v for k, v in vals.items() if k != "updated_at"})
                    m = MagicMock()
                    m.eq.return_value.execute.return_value = MagicMock(data=[user_row])
                    return m
                t.update.side_effect = upd_user
            elif name == "learner_profiles":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[learner_row])
                def upd_lr(vals):
                    learner_row.update({k: v for k, v in vals.items() if k != "updated_at"})
                    m = MagicMock()
                    m.eq.return_value.execute.return_value = MagicMock(data=[learner_row])
                    return m
                t.update.side_effect = upd_lr
            elif name == "academic_profiles":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[acad_row])
                def upd_ac(vals):
                    acad_row.update({k: v for k, v in vals.items() if k != "updated_at"})
                    m = MagicMock()
                    m.eq.return_value.execute.return_value = MagicMock(data=[acad_row])
                    return m
                t.update.side_effect = upd_ac
            elif name == "learning_preferences":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[pref_row])
            return t

        mock_db.table.side_effect = table_router

        resp = auth_client.get("/api/v1/settings/profile")
        assert resp.status_code == 200
        assert resp.json()["account"]["fullName"] == "Aarav Sharma"
        assert resp.json()["academic"]["degreeProgram"] == "BBA"

        patch_resp = auth_client.patch(
            "/api/v1/settings/profile",
            json={
                "account": {"fullName": "Aarav S.", "bio": "BBA Sem 1", "email": "hacked@evil.com"},
                "academic": {"university": "Mumbai University"},
            },
        )
        assert patch_resp.status_code == 200
        body = patch_resp.json()
        assert body["account"]["fullName"] == "Aarav S."
        assert body["account"]["bio"] == "BBA Sem 1"
        # Email cannot be overwritten via profile PATCH
        assert body["account"]["email"] == "student@unios.ai"
        assert body["academic"]["university"] == "Mumbai University"


def test_avatar_upload_validation_and_success(auth_client):
    # Invalid bytes rejected
    bad_resp = auth_client.post(
        "/api/v1/settings/profile/avatar",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
    )
    assert bad_resp.status_code == 400

    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
    with patch("app.services.settings_service.storage_service.upload_avatar", return_value=("avatars/u/a.png", "https://cdn.example/a.png")), \
         patch("app.services.settings_service.supabase_admin") as mock_db:
        mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{}])
        ok_resp = auth_client.post(
            "/api/v1/settings/profile/avatar",
            files={"file": ("avatar.png", png_bytes, "image/png")},
        )
        assert ok_resp.status_code == 200
        assert ok_resp.json()["avatarUrl"] == "https://cdn.example/a.png"


@pytest.mark.asyncio
async def test_context_v2_respects_ai_personalization_opt_out():
    def table_router(name):
        t = MagicMock()
        if name == "learner_profiles":
            t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"id": TEST_LEARNER_ID, "user_id": TEST_USER_ID, "primary_goal": "Analyst"}]
            )
        elif name == "user_settings":
            t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                data=[{"ai_personalization_enabled": False}]
            )
        else:
            t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            t.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            t.select.return_value.eq.return_value.eq.return_value.eq.return_value.is_.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
            t.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
        return t

    with patch("app.core.context_v2_assembler.supabase_admin.table", side_effect=table_router), \
         patch("app.core.context_v2_assembler.billing_guard.get_plan_tier", return_value="BASIC"), \
         patch("app.core.context_v2_assembler.event_service.get_recent_events") as mock_events, \
         patch("app.core.context_v2_assembler.kie_service.get_memory_summary", new=AsyncMock()) as mock_mem:
        ctx = await ContextV2Assembler.assemble(TEST_LEARNER_ID)
        assert ctx["recent_history"] == []
        assert ctx["memory_summary"] == {}
        mock_events.assert_not_called()
        mock_mem.assert_not_called()


def test_settings_context_and_read_only_files(auth_client):
    # Verify no DELETE route exists under /api/v1/settings/files
    file_delete_routes = [
        r for r in app.routes
        if getattr(r, "path", "").startswith("/api/v1/settings/files") and "DELETE" in getattr(r, "methods", set())
    ]
    assert file_delete_routes == []

    now_iso = datetime.now(timezone.utc).isoformat()
    with patch("app.services.settings_service.supabase_admin") as mock_db, \
         patch("app.services.settings_service.storage_service.create_signed_url", return_value="https://signed.example/syl.pdf"):
        def table_router(name):
            t = MagicMock()
            if name == "learner_profiles":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": TEST_LEARNER_ID, "user_id": TEST_USER_ID}])
            elif name == "syllabus_documents":
                t.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
                    data=[{"id": "syl-1", "file_name": "bba_sem1.pdf", "file_type": "application/pdf", "status": "CONFIRMED", "storage_key": "uploads/s1.pdf", "created_at": now_iso}]
                )
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"id": "syl-1", "learner_id": TEST_LEARNER_ID, "file_name": "bba_sem1.pdf", "storage_key": "uploads/s1.pdf"}]
                )
            elif name == "build_projects":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            elif name == "launch_resumes":
                t.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
                    data=[{"id": "res-1", "title": "BBA_Resume", "status": "final", "created_at": now_iso}]
                )
            elif name == "launch_ats_analyses":
                t.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
                    data=[{"id": "ats-1", "file_name": "cv.pdf", "file_type": "pdf", "overall_score": 84.5, "created_at": now_iso}]
                )
            return t

        mock_db.table.side_effect = table_router

        list_resp = auth_client.get("/api/v1/settings/files")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] == 3
        assert data["countsByCategory"]["SYLLABUS"] == 1
        assert data["countsByCategory"]["RESUME"] == 1
        assert data["countsByCategory"]["ATS"] == 1

        dl_resp = auth_client.get("/api/v1/settings/files/SYLLABUS/syl-1/download")
        assert dl_resp.status_code == 200
        assert dl_resp.json()["url"] == "https://signed.example/syl.pdf"
        assert dl_resp.json()["expiresIn"] == 300


def test_preferences_get_and_update(auth_client):
    pref_row = {
        "user_id": TEST_USER_ID,
        "email_notifications": True,
        "study_reminders": True,
        "product_updates": False,
        "ai_personalization_enabled": True,
    }
    with patch("app.services.settings_service.supabase_admin") as mock_db:
        t = MagicMock()
        t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[pref_row])
        def upd(vals):
            pref_row.update({k: v for k, v in vals.items() if k != "updated_at"})
            m = MagicMock()
            m.eq.return_value.execute.return_value = MagicMock(data=[pref_row])
            return m
        t.update.side_effect = upd
        mock_db.table.return_value = t

        resp = auth_client.patch(
            "/api/v1/settings/preferences",
            json={"productUpdates": True, "aiPersonalizationEnabled": False},
        )
        assert resp.status_code == 200
        assert resp.json()["productUpdates"] is True
        assert resp.json()["aiPersonalizationEnabled"] is False


def test_account_deletion_verification_and_storage_purge(auth_client):
    # 1. Wrong confirmation phrase -> 400
    bad_phrase = auth_client.post(
        "/api/v1/settings/account/delete",
        json={"confirmationText": "delete please"},
        headers={"Authorization": "Bearer tok"},
    )
    assert bad_phrase.status_code == 400

    # 2. Email user with wrong password -> 401
    fake_auth_user = SimpleNamespace(
        user=SimpleNamespace(
            identities=[SimpleNamespace(provider="email")],
            app_metadata={"providers": ["email"]},
            factors=[],
        )
    )
    with patch("app.services.settings_service.supabase_admin") as mock_db, \
         patch("app.services.settings_service.supabase_auth_api.sign_in", new=AsyncMock(side_effect=Exception("Invalid"))):
        mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"user_id": TEST_USER_ID, "email": "student@unios.ai", "mfa_enabled": False}]
        )
        mock_db.auth.admin.get_user_by_id.return_value = fake_auth_user

        bad_pw = auth_client.post(
            "/api/v1/settings/account/delete",
            json={"confirmationText": "DELETE", "currentPassword": "wrong"},
            headers={"Authorization": "Bearer tok"},
        )
        assert bad_pw.status_code == 401

    # 3. Valid email/password + DELETE -> purges storage BEFORE auth.admin.delete_user
    call_order = []
    with patch("app.services.settings_service.supabase_admin") as mock_db, \
         patch("app.services.settings_service.supabase_auth_api.sign_in", new=AsyncMock(return_value={"access_token": "ok"})), \
         patch("app.services.settings_service.storage_service.delete_files", side_effect=lambda b, keys: call_order.append(("purge", b, keys))):
        def table_router(name):
            t = MagicMock()
            if name == "users":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(
                    data=[{"user_id": TEST_USER_ID, "email": "student@unios.ai", "mfa_enabled": False, "avatar_url": "https://x.supabase.co/storage/v1/object/public/avatars/u1/pic.png"}]
                )
            elif name == "learner_profiles":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": TEST_LEARNER_ID}])
            elif name == "syllabus_documents":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"storage_key": "uploads/syl1.pdf"}])
            elif name == "build_projects":
                t.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "proj-1"}])
            elif name == "build_artifacts":
                t.select.return_value.in_.return_value.execute.return_value = MagicMock(data=[{"id": "art-1"}])
            elif name == "build_artifact_versions":
                t.select.return_value.in_.return_value.execute.return_value = MagicMock(data=[{"storage_key": "uploads/art1.zip"}])
            return t

        mock_db.table.side_effect = table_router
        mock_db.auth.admin.get_user_by_id.return_value = fake_auth_user
        mock_db.auth.admin.delete_user.side_effect = lambda uid: call_order.append(("delete_user", uid))

        ok_del = auth_client.post(
            "/api/v1/settings/account/delete",
            json={"confirmationText": "DELETE", "currentPassword": "correct-password"},
            headers={"Authorization": "Bearer tok"},
        )
        assert ok_del.status_code == 200
        assert ok_del.json()["success"] is True
        assert call_order[0] == ("purge", "syllabi", ["uploads/syl1.pdf", "uploads/art1.zip"])
        assert call_order[1] == ("purge", "avatars", ["u1/pic.png"])
        assert call_order[2] == ("delete_user", TEST_USER_ID)


import pytest
import datetime
from datetime import timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_supabase_api():
    with patch("app.api.v1.endpoints.auth.supabase_auth_api") as mock:
        yield mock

@pytest.fixture
def mock_supabase_admin():
    with patch("app.api.v1.endpoints.auth.supabase_admin") as mock:
        yield mock

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to UniOS.ai Auth API" in response.json()["message"]

# --- REGISTRATION TESTS ---

def test_register_invalid_password_complexity():
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "simple",  # missing min length, upper, digit, special char
        "terms_accepted": True
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.text

def test_register_terms_not_accepted():
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePassword123!",
        "terms_accepted": False
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert "You must accept the Terms & Conditions" in response.text

@pytest.mark.asyncio
async def test_register_success(mock_supabase_api):
    mock_supabase_api.sign_up = AsyncMock(return_value={"user": {"id": "user-uuid-123", "email": "john@example.com"}})
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePassword123!",
        "terms_accepted": True
    }
    # Standard sync TestClient handles async endpoints fine in FastAPI
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert "Registration successful" in response.json()["message"]
    mock_supabase_api.sign_up.assert_called_once_with(
        email="john@example.com",
        password="SecurePassword123!",
        full_name="John Doe",
        terms_accepted=True,
        redirect_to="http://localhost:3000/auth/callback"
    )

@pytest.mark.asyncio
async def test_register_success_with_redirect_to(mock_supabase_api):
    mock_supabase_api.sign_up = AsyncMock(return_value={"user": {"id": "user-uuid-123", "email": "john@example.com"}})
    payload = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePassword123!",
        "terms_accepted": True,
        "redirect_to": "http://localhost:3000/auth/callback"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    assert "Registration successful" in response.json()["message"]
    mock_supabase_api.sign_up.assert_called_once_with(
        email="john@example.com",
        password="SecurePassword123!",
        full_name="John Doe",
        terms_accepted=True,
        redirect_to="http://localhost:3000/auth/callback"
    )



# --- RESEND VERIFICATION & EMAIL STATUS TESTS ---

@pytest.mark.asyncio
async def test_resend_verification_success(mock_supabase_api):
    mock_supabase_api.resend_verification = AsyncMock(return_value={})
    payload = {"email": "john@example.com", "redirect_to": "http://localhost:3000/auth/callback"}
    response = client.post("/api/v1/auth/resend-verification", json=payload)
    assert response.status_code == 200
    assert "Verification email resent successfully" in response.json()["message"]
    mock_supabase_api.resend_verification.assert_called_once_with("john@example.com", redirect_to="http://localhost:3000/auth/callback")

@pytest.mark.asyncio
async def test_check_email_status_verified(mock_supabase_admin):
    mock_db_res = MagicMock()
    mock_db_res.data = [{"email": "john@example.com", "email_confirmed_at": "2026-08-20T12:00:00Z"}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    payload = {"email": "john@example.com"}
    response = client.post("/api/v1/auth/check-email-status", json=payload)
    assert response.status_code == 200
    assert response.json()["is_verified"] is True

@pytest.mark.asyncio
async def test_login_unverified_email(mock_supabase_api, mock_supabase_admin):
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 0, "account_locked_until": None}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    mock_supabase_api.sign_in = AsyncMock(side_effect=Exception("Email not confirmed"))
    payload = {"email": "unverified@example.com", "password": "SecurePassword123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"]

# --- LOGIN & LOCKOUT TESTS ---


@pytest.mark.asyncio
async def test_login_success(mock_supabase_api, mock_supabase_admin):
    # Mock profile fetch (no lockout, mfa disabled)
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 0, "account_locked_until": None, "mfa_enabled": False}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    # Mock sign_in response
    mock_supabase_api.sign_in = AsyncMock(return_value={
        "access_token": "valid-jwt",
        "refresh_token": "valid-refresh",
        "expires_in": 3600,
        "user": {"id": "user-uuid-123", "factors": []}
    })

    payload = {"email": "john@example.com", "password": "SecurePassword123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert response.json()["requires_mfa"] is False
    assert response.json()["session"]["access_token"] == "valid-jwt"

    # Verify db reset and last_login was triggered
    mock_supabase_admin.table.assert_called_with("users")
    mock_supabase_admin.table.return_value.update.assert_called_once()

@pytest.mark.asyncio
async def test_login_requires_mfa(mock_supabase_api, mock_supabase_admin):
    # Mock profile fetch (no lockout, mfa disabled in profile but factor in gotrue)
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 0, "account_locked_until": None, "mfa_enabled": False}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    # Mock sign_in response with verified TOTP factor
    mock_supabase_api.sign_in = AsyncMock(return_value={
        "access_token": "aal1-jwt",
        "refresh_token": "valid-refresh",
        "expires_in": 3600,
        "user": {"id": "user-uuid-123", "factors": [{"factor_type": "totp", "status": "verified"}]}
    })

    payload = {"email": "john@example.com", "password": "SecurePassword123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert response.json()["requires_mfa"] is True
    assert response.json()["user_id"] == "user-uuid-123"

@pytest.mark.asyncio
async def test_login_requires_mfa_from_db(mock_supabase_api, mock_supabase_admin):
    # Mock profile fetch: mfa_enabled is True in users table even if GoTrue token user object doesn't list factors
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 0, "account_locked_until": None, "mfa_enabled": True}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    # Mock sign_in response without factors array
    mock_supabase_api.sign_in = AsyncMock(return_value={
        "access_token": "aal1-jwt",
        "refresh_token": "valid-refresh",
        "expires_in": 3600,
        "user": {"id": "user-uuid-123"}
    })

    payload = {"email": "john@example.com", "password": "SecurePassword123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert response.json()["requires_mfa"] is True
    assert response.json()["user_id"] == "user-uuid-123"

@pytest.mark.asyncio
async def test_login_locked_out(mock_supabase_admin):
    # Mock profile fetch: Account is locked out for 15 minutes
    future_time = (datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=10)).isoformat()
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 5, "account_locked_until": future_time}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    payload = {"email": "john@example.com", "password": "SecurePassword123!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 423
    assert "Account is temporarily locked" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_failed_attempts_increment_lockout(mock_supabase_api, mock_supabase_admin):
    # Mock profile fetch: Currently has 4 failed attempts
    mock_db_res = MagicMock()
    mock_db_res.data = [{"user_id": "user-uuid-123", "failed_login_attempts": 4, "account_locked_until": None}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res

    # Mock sign_in throws exception on invalid password
    mock_supabase_api.sign_in = AsyncMock(side_effect=Exception("Invalid login credentials"))

    payload = {"email": "john@example.com", "password": "WrongPassword!"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

    # Verify update called to lock the account (attempts = 5)
    mock_supabase_admin.table.return_value.update.assert_called_once()
    called_update_args = mock_supabase_admin.table.return_value.update.call_args[0][0]
    assert called_update_args["failed_login_attempts"] == 5
    assert "account_locked_until" in called_update_args

# --- FORGOT & RESET PASSWORD TESTS ---

@pytest.mark.asyncio
async def test_forgot_password_success(mock_supabase_api):
    mock_supabase_api.forgot_password = AsyncMock()
    payload = {"email": "john@example.com"}
    response = client.post("/api/v1/auth/forgot-password", json=payload)
    assert response.status_code == 200
    assert "recovery email has been sent" in response.json()["message"]
    mock_supabase_api.forgot_password.assert_called_once_with("john@example.com", redirect_to="http://localhost:3000/reset-password")

@pytest.mark.asyncio
async def test_reset_password_status_check(mock_supabase_admin):
    mock_factor = MagicMock()
    mock_factor.factor_type = "totp"
    mock_factor.status = "verified"
    
    mock_user_data = MagicMock()
    mock_user_data.factors = [mock_factor]
    
    mock_admin_res = MagicMock()
    mock_admin_res.user = mock_user_data
    mock_supabase_admin.auth.admin.get_user_by_id.return_value = mock_admin_res
    
    mock_db_res = MagicMock()
    mock_db_res.data = [{"mfa_enabled": True}]
    mock_supabase_admin.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_db_res
    
    with patch("jose.jwt.get_unverified_claims", return_value={"sub": "user-uuid-123"}):
        headers = {"Authorization": "Bearer test-reset-token"}
        response = client.get("/api/v1/auth/reset-password/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["requires_mfa"] is True
        assert response.json()["user_id"] == "user-uuid-123"

@pytest.mark.asyncio
async def test_reset_password_success(mock_supabase_api):
    mock_supabase_api.update_password = AsyncMock()
    payload = {"new_password": "NewSecurePassword123!"}
    headers = {"Authorization": "Bearer test-reset-token"}
    response = client.post("/api/v1/auth/reset-password", json=payload, headers=headers)
    assert response.status_code == 200
    assert "Password has been reset successfully" in response.json()["message"]
    mock_supabase_api.update_password.assert_called_once_with("test-reset-token", "NewSecurePassword123!")

@pytest.mark.asyncio
async def test_reset_password_with_totp_success(mock_supabase_api, mock_supabase_admin):
    mock_factor = MagicMock()
    mock_factor.factor_type = "totp"
    mock_factor.status = "verified"
    mock_factor.id = "factor-uuid-123"
    
    mock_user_data = MagicMock()
    mock_user_data.factors = [mock_factor]
    
    mock_admin_res = MagicMock()
    mock_admin_res.user = mock_user_data
    mock_supabase_admin.auth.admin.get_user_by_id.return_value = mock_admin_res
    
    mock_supabase_api.mfa_challenge = AsyncMock(return_value={"id": "challenge-uuid-123"})
    mock_supabase_api.mfa_verify = AsyncMock(return_value={"access_token": "aal2-jwt-token"})
    mock_supabase_api.update_password = AsyncMock()

    with patch("jose.jwt.get_unverified_claims", return_value={"sub": "user-uuid-123"}):
        payload = {"new_password": "NewSecurePassword123!", "totp_code": "123456"}
        headers = {"Authorization": "Bearer test-reset-token"}
        response = client.post("/api/v1/auth/reset-password", json=payload, headers=headers)
        assert response.status_code == 200
        assert "Password has been reset successfully" in response.json()["message"]
        mock_supabase_api.mfa_verify.assert_called_once_with(
            token="test-reset-token",
            factor_id="factor-uuid-123",
            challenge_id="challenge-uuid-123",
            code="123456"
        )
        mock_supabase_api.update_password.assert_called_once_with("aal2-jwt-token", "NewSecurePassword123!")

# --- LOGOUT TESTS ---

@pytest.mark.asyncio
async def test_logout_success(mock_supabase_api):
    mock_supabase_api.logout = AsyncMock()
    headers = {"Authorization": "Bearer active-user-token"}
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    assert "Logged out successfully" in response.json()["message"]
    mock_supabase_api.logout.assert_called_once_with("active-user-token")

# --- MFA TESTS ---

@pytest.mark.asyncio
async def test_mfa_enroll_success(mock_supabase_api):
    mock_supabase_api.mfa_enroll = AsyncMock(return_value={"id": "factor-uuid-123", "type": "totp"})
    headers = {"Authorization": "Bearer active-user-token"}
    response = client.post("/api/v1/auth/mfa/enroll", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == "factor-uuid-123"
    mock_supabase_api.mfa_enroll.assert_called_once_with("active-user-token")

@pytest.mark.asyncio
async def test_mfa_verify_enroll_success(mock_supabase_api, mock_supabase_admin):
    mock_supabase_api.mfa_challenge = AsyncMock(return_value={"id": "challenge-uuid-123"})
    mock_supabase_api.mfa_verify = AsyncMock(return_value={"access_token": "aal2-jwt"})
    
    # Mock jwt decode and get_unverified_claims to get user_id
    with patch("jose.jwt.get_unverified_claims", return_value={"sub": "user-uuid-123"}), patch("jose.jwt.decode", return_value={"sub": "user-uuid-123"}):
        payload = {"factor_id": "factor-uuid-123", "code": "123456"}
        headers = {"Authorization": "Bearer active-user-token"}
        response = client.post("/api/v1/auth/mfa/verify-enroll", json=payload, headers=headers)
        assert response.status_code == 200
        assert "MFA activated successfully" in response.json()["message"]
        
        # Verify Supabase database was updated
        mock_supabase_admin.table.assert_called_with("users")
        mock_supabase_admin.table.return_value.update.assert_called_once_with({"mfa_enabled": True})

@pytest.mark.asyncio
async def test_mfa_verify_success(mock_supabase_api, mock_supabase_admin):
    # Mock admin.get_user_by_id
    mock_factor = MagicMock()
    mock_factor.factor_type = "totp"
    mock_factor.status = "verified"
    mock_factor.id = "factor-uuid-123"
    
    mock_user_data = MagicMock()
    mock_user_data.factors = [mock_factor]
    
    mock_admin_res = MagicMock()
    mock_admin_res.user = mock_user_data
    mock_supabase_admin.auth.admin.get_user_by_id.return_value = mock_admin_res
    
    mock_supabase_api.mfa_challenge = AsyncMock(return_value={"id": "challenge-uuid-123"})
    mock_supabase_api.mfa_verify = AsyncMock(return_value={"access_token": "aal2-jwt"})
    
    payload = {"user_id": "user-uuid-123", "totp_code": "123456"}
    headers = {"Authorization": "Bearer aal1-jwt"}
    response = client.post("/api/v1/auth/mfa/verify", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["session"]["access_token"] == "aal2-jwt"
    
    mock_supabase_admin.auth.admin.get_user_by_id.assert_called_once_with("user-uuid-123")
    mock_supabase_api.mfa_challenge.assert_called_once_with("aal1-jwt", "factor-uuid-123")
    mock_supabase_api.mfa_verify.assert_called_once_with(
        token="aal1-jwt",
        factor_id="factor-uuid-123",
        challenge_id="challenge-uuid-123",
        code="123456"
    )

# --- OAUTH / CALLBACK TESTS ---

@pytest.mark.asyncio
async def test_callback_get_success(mock_supabase_api):
    mock_supabase_api.exchange_code_for_session = AsyncMock(return_value={
        "access_token": "oauth-jwt-access",
        "refresh_token": "oauth-jwt-refresh",
        "expires_in": 3600,
        "token_type": "bearer",
        "user": {"id": "user-uuid-123", "email": "social@example.com"}
    })
    response = client.get("/api/v1/auth/callback?code=pkce_code_123")
    assert response.status_code == 200
    assert response.json()["message"] == "Authentication successful"
    assert response.json()["session"]["access_token"] == "oauth-jwt-access"
    mock_supabase_api.exchange_code_for_session.assert_called_once_with("pkce_code_123", None)

@pytest.mark.asyncio
async def test_callback_post_success(mock_supabase_api):
    mock_supabase_api.exchange_code_for_session = AsyncMock(return_value={
        "access_token": "oauth-jwt-access",
        "refresh_token": "oauth-jwt-refresh",
        "expires_in": 3600,
        "token_type": "bearer",
        "user": {"id": "user-uuid-123", "email": "social@example.com"}
    })
    payload = {"code": "pkce_code_123", "code_verifier": "verifier_xyz"}
    response = client.post("/api/v1/auth/callback", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Authentication successful"
    assert response.json()["session"]["access_token"] == "oauth-jwt-access"
    mock_supabase_api.exchange_code_for_session.assert_called_once_with("pkce_code_123", "verifier_xyz")

def test_callback_missing_code():
    response = client.get("/api/v1/auth/callback")
    assert response.status_code == 400
    assert "Missing required authorization code" in response.json()["detail"]

@pytest.mark.asyncio
async def test_callback_failure(mock_supabase_api):
    mock_supabase_api.exchange_code_for_session = AsyncMock(side_effect=Exception("Invalid authorization code"))
    response = client.get("/api/v1/auth/callback?code=invalid_code")
    assert response.status_code == 400
    assert "Invalid authorization code" in response.json()["detail"]




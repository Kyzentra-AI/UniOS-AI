import re
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo

PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$")

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    terms_accepted: bool

    @field_validator("terms_accepted")
    @classmethod
    def must_accept_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must accept the Terms & Conditions and Privacy Policy")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, "
                "one number, and one special character."
            )
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class EmailStatusRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    # For password reset, the user gets a temporary session or access token from the reset email link.
    # Supabase allows updating the user credentials while they have an active reset session.
    # In FastAPI, we can accept the token or just allow the request if they are authenticated.
    # If the client passes the token, we can use it to update the password.
    new_password: str
    totp_code: str | None = None

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, "
                "one number, and one special character."
            )
        return v

class MFAVerifyRequest(BaseModel):
    # Although the FRD says user_id, totp_code, we also need the user's active access token
    # to authenticate the challenge/verify process. We will receive the access token in headers,
    # and we can accept user_id in the body for logging/verification.
    user_id: str
    totp_code: str

class SocialLoginRequest(BaseModel):
    provider: str # "google", "facebook", "github"

class MFAEnrollVerifyRequest(BaseModel):
    factor_id: str
    code: str

class CallbackRequest(BaseModel):
    code: str
    code_verifier: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str




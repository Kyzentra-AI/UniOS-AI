# UniOS.ai Auth API

FastAPI backend for user authentication and secure platform entry using Supabase Auth.

## Overview

This service provides authentication endpoints for user registration, login, social login, multi-factor authentication (MFA), password recovery, and session management. It integrates with Supabase for user storage and authentication.

## Setup

1. **Clone the repository**
2. **Navigate to the backend directory**
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   Copy `.env.example` to `.env` and fill in the required values (Supabase URL and API keys).
5. **Run the database migrations** (if any) - check `supabase_schema.sql`.
6. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Endpoints

All endpoints are prefixed with `/api/v1/auth` unless otherwise noted.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register a new user. Requires email, password, full name, and acceptance of terms. Sends verification email. |
| `POST` | `/login` | Authenticate user with email and password. Returns session tokens. May require MFA if enabled. |
| `POST` | `/social` | Initiate social login (Google, GitHub, Facebook). Returns authorization URL for redirect. |
| `GET/POST` | `/callback` | Handle callback from social provider. Exchanges authorization code for session. |
| `POST` | `/logout` | Invalidate the current session (requires auth token). |

### Email Verification

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/resend-verification` | Resend email verification link. |
| `POST` | `/check-email-status` | Check if a given email address is verified. |

### Multi-Factor Authentication (MFA)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mfa/enroll` | Begin MFA enrollment (requires auth token). Returns secret for TOTP setup. |
| `POST` | `/mfa/verify-enroll` | Verify and activate MFA enrollment (requires auth token and factor ID). |
| `POST` | `/mfa/verify` | Verify MFA TOTP code during login (requires auth token). |

### Password Recovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/forgot-password` | Send password reset email. |
| `POST` | `/reset-password` | Reset password using a valid session token (from reset email link). |

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/refresh` | Refresh access token using refresh token. |

### Root Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message and pointer to documentation. |

## Request & Response Models

### RegisterRequest
- `full_name`: string (required)
- `email`: string (email format, required)
- `password`: string (must meet complexity requirements, required)
- `terms_accepted`: boolean (must be true, required)

### LoginRequest
- `email`: string (email format, required)
- `password`: string (required)

### SocialLoginRequest
- `provider`: string (must be "google", "github", or "facebook", required)

### MFAVerifyRequest
- `user_id`: string (required)
- `totp_code`: string (required)

### MFAEnrollVerifyRequest
- `factor_id`: string (required)
- `code`: string (TOTP code, required)

### CallbackRequest
- `code`: string (required)
- `code_verifier`: string (optional)

### RefreshTokenRequest
- `refresh_token`: string (required)

### ForgotPasswordRequest
- `email`: string (email format, required)

### ResetPasswordRequest
- `new_password`: string (must meet complexity requirements, required)

### EmailStatusRequest
- `email`: string (email format, required)

### ResendVerificationRequest
- `email`: string (email format, required)

## Responses

Successful responses typically return a JSON object with a `message` field and relevant data. Error responses return a JSON object with a `detail` field containing the error message and appropriate HTTP status code.

Common status codes:
- `200 OK`: Successful operation
- `201 Created`: Resource created (e.g., registration)
- `400 Bad Request`: Invalid input or request
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Email not verified or insufficient permissions
- `423 Locked`: Account temporarily locked due to failed login attempts
- `500 Internal Server Error`: Unexpected server error

## Environment Variables

Copy `.env.example` to `.env` and set:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key (for admin operations)
- `FRONTEND_URL`: URL of your frontend (for redirect validation, optional)

## Running Tests

To run the test suite:

```bash
pytest
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── auth.py     # Authentication endpoints
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   ├── deps.py             # Dependencies (e.g., Supabase clients)
│   │   ├── supabase.py         # Supabase client initialization
│   │   └── supabase_api.py     # Wrapper for Supabase Auth API
│   └── schemas/
│       └── auth.py             # Pydantic models for requests/responses
├── docs/                       # Additional documentation
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── supabase_schema.sql         # Supabase database schema
├── .env.example                # Example environment variables
└── README.md                   # This file
```

## Notes

- Passwords must meet complexity requirements: at least 8 characters, one uppercase letter, one number, and one special character.
- The terms of service and privacy policy must be accepted during registration.
- Social login redirects to a callback URL configured in your Supabase project settings.
- MFA uses TOTP (Time-based One-Time Password) via apps like Google Authenticator or Authy.

## License

This project is proprietary and confidential. Unauthorized copying or distribution is prohibited.
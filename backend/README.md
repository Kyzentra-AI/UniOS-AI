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

### 📚 Developer Documentation Guides

Dedicated guide documents are available in the [`docs/`](docs/) directory:
- 📱 **[Sprint 2 Frontend API & Endpoint Guide](docs/sprint_2_frontend_endpoints.md)**: Onboarding flow, profile management, auth tokens, user memory reset.
- 🤖 **[Sprint 2 AI/ML API & Context Engine Guide](docs/sprint_2_aiml_endpoints.md)**: System Prompt context injection payload, implicit memory logging.
- 📱 **[Sprint 3 Frontend Integration Guide](docs/sprint3_frontend_integration_guide.md)**: Syllabi uploads, Roadmap AI generation polling, Mission state machine.
- 🤖 **[Sprint 3 KIE AI/ML Integration Guide](docs/sprint3_kie_integration_guide.md)**: AI/ML schema expectations for Roadmap, Syllabus extraction, and Memory generation.
- 🧪 **[API Testing Guide](docs/api_testing_guide.md)**: Comprehensive testing workflows with cURL, Swagger, and Postman.
- 🗄️ **[Supabase Setup Guide](docs/supabase_setup_guide.md)**: Database schema migration and configuration.

---

## Endpoints

All endpoints are versioned under `/api/v1`.

### 1. Authentication (`/api/v1/auth`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `POST` | `/api/v1/auth/register` | No | Register a new user with email, password, full name. Sends verification email. |
| `POST` | `/api/v1/auth/login` | No | Authenticate user with email and password. Returns session tokens or MFA requirement. |
| `POST` | `/api/v1/auth/social` | No | Initiate social login (Google, GitHub, Facebook). Returns redirect URL. |
| `GET/POST` | `/api/v1/auth/callback` | No | Handle OAuth callback from social provider. |
| `POST` | `/api/v1/auth/logout` | **Yes** | Invalidate current user session. |
| `POST` | `/api/v1/auth/refresh` | No | Refresh access token using valid `refresh_token`. |
| `POST` | `/api/v1/auth/resend-verification` | No | Resend email verification link. |
| `POST` | `/api/v1/auth/check-email-status` | No | Check if email is verified. |
| `POST` | `/api/v1/auth/mfa/enroll` | **Yes** | Begin TOTP MFA enrollment. |
| `POST` | `/api/v1/auth/mfa/verify-enroll` | **Yes** | Verify and activate TOTP MFA enrollment. |
| `POST` | `/api/v1/auth/mfa/verify` | No | Verify TOTP code during 2FA login flow. |
| `POST` | `/api/v1/auth/forgot-password` | No | Send password reset email. |
| `POST` | `/api/v1/auth/reset-password` | **Yes** | Reset password using reset session token. |

### 2. Student Profile & Onboarding (`/api/v1/profile`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `GET` | `/api/v1/profile` | **Yes** | Retrieve student profile and active explicit AI directives. |
| `POST` | `/api/v1/profile` | **Yes** | Create or update profile preferences & explicit directives. |
| `POST` | `/api/v1/profile/directives` | **Yes** | Add a single explicit AI custom instruction. |
| `DELETE`| `/api/v1/profile/directives/{id}`| **Yes** | Delete an explicit AI directive by ID. |

### 3. AI Memory & Context Engine (`/api/v1`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `GET` | `/api/v1/context/retrieve` | **Yes** | Retrieve compiled student context payload (preferences, friction points, directives) for LLM prompts. |
| `POST` | `/api/v1/memory/logs` | **Yes** | Record or increment student concept friction log (implicit memory). |
| `POST` | `/api/v1/memory/reset` | **Yes** | Reset implicit learning memory (all or concept-specific). |
| `DELETE`| `/api/v1/memory/logs/{memory_id}`| **Yes** | Hard delete a specific memory log entry. |

### 4. Syllabus & Roadmaps (`/api/v1/syllabi`, `/api/v1/roadmaps`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `POST` | `/api/v1/syllabi` | **Yes** | Upload syllabus PDF. Returns ID and processing status. |
| `GET` | `/api/v1/syllabi/{id}/status` | **Yes** | Poll for AI extraction status. |
| `GET` | `/api/v1/syllabi/{id}` | **Yes** | Fetch parsed syllabus content (WAITING_FOR_CONFIRMATION). |
| `PUT` | `/api/v1/syllabi/{id}/parsed-content` | **Yes** | Update AI parsed content. |
| `POST` | `/api/v1/syllabi/{id}/reprocess` | **Yes** | Retry AI extraction on failure. |
| `POST` | `/api/v1/syllabi/{id}/confirm` | **Yes** | Confirm parsed syllabus, enabling roadmap generation. |
| `POST` | `/api/v1/roadmaps` | **Yes** | Generate new roadmap + missions via KIE from a confirmed syllabus. |

### 5. Missions (`/api/v1/missions`)

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `GET` | `/api/v1/missions` | **Yes** | List missions (optional `?roadmap_id=xxx` filter). |
| `POST` | `/api/v1/missions/{id}/start` | **Yes** | Transition mission from PENDING -> IN_PROGRESS. |
| `POST` | `/api/v1/missions/{id}/complete`| **Yes** | Transition mission from IN_PROGRESS -> COMPLETED. |
| `POST` | `/api/v1/missions/{id}/defer` | **Yes** | Defer a mission. |
| `POST` | `/api/v1/missions/{id}/skip` | **Yes** | Skip a mission. |

### Root Endpoint

| Method | Endpoint | Auth Required | Description |
|--------|----------|:-------------:|-------------|
| `GET` | `/` | No | Welcome message and pointer to documentation. |

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
│   │           ├── auth.py         # Authentication endpoints
│   │           ├── onboarding.py   # Learner onboarding
│   │           ├── syllabus.py     # Syllabus upload & parsing
│   │           ├── roadmaps.py     # AI Roadmap generation
│   │           └── missions.py     # Mission lifecycle management
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   ├── deps.py             # Dependencies (e.g., Supabase clients)
│   │   ├── supabase.py         # Supabase client initialization
│   │   ├── context_v2_assembler.py # Context orchestration
│   │   └── supabase_api.py     # Wrapper for Supabase Auth API
│   ├── services/               # Core business logic
│   │   ├── event_service.py
│   │   ├── kie_service.py
│   │   ├── pdf_service.py
│   │   ├── storage_service.py
│   │   ├── roadmap_service.py
│   │   └── syllabus_service.py
│   └── schemas/
│       ├── auth.py             # Auth schemas
│       ├── events.py
│       ├── mission.py
│       ├── roadmap.py
│       └── syllabus.py
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
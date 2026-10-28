# Sprint 2: Identity + AI Onboarding (07 Sep – 13 Sep) Implementation Plan

## Architectural Overview & Context
The **UniOS Learning Intelligence** repository functions as the **AI/ML-2** capability engine within the broader UniOS ecosystem (interacting with UniOS Backend, KIE, and AI/ML-1).
Sprint 2 expands capabilities into **Identity + AI Onboarding**, capturing rich learner profiles (academic stage, career goals, declared skills, modalities, learning preferences) and transforming them into structured multi-dimensional intelligence (Skill Analysis, Knowledge Analysis, Learning Style, Career Goal Alignment, Motivation Profile, and Readiness Assessment).

---

## User Review Required

> [!IMPORTANT]
> **Database & Identity Scope Boundary Clarification**:
> Currently, the repository is entirely stateless with no ORM or database engine (no SQLAlchemy/SQLModel/PostgreSQL/SQLite). Learner identities are referenced via `learner_id`.
> - **Option A (AI Service Contract Focus)**: Maintain AI/ML-2 service boundary where UniOS Backend/KIE stores the raw user/auth tables, while AI/ML-2 provides validated schemas, onboarding intelligence evaluation, and optional lightweight caching/profile persistence (e.g. SQLite/SQLAlchemy or JSON store).
> - **Option B (Full Self-Contained Identity & Auth)**: Add local database (SQLite/SQLAlchemy), user tables (`users`, `learner_profiles`, `onboarding_reports`), and auth token/API key verification in this service.
> *(We recommend Option A + local persistence capability so AI/ML-2 can function both as an independent service and seamlessly integrate with the main backend).*

> [!WARNING]
> **LLM Provider Rate Limits & Reliability**:
> Free Groq API keys with `qwen/qwen3.8-27b` enforce a strict 1,000 output tokens/minute (OTPM) rate limit. The onboarding prompt with 6 intelligence dimensions requires ~600-900 output tokens.
> When evaluating or testing, live back-to-back calls risk HTTP 429 errors unless robust fallback handling, schema-constrained output, and mock/caching options are provided.

---

## Proposed Changes

### Component 1: Schema & Data Contracts (`app/schemas/`)
Strengthen data models to represent identity, onboarding input, and intelligence output.

#### [MODIFY] [learner.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/schemas/learner.py)
- Expand `LearnerStage` and `LearnerState` to support onboarding linkage, user identifiers, and baseline metadata.

#### [MODIFY] [onboarding.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/schemas/onboarding.py)
- Ensure all input profile fields (`learner_id`, `stage`, `declared_skills`, `preferences`, `target_role`, `interests`) have comprehensive validation, documentation, and boundary constraints.
- Add identity support schemas (e.g. `LearnerIdentity`, `LearnerProfileCreate`, `LearnerProfileUpdate`).

#### [MODIFY] [intelligence.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/schemas/intelligence.py)
- Refine field validators and optional defaults for `SkillAnalysis`, `KnowledgeAnalysis`, `LearningStyleProfile`, `CareerGoalProfile`, `MotivationProfile`, and `ReadinessAssessment` to guarantee resilience against partial LLM outputs.

---

### Component 2: AI/ML-2 Intelligence Services (`app/services/`)
Separation of AI intelligence from routing and transport.

#### [MODIFY] [onboarding_prompt_builder.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/services/onboarding_prompt_builder.py)
- Ensure prompt provides explicit JSON schema definitions with exact keys and strict boundary rules (no raw UI code, no hallucinated markdown).
- Add compact token budgeting to stay within provider OTPM limits without sacrificing analytical depth.

#### [MODIFY] [llm_provider.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/services/llm_provider.py)
- Refine `GroqLLMProvider.analyze_learner_onboarding`:
  - Enforce defensive parsing, key normalization, and field fallback so slight LLM schema deviations do not crash validation.
  - Implement dynamic token-budget management (e.g., target 800-950 tokens instead of 1500 to prevent Groq 429 rate limit errors).
- Enhance `MockLLMProvider.analyze_learner_onboarding` with deterministic, realistic intelligence computation across Bachelor, Master, and Graduate test fixtures.

---

### Component 3: API Endpoints & Routes (`app/api/v1/endpoints/`)

#### [MODIFY] [onboarding.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/api/v1/endpoints/onboarding.py)
- Keep `/analyze` and `/learner-intelligence` endpoints robust.
- Add validation error handling, detailed OpenAPI documentation, and response timing metadata.
- If persistence is enabled: add profile retrieval (`GET /api/v1/onboarding/{learner_id}`) and report history endpoints.

#### [MODIFY] [api.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/api/v1/api.py)
- Ensure route registry cleanly connects learning and onboarding routers.

---

### Component 4: Optional Persistence / Storage Layer (`app/models/` & `app/core/`)

#### [NEW] [models/learner.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/app/models/learner.py) *(if DB persistence approved)*
- Lightweight SQLModel/SQLAlchemy or structured document storage for caching ingested onboarding profiles and generated intelligence reports.

---

### Component 5: Test Harness & Validation (`tests/`)

#### [MODIFY] [test_onboarding.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/tests/test_onboarding.py)
- Ensure mock provider test cases pass instantly with zero cost.
- Add isolated unit tests for prompt building, schema validations, boundary restrictions, and live provider error resilience.

#### [MODIFY] [test_contracts.py](file:///e:/Gen%20AI%20projects/unios-learning-intelligence/tests/test_contracts.py)
- Fix test assertion in `test_structured_lesson_generation_and_boundary_rules` to handle block variations gracefully while retaining boundary check against raw UI/JSX code.

---

## Verification Plan

### Automated Tests
- Run full test suite with mock provider:
  ```powershell
  $env:LLM_PROVIDER="mock"
  .\myvenv\Scripts\python.exe -m unittest discover tests
  ```
- Run live provider test with rate-limit pacing:
  ```powershell
  $env:LLM_PROVIDER="groq"
  .\myvenv\Scripts\python.exe -m unittest tests/test_onboarding.py
  ```

### Manual API Verification
- Test HTTP POST `/api/v1/onboarding/analyze` with curl/Postman/urllib against running Uvicorn server (`http://127.0.0.1:8000/docs`).

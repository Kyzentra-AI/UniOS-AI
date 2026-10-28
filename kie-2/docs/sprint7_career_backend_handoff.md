# UniOS Learning Intelligence — Sprint 7 Backend Handoff
## Career Intelligence & ATS Engine (AI/ML-2 KIE)

### 1. Architectural Boundaries & System Ownership

| Layer | System Owner | Core Responsibilities |
|---|---|---|
| **Persistence & Auth** | UniOS Backend | Authoritative databases (PostgreSQL/SQLAlchemy), user accounts, raw resume PDF/DOCX binaries, document parsing, deterministic ATS rule score computation, artifact storage. |
| **Intelligence Engine** | AI/ML-2 (This Service) | Stateless generative resume tailoring targeting roles/tones, grounding evidence synthesis, and qualitative ATS executive summaries/recommendations. |

**Invariants:**
- **Stateless Service:** Zero database access, ORM models, or persistent state.
- **Score Integrity:** The deterministic ATS rule score and scoring methodology are strictly owned by Backend. AI/ML-2 never recalculates, overrides, or alters them.
- **Anti-Hallucination & Grounding:** Missing contact details remain `null`. Whitelists of employers, institutions, and project titles are strictly respected. Original entry IDs are preserved.

---

### 2. API Endpoints Specification

#### Endpoint 1: AI Resume Generation
- **Path:** `POST /api/v1/kie/career/resume/generate`
- **Summary:** Synthesizes and tailors a professional resume draft grounded in authentic learner history and career readiness evidence.
- **Contract Source:** `launch_aiml_integration_guide.md` (Sections 3.2, 3.3, 3.4).

##### Request Schema Fields (`ResumeGenerateRequest`)
Supports both snake_case and camelCase field aliases:

| Field | Type | Required | Description |
|---|---|---|---|
| `request_id` / `requestId` | `string (UUID)` | Yes | Distributed tracing request identifier. |
| `learner_id` / `learnerId` | `string (UUID)` | Yes | Learner profile identifier. |
| `title` | `string` | Yes | Target resume title (e.g. `"Senior Cloud Backend Engineer"`). |
| `source` | `string ("profile" \| "manual")` | Yes | Source of base draft data. |
| `preferences` | `object` | No | Target role and writing tone preferences (`"professional"` \| `"concise"`). |
| `content` | `ResumeDraft` | Yes | Current draft content (`contact`, `headline`, `summary`, `skills`, `education`, `experience`, `projects`, `achievements`). |
| `career_context` / `careerContext` | `CareerContext (ContextV2)` | Yes | Verified grounding evidence from database (`learner`, `education`, `career_readiness`). |

##### Representative Request JSON
```json
{
  "requestId": "1c9a9189-3cb4-4b25-a053-467c1c0777d1",
  "learnerId": "00000000-0000-0000-0000-000000000002",
  "title": "Senior Cloud Backend Engineer",
  "source": "profile",
  "preferences": {
    "targetRole": "Backend Systems Architect",
    "tone": "professional"
  },
  "content": {
    "contact": {
      "fullName": "Jordan Lee",
      "email": "jordan.lee@example.com",
      "phone": "+1-415-555-0199",
      "location": "San Francisco, CA",
      "linkedInUrl": "https://linkedin.com/in/jordanlee",
      "githubUrl": "https://github.com/jordanlee",
      "portfolioUrl": "https://jordanlee.dev"
    },
    "headline": "Software Engineer",
    "summary": "Software engineer with backend experience.",
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
    "education": [
      {
        "id": "e8a93144-88ab-448c-9c98-cfba0c6fa4d2",
        "institution": "University of California, Berkeley",
        "degree": "B.S. in Computer Science",
        "fieldOfStudy": "Distributed Systems",
        "startDate": "2020",
        "endDate": "2024",
        "grade": "3.85 GPA"
      }
    ],
    "experience": [
      {
        "id": "3e9b1d07-2a4e-4f05-87cc-98836171f201",
        "company": "Acme Cloud Corp",
        "role": "Software Engineering Intern",
        "location": "San Francisco, CA",
        "startDate": "2023-06",
        "endDate": "2023-09",
        "isCurrent": false,
        "description": "Worked on backend APIs. Handled database queries and optimized performance."
      }
    ],
    "projects": [
      {
        "id": "d61b34e5-9c8a-4d22-9cb7-789a456123ef",
        "name": "Distributed Task Scheduler",
        "description": "Background task worker queue with priority routing.",
        "technologies": ["Python", "Redis", "Docker"],
        "projectUrl": "https://github.com/jordanlee/scheduler",
        "startDate": "2024-01",
        "endDate": "2024-04"
      }
    ],
    "achievements": [
      {
        "id": "f51c78a9-4b2e-49cd-90ef-123456789abc",
        "title": "AWS Certified Solutions Architect",
        "description": "Validated expertise in distributed cloud systems.",
        "date": "2024-05"
      }
    ]
  },
  "careerContext": {
    "learnerId": "00000000-0000-0000-0000-000000000002",
    "learner": {
      "primaryGoal": "Become a Principal Cloud Architect",
      "skills": ["Python", "FastAPI", "Go", "Docker", "PostgreSQL"],
      "experience": "Worked on backend APIs. Handled database queries and optimized performance."
    },
    "education": {
      "university": "University of California, Berkeley",
      "degreeProgram": "B.S. in Computer Science",
      "domain": "Distributed Systems",
      "academicStatus": "Graduated"
    },
    "careerReadiness": {
      "projects": [
        {
          "id": "b0a1c2d3-0001-4000-8000-000000000001",
          "title": "High-Throughput Microservice",
          "description": "Built resilient async event pipeline handling 100k msg/sec.",
          "skills": ["Python", "Redis", "FastAPI"],
          "status": "COMPLETED"
        }
      ],
      "evidence": [
        {
          "id": "ev-001",
          "title": "Query Latency Reduction",
          "description": "Decreased p99 database query response latency by 42%.",
          "skills": ["PostgreSQL", "Database Indexing"]
        }
      ],
      "mastery": [
        {
          "subject": "Computer Science",
          "topic": "Distributed Consensus & Raft",
          "masteryScore": 0.88,
          "status": "MASTERED"
        }
      ]
    }
  }
}
```

##### Representative Response JSON (`200 OK`)
```json
{
  "content": {
    "contact": {
      "fullName": "Jordan Lee",
      "email": "jordan.lee@example.com",
      "phone": "+1-415-555-0199",
      "location": "San Francisco, CA",
      "linkedInUrl": "https://linkedin.com/in/jordanlee",
      "githubUrl": "https://github.com/jordanlee",
      "portfolioUrl": "https://jordanlee.dev"
    },
    "headline": "Backend Systems Architect | Distributed Cloud & Data Infrastructure",
    "summary": "Engineering-focused Backend Systems Architect with deep foundations in distributed systems, asynchronous pipelines, and high-throughput databases. Demonstrated track record in containerized cloud microservices.",
    "skills": ["Python", "FastAPI", "Go", "PostgreSQL", "Docker", "Redis", "Distributed Consensus & Raft"],
    "education": [
      {
        "id": "e8a93144-88ab-448c-9c98-cfba0c6fa4d2",
        "institution": "University of California, Berkeley",
        "degree": "B.S. in Computer Science",
        "fieldOfStudy": "Distributed Systems",
        "startDate": "2020",
        "endDate": "2024",
        "grade": "3.85 GPA"
      }
    ],
    "experience": [
      {
        "id": "3e9b1d07-2a4e-4f05-87cc-98836171f201",
        "company": "Acme Cloud Corp",
        "role": "Software Engineering Intern",
        "location": "San Francisco, CA",
        "startDate": "2023-06",
        "endDate": "2023-09",
        "isCurrent": false,
        "description": "Architected asynchronous REST microservices in FastAPI, decreasing p99 database query latency by 42% through query indexing and Redis caching."
      }
    ],
    "projects": [
      {
        "id": "d61b34e5-9c8a-4d22-9cb7-789a456123ef",
        "name": "Distributed Task Scheduler",
        "description": "Engineered event-driven task worker queue handling 100k msg/sec with automated fault recovery and Redis priority routing.",
        "technologies": ["Python", "Redis", "Docker"],
        "projectUrl": "https://github.com/jordanlee/scheduler",
        "startDate": "2024-01",
        "endDate": "2024-04"
      }
    ],
    "achievements": [
      {
        "id": "f51c78a9-4b2e-49cd-90ef-123456789abc",
        "title": "AWS Certified Solutions Architect",
        "description": "Validated expertise in distributed cloud architectures, high availability, and secure networking.",
        "date": "2024-05"
      }
    ]
  }
}
```

---

#### Endpoint 2: ATS Resume Analysis Feedback Refinement
- **Path:** `POST /api/v1/kie/career/ats/analyze`
- **Summary:** Enriches deterministic ATS rule findings with personalized qualitative executive summaries and actionable advice (Google XYZ framing).
- **Contract Source:** `launch_aiml_integration_guide.md` (Sections 4.2, 4.3, 4.4).

##### Request Schema Fields (`ATSAnalyzeRequest`)
Supports both snake_case and camelCase field aliases:

| Field | Type | Required | Description |
|---|---|---|---|
| `request_id` / `requestId` | `string (UUID)` | Yes | Tracing identifier. |
| `learner_id` / `learnerId` | `string (UUID)` | Yes | Learner profile identifier. |
| `document` | `DocumentMetadata` | Yes | File metadata (`fileName`, `fileType`: `"pdf"` \| `"docx"`, `pageCount`, `extractedCharacterCount`). |
| `extracted_text` / `extractedText` | `string` | Yes | Raw extracted plain text from resume document. |
| `rule_score` / `ruleScore` | `RuleScore` | Yes | Deterministic rule score (`value`: `0.0–100.0`, `maxValue`: `100.0`, `methodology`, `methodologyVersion`). |
| `rule_findings` / `ruleFindings` | `List[RuleFinding]` | Yes | Rule-based findings from Backend engine (`id`, `category`, `severity`, `title`, `description`, `recommendation`). |

##### Representative Request JSON
```json
{
  "requestId": "2d8f99a0-1b2c-4e3d-9f0a-112233445566",
  "learnerId": "00000000-0000-0000-0000-000000000002",
  "document": {
    "fileName": "Jordan_Lee_Resume.pdf",
    "fileType": "pdf",
    "pageCount": 1,
    "extractedCharacterCount": 2150
  },
  "extractedText": "Jordan Lee\njordan.lee@example.com | San Francisco, CA\n\nSUMMARY\nSoftware Engineer with experience in Python and databases.\n\nEXPERIENCE\nAcme Cloud Corp - Intern\nWorked on backend APIs and helped with database.\n\nPROJECTS\nDistributed Task Scheduler\nBuilt an async task worker queue.\n\nEDUCATION\nUC Berkeley - B.S. in Computer Science\nGraduated 2024",
  "ruleScore": {
    "value": 72.0,
    "maxValue": 100.0,
    "methodology": "defined-rule-based-checks",
    "methodologyVersion": "1.0"
  },
  "ruleFindings": [
    {
      "id": "f1-contact",
      "category": "contact_information",
      "severity": "warning",
      "title": "Missing Phone Number",
      "description": "No reachable phone number was found.",
      "recommendation": "Add a standardized phone number with area/country code so recruiters can contact you."
    },
    {
      "id": "f2-metrics",
      "category": "missing_information",
      "severity": "warning",
      "title": "Few Quantifiable Impact Metrics",
      "description": "Found only 0 quantifiable data points or percentage improvements.",
      "recommendation": "Include specific numbers, scale indicators, and metrics."
    },
    {
      "id": "f3-verbs",
      "category": "content",
      "severity": "warning",
      "title": "Low Action Verb Density",
      "description": "Detected only 2 distinct strong action verbs in your resume.",
      "recommendation": "Start bullet points with high-impact action verbs."
    }
  ]
}
```

##### Representative Response JSON (`200 OK`)
```json
{
  "summary": "Jordan displays a strong educational foundation from UC Berkeley and solid exposure to modern backend technologies like Python and Docker. However, the resume exhibits critical ATS screening liabilities: an absent telephone number, lack of quantifiable impact metrics, and passive phrasing in the work experience section. Incorporating quantified metrics (such as request throughput or latency reductions) and opening each bullet with active technical verbs will dramatically increase screening pass-rates.",
  "findings": [
    {
      "id": "f1-contact",
      "category": "contact_information",
      "severity": "critical",
      "title": "Critical Missing Contact: Phone Number",
      "description": "ATS parsing engines and recruiters cannot trigger automated phone screening without a standardized contact number.",
      "recommendation": "Add a standardized phone number with area code (+1-XXX-XXX-XXXX) directly beneath your name in the contact header."
    },
    {
      "id": "f2-metrics",
      "category": "missing_information",
      "severity": "warning",
      "title": "Absence of Quantified Outcomes (Google XYZ Formula)",
      "description": "Found 0 numerical metrics in experience bullets. Modern ATS algorithms and engineering hiring managers heavily favor quantified impact.",
      "recommendation": "Rewrite bullets using Google's formula: 'Accomplished [X], as measured by [Y], by doing [Z]'. Example: 'Reduced query latency by 42% by introducing Redis caching'."
    },
    {
      "id": "f3-verbs",
      "category": "content",
      "severity": "suggestion",
      "title": "Passive Phrasing in Experience Bullets",
      "description": "Phrases such as 'Worked on' and 'Helped with' weaken candidate impact signals during recruiter skim-reviews.",
      "recommendation": "Replace with vigorous technical action verbs: 'Architected', 'Containerized', 'Spearheaded', 'Optimized'."
    }
  ]
}
```

---

### 3. HTTP Status Codes & Error Protocol

| Status Code | Description | Example Detail |
|---|---|---|
| `200 OK` | Valid request evaluated successfully. | Structured JSON matching response model. |
| `422 Unprocessable Entity` | Pydantic validation error (e.g. missing required field, score > 100.0). | `{"detail": [{"loc": ["body", "rule_score", "value"], "msg": "Rule score value must be between 0.0 and 100.0."}]}` |
| `429 Too Many Requests` | LLM provider output token rate limit reached. | `{"detail": "Groq API rate limit exceeded (HTTP 429). Please retry shortly or use mock provider."}` |
| `502 Bad Gateway` | Malformed JSON or schema validation error from LLM. | `{"detail": "Resume generation response could not be parsed: Failed to parse career response JSON: ..."}` |
| `504 Gateway Timeout` | Provider network connection or read timeout. | `{"detail": "Groq API connection or timeout failure: Read timed out."}` |
| `500 Internal Server Error` | Unexpected internal exception. | `{"detail": "Unexpected internal error during resume generation: ..."}` |

*Security invariant:* All error messages are passed through `_sanitize_error_message`, ensuring raw API keys (`gsk_...`, `sk-...`), `Bearer` tokens, and secrets are permanently masked (`[REDACTED_API_KEY]`) before reaching clients.

---

### 4. Local Execution & Startup Guide

#### Environment Variables (`.env`)
```bash
APP_NAME="UniOS Learning Intelligence"
# Use 'mock' for zero-cost offline local testing, or 'groq' for live inference
LLM_PROVIDER=mock
LLM_MODEL=qwen/qwen3.8-27b
LLM_TEMPERATURE=0.2
# Required only if LLM_PROVIDER=groq
GROQ_API_KEY=
```

#### Starting the Service
```powershell
.\myvenv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health Check: `http://127.0.0.1:8000/health`

#### Running Tests
```powershell
# Sprint 7 Complete Suite (69 tests)
.\myvenv\Scripts\pytest -v tests/test_sprint7_career_schemas.py tests/test_sprint7_career_prompts.py tests/test_sprint7_career_service.py tests/test_sprint7_career_routes.py

# Full Repository Regression Suite (260 tests)
.\myvenv\Scripts\pytest -v
```

---

### 5. Known Integration Boundaries & Notes for Backend Team

1. **Document Parsing Responsibility:**
   - AI/ML-2 does not parse binary `.pdf` or `.docx` files. Backend is responsible for running `pypdf`/`pdfminer`/`python-docx` and passing the resulting plain text in `extracted_text`.
2. **Deterministic Score Boundary:**
   - The `rule_score` object must be calculated by Backend's deterministic rule engine (v1.0) before calling `POST /api/v1/kie/career/ats/analyze`.
   - AI/ML-2 does not store or alter the rule score. Backend stores both the deterministic score and the enriched qualitative feedback.
3. **Artifact Persistence:**
   - AI/ML-2 does not store generated resume drafts in a database. Backend receives the tailored `ResumeDraft` from `POST /api/v1/kie/career/resume/generate` and commits it to Backend's `resumes` table.
4. **Token Rate Limits on Live Groq:**
   - When deploying with live Groq (`qwen/qwen3.8-27b`), output token limits (1000 OTPM on free tier) may cause HTTP 429 during heavy bursts. In production, configure an enterprise tier key or provision a dedicated fallback provider.

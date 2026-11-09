from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

tags_metadata = [
    {
        "name": "KIE Context Intelligence",
        "description": "Unified KIE: Onboarding Context Analysis & Resolution with asynchronous webhook delivery.",
    },
    {
        "name": "KIE Syllabus Intelligence",
        "description": "Unified KIE: Structured curriculum, subject & topic extraction from syllabus documents.",
    },
    {
        "name": "KIE Roadmap Intelligence",
        "description": "Unified KIE: Dynamic academic & career roadmap synthesis and mission generation.",
    },
    {
        "name": "KIE Memory Intelligence",
        "description": "Unified KIE: Pedagogical memory summary for ContextV2Assembler.",
    },
    {
        "name": "Memory Intelligence",
        "description": "AI/ML-2 Capabilities: Learner Memory Engine, Context Retrieval & Roadmap Adaptation.",
    },
    {
        "name": "Identity & Onboarding Intelligence",
        "description": "AI/ML-2 Capabilities: Multi-Dimensional Learner Profiling & Readiness Assessment.",
    },
    {
        "name": "Learning Intelligence",
        "description": "AI/ML-2 Capabilities: Pedagogy Decision & Structured Lesson Generation.",
    },
    {
        "name": "Build Intelligence",
        "description": "AI/ML-2 Capabilities: Universal Build Coach & Domain-Adaptive Project Recommendations.",
    },
    {
        "name": "Career Intelligence",
        "description": "AI/ML-2 Capabilities: AI Resume Generator & ATS Resume Analysis.",
    },
    {
        "name": "Assessment Intelligence",
        "description": "AI/ML KIE Capabilities: Dynamic Assessment Synthesis & Mastery Attempt Evaluation.",
    },
    {
        "name": "Mentor Intelligence",
        "description": "AI/ML KIE Capabilities: Persona-Driven AI Mentor Chat across 4 Pedagogical Modes.",
    },
    {
        "name": "Health",
        "description": "System readiness and health check operations.",
    },
]

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description="UniOS AI/ML-2 Learning Intelligence Service. Exposes structured intelligence contracts to AI/ML-1 and Backend. Assessments, Mastery & Mentor Chat Engine.",
    version="1.3.0",
    openapi_tags=tags_metadata,
)

# Enable CORS for external/backend access
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "https://unios-ai.round-paper-f740.workers.dev",
    "https://unios-ai.round-paper-f740.workers.dev/",
    "https://unios-ai.onrender.com",
    "https://unios-ai.onrender.com/",
    "https://unios-ai-q0th.onrender.com",
    "https://unios-ai-q0th.onrender.com/",
    "https://unios-kie2.onrender.com",
    "https://unios-kie2.onrender.com/",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API capability routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"], summary="UniOS Service Root Index")
def root_index():
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "version": "1.3.0",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "health_check": "/health",
        "primary_endpoints": {
            "context_analyze": "/api/v1/kie/context/analyze",
            "context_resolve": "/api/v1/kie/context/resolve",
            "syllabus_extract": "/api/v1/kie/syllabus/extract",
            "roadmap_generate": "/api/v1/kie/roadmap/generate",
            "memory_summary": "/api/v1/kie/memory/summary",
            "learn_interpret": "/api/v1/kie/learn/interpret",
            "lesson_generation": "/api/v1/kie/lesson/generate",
            "mastery_evaluate": "/api/v1/kie/mastery/evaluate",
            "build_coach": "/api/v1/kie/build/coach",
            "build_recommend": "/api/v1/kie/build/recommend",
            "career_resume": "/api/v1/kie/career/resume/generate",
            "career_ats": "/api/v1/kie/career/ats/analyze",
            "assessments_generate": "/api/v1/kie/assessments/generate",
            "mentor_chat": "/api/v1/kie/mentor/chat",
        },
    }



@app.get("/health", tags=["Health"], summary="System Health Check")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
    }


from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

tags_metadata = [
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
        "name": "Health",
        "description": "System readiness and health check operations.",
    },
]

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description="UniOS AI/ML-2 Learning Intelligence Service. Exposes structured intelligence contracts to AI/ML-1 and Backend. Sprint 7: Career Intelligence & ATS Engine.",
    version="1.2.0",
    openapi_tags=tags_metadata,
)

# Enable CORS for external/backend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "version": "1.2.0",
        "documentation": "/docs",
        "openapi_schema": "/openapi.json",
        "health_check": "/health",
        "primary_endpoints": {
            "lesson_generation": "/api/v1/kie/lesson/generate",
            "learning_plan": "/api/v1/learning/plan-lesson",
            "onboarding": "/api/v1/onboarding/analyze",
            "memory": "/api/v1/memory/relevant-context",
            "build_coach": "/api/v1/kie/build/coach",
            "career_ats": "/api/v1/kie/career/ats-analyze",
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


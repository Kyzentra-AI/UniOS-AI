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

app = FastAPI(
    title=settings.APP_NAME,
    description="UniOS AI/ML-2 Learning Intelligence Service. Exposes structured intelligence contracts to AI/ML-1 and Backend. Sprint 7: Career Intelligence & ATS Engine.",
    version="1.2.0",
    openapi_tags=tags_metadata,
)

# Include v1 API capability routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"], summary="System Health Check")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
    }

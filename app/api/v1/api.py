from fastapi import APIRouter
from app.api.v1.endpoints import learning, onboarding, memory
from app.api.v1.endpoints import build
from app.api.v1.endpoints import career

api_router = APIRouter()
# Sprint 1-4 learning routes — /api/v1/learning/*
api_router.include_router(
    learning.router, prefix="/learning", tags=["Learning Intelligence"]
)
# Section 14.1 AI-1 Pedagogical Interpreter — /api/v1/kie/learn/interpret
api_router.include_router(
    learning.router, prefix="/kie/learn", tags=["Learning Intelligence"]
)
# Section 14.2 AI-2 Lesson Generation — /api/v1/kie/lesson/generate
api_router.include_router(
    learning.router, prefix="/kie/lesson", tags=["Learning Intelligence"]
)
# General KIE namespace alias
api_router.include_router(
    learning.router, prefix="/kie", tags=["Learning Intelligence"]
)
api_router.include_router(
    onboarding.router, prefix="/onboarding", tags=["Identity & Onboarding Intelligence"]
)
api_router.include_router(
    memory.router, prefix="/memory", tags=["Memory Intelligence"]
)
# Sprint 5: Universal Build Engine — /api/v1/kie/build/*
api_router.include_router(
    build.router, prefix="/kie/build", tags=["Build Intelligence"]
)
# Sprint 7: Career Intelligence & ATS — /api/v1/kie/career/*
api_router.include_router(
    career.router, prefix="/kie/career", tags=["Career Intelligence"]
)

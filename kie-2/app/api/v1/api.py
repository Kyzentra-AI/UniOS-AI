from fastapi import APIRouter
from app.api.v1.endpoints import learning, onboarding, memory
from app.api.v1.endpoints import build
from app.api.v1.endpoints import career
from app.api.v1.endpoints import assessment
from app.api.v1.endpoints import mentor
from app.api.v1.endpoints import context
from app.api.v1.endpoints import syllabus
from app.api.v1.endpoints import roadmap
from app.api.v1.endpoints import memory_summary

api_router = APIRouter()

# --- Unified KIE Migration Endpoints (Absorbing KIE-1 into KIE-2) ---
# Endpoint 1 & 2: Context Analysis & Resolution — /api/v1/kie/context/*
api_router.include_router(
    context.router, prefix="/kie/context", tags=["KIE Context Intelligence"]
)

# Endpoint 3: Syllabus Extraction — /api/v1/kie/syllabus/*
api_router.include_router(
    syllabus.router, prefix="/kie/syllabus", tags=["KIE Syllabus Intelligence"]
)

# Endpoint 4: Roadmap & Missions Generation — /api/v1/kie/roadmap/*
api_router.include_router(
    roadmap.router, prefix="/kie/roadmap", tags=["KIE Roadmap Intelligence"]
)

# Endpoint 5: Memory Summary for ContextV2Assembler — /api/v1/kie/memory/*
api_router.include_router(
    memory_summary.router, prefix="/kie/memory", tags=["KIE Memory Intelligence"]
)

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

# Assessments Intelligence — /api/v1/kie/assessments/*
api_router.include_router(
    assessment.assessment_router, prefix="/kie/assessments", tags=["Assessment Intelligence"]
)
api_router.include_router(
    assessment.assessment_router, prefix="/assessments", tags=["Assessment Intelligence"]
)

# Mastery Evaluation — /api/v1/kie/mastery/*
api_router.include_router(
    assessment.mastery_router, prefix="/kie/mastery", tags=["Assessment Intelligence"]
)
api_router.include_router(
    assessment.mastery_router, prefix="/mastery", tags=["Assessment Intelligence"]
)

# Mentor Chat — /api/v1/kie/mentor/*
api_router.include_router(
    mentor.router, prefix="/kie/mentor", tags=["Mentor Intelligence"]
)
api_router.include_router(
    mentor.router, prefix="/mentor", tags=["Mentor Intelligence"]
)


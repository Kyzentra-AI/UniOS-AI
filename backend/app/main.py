from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler, http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.endpoints import (
    auth,
    onboarding,
    syllabus,
    roadmaps,
    missions,
    learning,
    assessments,
    build,
    launch,
    billing,
    mentor,
)
from app.schemas.launch import APIError

app = FastAPI(
    title="UniOS.ai Backend API",
    description="FastAPI Backend for User Authentication, Learning, Build & Launch Engine",
    version="1.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_REDIRECT_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors on launch endpoints to match standardized APIError schema."""
    if request.url.path.startswith("/api/v1/launch"):
        req_id = request.headers.get("x-request-id")
        return JSONResponse(
            status_code=422,
            content=APIError(
                code="VALIDATION_ERROR",
                message="Request validation failed.",
                details={"errors": exc.errors()},
                request_id=req_id,
            ).model_dump(by_alias=True),
        )
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Formats HTTP exceptions on launch endpoints to match standardized APIError schema."""
    if request.url.path.startswith("/api/v1/launch"):
        req_id = request.headers.get("x-request-id")
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            data = exc.detail
            if not data.get("requestId") and not data.get("request_id"):
                data["requestId"] = req_id
            return JSONResponse(status_code=exc.status_code, content=data)
        return JSONResponse(
            status_code=exc.status_code,
            content=APIError(
                code="HTTP_ERROR",
                message=str(exc.detail),
                details=None,
                request_id=req_id,
            ).model_dump(by_alias=True),
        )
    return await http_exception_handler(request, exc)


# Include Routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(syllabus.router)
app.include_router(roadmaps.router)
app.include_router(missions.router)
app.include_router(learning.router)
app.include_router(assessments.router)
app.include_router(build.router)
app.include_router(launch.router)
app.include_router(billing.router)
app.include_router(mentor.router)


@app.get("/")
async def root():
    return {"message": "Welcome to UniOS.ai Backend API. Go to /api/docs for API documentation."}

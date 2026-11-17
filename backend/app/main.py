import uuid
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
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

logger = logging.getLogger(__name__)

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
    expose_headers=["X-Request-ID"],
)


from starlette.types import ASGIApp, Receive, Scope, Send

class RequestTracingMiddleware:
    """Web BUG-10: Pure ASGI request tracing middleware for end-to-end X-Request-ID propagation."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_dict = dict(scope.get("headers", []))
        raw_req_id = headers_dict.get(b"x-request-id", b"").decode("utf-8")
        req_id = raw_req_id if raw_req_id else f"req_{uuid.uuid4().hex[:8]}"
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = req_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                resp_headers = list(message.get("headers", []))
                resp_headers.append((b"x-request-id", req_id.encode("utf-8")))
                message["headers"] = resp_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

app.add_middleware(RequestTracingMiddleware)


def _sanitize_validation_errors(raw_errors: list) -> list:
    """Recursively converts Exceptions in error dicts (e.g. ValueError in ctx) into strings and makes them JSON-safe."""
    safe_errors = []
    for err in raw_errors:
        clean = dict(err)
        if "ctx" in clean and isinstance(clean["ctx"], dict):
            clean["ctx"] = {
                k: str(v) if isinstance(v, Exception) else v
                for k, v in clean["ctx"].items()
            }
        safe_errors.append(clean)
    return jsonable_encoder(safe_errors, custom_encoder={Exception: str})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Web BUG-10: Standardized validation error envelope matching frontend contract."""
    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:8]}"
    safe_errors = _sanitize_validation_errors(exc.errors())
    content = {
        "code": "VALIDATION_ERROR",
        "message": "Request validation failed.",
        "detail": safe_errors,
        "details": {"errors": safe_errors},
        "requestId": req_id,
    }
    # Backward compatibility with /api/v1/launch
    if request.url.path.startswith("/api/v1/launch"):
        content["success"] = False
        content["errors"] = safe_errors

    response = JSONResponse(status_code=422, content=content)
    response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Web BUG-10: Standardized HTTP exception envelope matching frontend contract."""
    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:8]}"

    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        msg = exc.detail.get("message") or exc.detail.get("detail") or "An error occurred."
        details = exc.detail.get("details", {})
    else:
        status_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            502: "UPSTREAM_KIE_TIMEOUT" if "KIE" in str(exc.detail) else "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT",
        }
        code = status_code_map.get(exc.status_code, "HTTP_ERROR")
        msg = str(exc.detail)
        details = {}

    content = {
        "code": code,
        "message": msg,
        "detail": msg,
        "details": details,
        "requestId": req_id,
    }
    if request.url.path.startswith("/api/v1/launch"):
        content["success"] = False

    response = JSONResponse(status_code=exc.status_code, content=content)
    response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Web BUG-10: Resilient fallback for unhandled 500 errors."""
    req_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex[:8]}"
    logger.error(f"Unhandled error [{req_id}] on {request.url.path}: {exc}", exc_info=True)
    msg = "An unexpected server error occurred. Please retry."
    content = {
        "code": "INTERNAL_SERVER_ERROR",
        "message": msg,
        "detail": msg,
        "details": {},
        "requestId": req_id,
    }
    response = JSONResponse(status_code=500, content=content)
    response.headers["X-Request-ID"] = req_id
    return response


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

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.errors.handlers import (
    validation_error_handler,
    general_error_handler,
)


app = FastAPI(
    title="UniOS.ai KIE Core",
    version="0.1.0",
    description="KIE Core and orchestration service for UniOS.ai",
)

# Configure CORS
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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    Exception,
    general_error_handler,
)


app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "kie-core",
    }
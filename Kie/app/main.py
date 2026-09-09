from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
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
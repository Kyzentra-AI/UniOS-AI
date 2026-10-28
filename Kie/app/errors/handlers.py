from fastapi import Request
from fastapi.responses import JSONResponse


def validation_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
            },
        },
    )


def general_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )
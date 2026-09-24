from fastapi import APIRouter

from app.core.context import ContextEngine
from app.core.service import KIEService

from app.schemas.request import (
    AnalyzeContextRequest,
    KIERequest,
    ResolveContextRequest,
)

from app.schemas.response import (
    AnalyzeContextResponse,
    KIEResponse,
    ResolveContextResponse,
)


router = APIRouter(
    tags=["KIE"],
)


kie_service = KIEService()
context_engine = ContextEngine()


@router.post(
    "/kie/execute",
    response_model=KIEResponse,
)
def execute_kie(
    request: KIERequest,
) -> KIEResponse:

    return kie_service.execute(request)


# ============================================================
# Sprint 2 — Onboarding Context Analysis
# ============================================================


@router.post(
    "/api/v1/kie/context/analyze",
    response_model=AnalyzeContextResponse,
)
def analyze_onboarding_context(
    request: AnalyzeContextRequest,
) -> AnalyzeContextResponse:

    result = (
        context_engine.analyze_onboarding_context(
            request
        )
    )

    return AnalyzeContextResponse(
        **result
    )


# ============================================================
# Sprint 2 — Onboarding Context Resolution
# ============================================================


@router.post(
    "/api/v1/kie/context/resolve",
    response_model=ResolveContextResponse,
)
def resolve_onboarding_context(
    request: ResolveContextRequest,
) -> ResolveContextResponse:

    result = (
        context_engine.resolve_onboarding_context(
            request
        )
    )

    return ResolveContextResponse(
        **result
    )
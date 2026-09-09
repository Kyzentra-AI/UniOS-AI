from fastapi import APIRouter

from app.core.service import KIEService
from app.schemas.request import KIERequest
from app.schemas.response import KIEResponse


router = APIRouter(
    prefix="/kie",
    tags=["KIE"],
)

kie_service = KIEService()


@router.post(
    "/execute",
    response_model=KIEResponse,
)
def execute_kie(request: KIERequest) -> KIEResponse:
    return kie_service.execute(request)
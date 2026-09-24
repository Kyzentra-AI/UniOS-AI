import httpx
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KIEService:
    @staticmethod
    async def analyze_context(context_payload: Dict[str, Any]) -> None:
        """
        Sends the assembled context to KIE for analysis asynchronously.
        KIE will process this and send questions to the webhook endpoint.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/context/analyze",
                    json=context_payload,
                    timeout=10.0
                )
                response.raise_for_status()
            except httpx.RequestError as exc:
                logger.error(f"An error occurred while requesting KIE analyze: {exc}")
            except httpx.HTTPStatusError as exc:
                logger.error(f"Error response {exc.response.status_code} while requesting KIE analyze.")

    @staticmethod
    async def resolve_context(user_id: str, answers: list) -> None:
        """
        Sends the user answers to KIE for resolution asynchronously.
        KIE will process this and send the resolved context to the webhook endpoint.
        """
        payload = {
            "user_id": user_id,
            "answers": [answer.model_dump() for answer in answers]
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.KIE_BASE_URL}/api/v1/kie/context/resolve",
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
            except httpx.RequestError as exc:
                logger.error(f"An error occurred while requesting KIE resolve: {exc}")
            except httpx.HTTPStatusError as exc:
                logger.error(f"Error response {exc.response.status_code} while requesting KIE resolve.")

kie_service = KIEService()

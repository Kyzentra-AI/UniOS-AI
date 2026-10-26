import logging
import os
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class BackendWebhookSender:
    """
    Sends asynchronous KIE callbacks to the Backend.

    Backend remains responsible for persistence.
    KIE only sends the structured inference result.
    """

    def __init__(self) -> None:
        self.backend_base_url = os.getenv(
            "BACKEND_BASE_URL",
            "",
        ).rstrip("/")

        self.webhook_secret = os.getenv(
            "KIE_WEBHOOK_SECRET",
            "",
        )

        self.timeout = httpx.Timeout(
            connect=5.0,
            read=15.0,
            write=15.0,
            pool=5.0,
        )

    def _validate_configuration(self) -> bool:
        if not self.backend_base_url:
            logger.error(
                "BACKEND_BASE_URL is not configured"
            )
            return False

        if not self.webhook_secret:
            logger.error(
                "KIE_WEBHOOK_SECRET is not configured"
            )
            return False

        return True

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Kie-Signature": self.webhook_secret,
        }

    def _post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> bool:
        if not self._validate_configuration():
            return False

        url = f"{self.backend_base_url}{endpoint}"

        try:
            with httpx.Client(
                timeout=self.timeout,
            ) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                )

            if 200 <= response.status_code < 300:
                logger.info(
                    "KIE webhook delivered successfully: %s",
                    endpoint,
                )
                return True

            logger.error(
                "KIE webhook failed: endpoint=%s status=%s body=%s",
                endpoint,
                response.status_code,
                response.text[:500],
            )
            return False

        except httpx.RequestError as exc:
            logger.error(
                "KIE webhook request failed: endpoint=%s error=%s",
                endpoint,
                exc,
            )
            return False

    def send_questions(
        self,
        user_id: str,
        questions: list[dict[str, Any]],
    ) -> bool:
        payload = {
            "user_id": user_id,
            "questions": questions,
        }

        return self._post(
            "/api/v1/onboarding/kie/webhook/questions",
            payload,
        )

    def send_resolved_context(
        self,
        user_id: str,
        new_context: dict[str, Any],
    ) -> bool:
        payload = {
            "user_id": user_id,
            "new_context": new_context,
        }

        return self._post(
            "/api/v1/onboarding/kie/webhook/resolved",
            payload,
        )
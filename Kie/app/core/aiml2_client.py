
import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


class AIML2ClientError(Exception):
    """Raised when communication with AI/ML-2 fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class AIML2Client:
    """
    HTTP client for the AI/ML-2 intelligence service.

    KIE owns orchestration.
    AI/ML-2 provides specialized intelligence.
    Backend remains responsible for persistence.
    """

    def __init__(self) -> None:
        self.base_url = os.getenv(
            "AIML2_BASE_URL",
            "",
        ).rstrip("/")

        self.timeout = httpx.Timeout(
            connect=float(os.getenv("AIML2_CONNECT_TIMEOUT", "5")),
            read=float(os.getenv("AIML2_READ_TIMEOUT", "30")),
            write=15.0,
            pool=5.0,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:

        if not self.base_url:
            raise AIML2ClientError(
                "AIML2_BASE_URL is not configured."
            )

        url = f"{self.base_url}{endpoint}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                )

            response.raise_for_status()

            try:
                result = response.json()
            except ValueError as exc:
                raise AIML2ClientError(
                    "AI/ML-2 returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc

            if not isinstance(result, dict):
                raise AIML2ClientError(
                    "AI/ML-2 returned an unexpected response format.",
                    status_code=response.status_code,
                )

            return result

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            logger.error(
                "AI/ML-2 HTTP error: method=%s endpoint=%s status=%s",
                method,
                endpoint,
                status_code,
            )

            raise AIML2ClientError(
                f"AI/ML-2 returned HTTP {status_code}.",
                status_code=status_code,
            ) from exc

        except httpx.RequestError as exc:
            logger.error(
                "AI/ML-2 connection failed: method=%s endpoint=%s error=%s",
                method,
                endpoint,
                exc,
            )

            raise AIML2ClientError(
                "Unable to communicate with AI/ML-2."
            ) from exc

    def generate_resume(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/kie/career/resume/generate",
            json=payload,
        )

    def analyze_ats(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/kie/career/ats/analyze",
            json=payload,
        )

    def coach_build(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/kie/build/coach",
            json=payload,
        )

    def recommend_builds(
        self,
        learner_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/kie/build/recommend",
            params={"learner_id": learner_id},
        )

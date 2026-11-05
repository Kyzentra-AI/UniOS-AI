
import os
from typing import Any

import httpx


class OllamaProviderError(Exception):
    """Raised when Ollama inference fails."""


class OllamaProvider:
    """Connects KIE Core to the local Ollama LLM."""

    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        ).rstrip("/")

        self.model = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:3b"
        )

        self.timeout = 90.0

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        capability: str = "general",
    ) -> dict[str, Any]:

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3
            },
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()
            data = response.json()

            content = data.get("message", {}).get("content")

            if not isinstance(content, str) or not content.strip():
                raise OllamaProviderError(
                    "Ollama returned an empty response."
                )

            return {
                "content": content.strip(),
                "provider": "ollama",
                "model": self.model,
                "capability": capability,
            }

        except httpx.TimeoutException as exc:
            raise OllamaProviderError(
                "Ollama request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise OllamaProviderError(
                f"Ollama HTTP error: {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise OllamaProviderError(
                "Cannot connect to Ollama. Check the server."
            ) from exc

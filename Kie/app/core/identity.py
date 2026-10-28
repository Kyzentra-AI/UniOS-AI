from typing import Any

from app.schemas.request import KIERequest


class IdentityEngine:
    """
    Sprint 2 Identity Engine.

    Resolves the identity information provided by UniOS
    and produces a normalized identity context for KIE.
    """

    def resolve(self, request: KIERequest) -> dict[str, Any]:
        return {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "role": request.role,
        }
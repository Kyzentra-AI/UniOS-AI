from typing import Any


class ToolRouter:
    """
    Sprint 4 Tool Routing Engine.

    Provides controlled routing for approved KIE tools.

    The router:
    - allowlists approved tools
    - validates tool arguments
    - checks permissions
    - applies timeout limits
    - limits payload size
    - normalizes routing results
    - reports controlled failures

    This layer selects and validates tools.
    Actual external tool execution remains behind
    approved tool integrations.
    """

    DEFAULT_TOOLS = {
        "knowledge",
        "retrieval",
        "calculator",
        "assessment",
    }

    LEARNING_TOOL_MAP = {
        "explain": ["knowledge", "retrieval"],
        "teach": ["knowledge", "retrieval"],
        "practice": ["knowledge"],
        "revise": ["knowledge", "retrieval"],
        "assess": ["assessment"],
        "summarize": ["knowledge", "retrieval"],
        "continue-learning": ["knowledge", "retrieval"],
    }

    DEFAULT_TIMEOUT_SECONDS = 10

    MAX_TIMEOUT_SECONDS = 30

    MAX_ARGUMENT_PAYLOAD = 4096

    def __init__(
        self,
        allowed_tools: set[str] | None = None,
    ) -> None:
        self.allowed_tools = (
            allowed_tools
            if allowed_tools is not None
            else set(self.DEFAULT_TOOLS)
        )

    def route_learning_tool(
        self,
        learning_action: str,
        requested_tool: str | None = None,
        arguments: dict[str, Any] | None = None,
        permissions: set[str] | None = None,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """
        Route a tool request for a learning action.
        """

        arguments = arguments or {}
        permissions = permissions or set()

        if learning_action not in self.LEARNING_TOOL_MAP:
            return self._failure(
                code="unsupported_learning_action",
                message=(
                    "No learning tool routing policy exists "
                    f"for action: {learning_action}"
                ),
            )

        available_tools = self.LEARNING_TOOL_MAP[
            learning_action
        ]

        if requested_tool is None:
            return {
                "status": "routed",
                "learning_action": learning_action,
                "tool": available_tools[0],
                "available_tools": available_tools,
                "arguments": arguments,
                "timeout_seconds": self._resolve_timeout(
                    timeout_seconds
                ),
            }

        if requested_tool not in available_tools:
            return self._failure(
                code="tool_not_allowed_for_action",
                message=(
                    f"Tool '{requested_tool}' is not allowed "
                    f"for learning action '{learning_action}'."
                ),
            )

        if requested_tool not in self.allowed_tools:
            return self._failure(
                code="tool_not_allowlisted",
                message=(
                    f"Tool '{requested_tool}' is not "
                    "allowlisted."
                ),
            )

        argument_error = self._validate_arguments(
            arguments
        )

        if argument_error is not None:
            return self._failure(
                code="invalid_tool_arguments",
                message=argument_error,
            )

        permission_error = self._check_permission(
            requested_tool,
            permissions,
        )

        if permission_error is not None:
            return self._failure(
                code="tool_permission_denied",
                message=permission_error,
            )

        timeout = self._resolve_timeout(
            timeout_seconds
        )

        return {
            "status": "routed",
            "learning_action": learning_action,
            "tool": requested_tool,
            "available_tools": available_tools,
            "arguments": arguments,
            "timeout_seconds": timeout,
        }

    def _validate_arguments(
        self,
        arguments: dict[str, Any],
    ) -> str | None:
        """
        Validate basic tool argument requirements.
        """

        if not isinstance(arguments, dict):
            return "Tool arguments must be a dictionary."

        if len(str(arguments)) > self.MAX_ARGUMENT_PAYLOAD:
            return "Tool argument payload exceeds the allowed limit."

        return None

    def _check_permission(
        self,
        tool: str,
        permissions: set[str],
    ) -> str | None:
        """
        Validate that the caller has permission to use
        the selected tool.
        """

        if not permissions:
            return None

        if tool not in permissions:
            return (
                f"Permission denied for tool '{tool}'."
            )

        return None

    def _resolve_timeout(
        self,
        timeout_seconds: int | None,
    ) -> int:
        """
        Apply a bounded timeout policy.
        """

        if timeout_seconds is None:
            return self.DEFAULT_TIMEOUT_SECONDS

        if timeout_seconds <= 0:
            return self.DEFAULT_TIMEOUT_SECONDS

        return min(
            timeout_seconds,
            self.MAX_TIMEOUT_SECONDS,
        )

    def _failure(
        self,
        code: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Return a normalized controlled failure.
        """

        return {
            "status": "failed",
            "error": {
                "code": code,
                "message": message,
            },
        }
from typing import Any


class ToolRouter:
    """
    Sprint 4 + Sprint 5 Tool Routing Engine.

    Provides controlled routing for approved KIE tools.

    Sprint 4 responsibilities:
    - allowlist approved tools
    - validate tool arguments
    - check permissions
    - apply timeout limits
    - limit payload size
    - normalize routing results
    - report controlled failures

    Sprint 5 responsibilities:
    - route tools according to artifact/project type
    - support coding, research, document, and analysis
      routing policies
    - avoid forcing non-coding artifacts through coding tools
    - keep routing limited to approved/allowlisted tools

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

    ARTIFACT_TOOL_MAP = {
        "CODING": [],
        "RESEARCH": [
            "knowledge",
            "retrieval",
        ],
        "ANALYSIS": [
            "knowledge",
            "retrieval",
            "calculator",
        ],
        "DOCUMENT": [],
        "DESIGN": [
            "knowledge",
            "retrieval",
        ],
        "BUSINESS": [
            "knowledge",
            "retrieval",
            "calculator",
        ],
    }

    ARTIFACT_ALIASES = {
        "CODE": "CODING",
        "CODING": "CODING",
        "SOFTWARE": "CODING",
        "DEVELOPMENT": "CODING",
        "RESEARCH": "RESEARCH",
        "ANALYSIS": "ANALYSIS",
        "DATA_ANALYSIS": "ANALYSIS",
        "DATA-ANALYSIS": "ANALYSIS",
        "DOCUMENT": "DOCUMENT",
        "DOCUMENTATION": "DOCUMENT",
        "DESIGN": "DESIGN",
        "UX": "DESIGN",
        "UI": "DESIGN",
        "BUSINESS": "BUSINESS",
        "BUSINESS_CASE": "BUSINESS",
        "BUSINESS-CASE": "BUSINESS",
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

        return self._route_requested_tool(
            requested_tool=requested_tool,
            available_tools=available_tools,
            arguments=arguments,
            permissions=permissions,
            timeout_seconds=timeout_seconds,
            context_key="learning_action",
            context_value=learning_action,
        )

    def route_build_tool(
        self,
        artifact_type: str,
        requested_tool: str | None = None,
        arguments: dict[str, Any] | None = None,
        permissions: set[str] | None = None,
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """
        Route a tool request for a Sprint 5 Build artifact.

        Tool selection is based on artifact type rather than
        assuming that every project is a coding project.
        """

        arguments = arguments or {}
        permissions = permissions or set()

        normalized_type = self._normalize_artifact_type(
            artifact_type
        )

        if normalized_type not in self.ARTIFACT_TOOL_MAP:
            return self._failure(
                code="unsupported_artifact_type",
                message=(
                    "No Build tool routing policy exists "
                    f"for artifact type: {artifact_type}"
                ),
            )

        available_tools = self.ARTIFACT_TOOL_MAP[
            normalized_type
        ]

        if not available_tools:
            return self._failure(
                code="no_approved_tool_for_artifact",
                message=(
                    f"No approved tool integration is currently "
                    f"available for artifact type '{normalized_type}'."
                ),
            )

        if requested_tool is None:
            selected_tool = self._select_first_allowed_tool(
                available_tools
            )

            if selected_tool is None:
                return self._failure(
                    code="no_allowlisted_tool_for_artifact",
                    message=(
                        f"No configured tool for artifact type "
                        f"'{normalized_type}' is currently allowlisted."
                    ),
                )

            return {
                "status": "routed",
                "artifact_type": normalized_type,
                "tool": selected_tool,
                "available_tools": available_tools,
                "arguments": arguments,
                "timeout_seconds": self._resolve_timeout(
                    timeout_seconds
                ),
            }

        return self._route_requested_tool(
            requested_tool=requested_tool,
            available_tools=available_tools,
            arguments=arguments,
            permissions=permissions,
            timeout_seconds=timeout_seconds,
            context_key="artifact_type",
            context_value=normalized_type,
        )

    def _route_requested_tool(
        self,
        requested_tool: str,
        available_tools: list[str],
        arguments: dict[str, Any],
        permissions: set[str],
        timeout_seconds: int | None,
        context_key: str,
        context_value: str,
    ) -> dict[str, Any]:
        """
        Validate and route an explicitly requested tool.
        """

        if requested_tool not in available_tools:
            if context_key == "learning_action":
                return self._failure(
                    code="tool_not_allowed_for_action",
                    message=(
                        f"Tool '{requested_tool}' is not allowed "
                        f"for learning action '{context_value}'."
                    ),
                )

            return self._failure(
                code="tool_not_allowed_for_context",
                message=(
                    f"Tool '{requested_tool}' is not allowed "
                    f"for {context_key} '{context_value}'."
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

        return {
            "status": "routed",
            context_key: context_value,
            "tool": requested_tool,
            "available_tools": available_tools,
            "arguments": arguments,
            "timeout_seconds": self._resolve_timeout(
                timeout_seconds
            ),
        }

    def _select_first_allowed_tool(
        self,
        available_tools: list[str],
    ) -> str | None:
        """
        Select the first tool that is currently allowlisted.
        """

        for tool in available_tools:
            if tool in self.allowed_tools:
                return tool

        return None

    @classmethod
    def _normalize_artifact_type(
        cls,
        artifact_type: str,
    ) -> str:
        """
        Normalize artifact/project type aliases.
        """

        normalized = str(
            artifact_type
        ).strip().upper()

        return cls.ARTIFACT_ALIASES.get(
            normalized,
            normalized,
        )

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
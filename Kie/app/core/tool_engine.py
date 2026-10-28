from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """
    Defines a tool that KIE is allowed to invoke.
    """

    name: str
    description: str
    handler: Callable[..., Any]
    requires_permission: bool = False


class ToolEngine:
    """
    KIE Tool Engine foundation.

    Responsibilities:
    - Maintain an allowlist of tools
    - Validate requested tools
    - Check basic permission requirements
    - Invoke approved tools
    - Normalize tool results
    - Produce structured errors
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """
        Register an allowlisted tool.
        """

        self._tools[tool.name] = tool

    def is_allowed(self, tool_name: str) -> bool:
        """
        Check whether a tool is registered and allowed.
        """

        return tool_name in self._tools

    def list_tools(self) -> list[str]:
        """
        Return the names of all allowlisted tools.
        """

        return list(self._tools.keys())

    def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        permission_granted: bool = True,
    ) -> dict[str, Any]:
        """
        Safely invoke an allowlisted tool.
        """

        arguments = arguments or {}

        if not self.is_allowed(tool_name):
            return {
                "status": "error",
                "error": {
                    "code": "TOOL_NOT_ALLOWED",
                    "message": f"Tool '{tool_name}' is not allowlisted",
                },
            }

        tool = self._tools[tool_name]

        if tool.requires_permission and not permission_granted:
            return {
                "status": "error",
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": f"Permission denied for tool '{tool_name}'",
                },
            }

        try:
            result = tool.handler(**arguments)

            return {
                "status": "success",
                "tool": tool_name,
                "result": result,
            }

        except Exception:
            return {
                "status": "error",
                "tool": tool_name,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": "Tool execution failed",
                },
            }
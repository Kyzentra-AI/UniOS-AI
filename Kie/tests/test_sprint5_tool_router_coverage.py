
import pytest

from app.core.tool_router import ToolRouter


@pytest.mark.parametrize(
    ("artifact_type", "expected_tool"),
    [
        ("RESEARCH", "knowledge"),
        ("ANALYSIS", "knowledge"),
        ("BUSINESS", "knowledge"),
        ("DESIGN", "knowledge"),
    ],
)
def test_non_coding_artifacts_route_to_approved_tools(
    artifact_type,
    expected_tool,
):
    result = ToolRouter().route_build_tool(
        artifact_type=artifact_type,
    )

    assert result["status"] == "routed"
    assert result["artifact_type"] == artifact_type
    assert result["tool"] == expected_tool


def test_build_routing_rejects_tool_outside_artifact_policy():
    result = ToolRouter().route_build_tool(
        artifact_type="RESEARCH",
        requested_tool="calculator",
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "tool_not_allowed_for_context"


def test_build_routing_rejects_non_allowlisted_tool():
    router = ToolRouter(allowed_tools={"knowledge"})

    result = router.route_build_tool(
        artifact_type="ANALYSIS",
        requested_tool="calculator",
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "tool_not_allowlisted"


def test_build_routing_rejects_invalid_argument_payload():
    result = ToolRouter().route_build_tool(
        artifact_type="ANALYSIS",
        requested_tool="calculator",
        arguments={"expression": "2 + 2"},
    )

    assert result["status"] == "routed"
    assert result["arguments"]["expression"] == "2 + 2"


def test_build_routing_rejects_oversized_arguments():
    result = ToolRouter().route_build_tool(
        artifact_type="ANALYSIS",
        requested_tool="calculator",
        arguments={"data": "x" * 5000},
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "invalid_tool_arguments"


@pytest.mark.parametrize(
    ("requested_timeout", "expected_timeout"),
    [
        (None, 10),
        (5, 5),
        (100, 30),
        (0, 10),
        (-1, 10),
    ],
)
def test_build_routing_applies_bounded_timeouts(
    requested_timeout,
    expected_timeout,
):
    result = ToolRouter().route_build_tool(
        artifact_type="ANALYSIS",
        requested_tool="calculator",
        timeout_seconds=requested_timeout,
    )

    assert result["status"] == "routed"
    assert result["timeout_seconds"] == expected_timeout


def test_build_routing_reports_when_no_tool_is_allowlisted():
    router = ToolRouter(allowed_tools={"assessment"})

    result = router.route_build_tool(
        artifact_type="RESEARCH",
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "no_allowlisted_tool_for_artifact"


def test_build_permission_is_enforced_when_permissions_are_supplied():
    result = ToolRouter().route_build_tool(
        artifact_type="ANALYSIS",
        requested_tool="calculator",
        permissions={"knowledge"},
    )

    assert result["status"] == "failed"
    assert result["error"]["code"] == "tool_permission_denied"

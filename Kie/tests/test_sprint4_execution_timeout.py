
import time

import pytest

from app.core.reliability import (
    ExecutionReliability,
    ExecutionTimeoutError,
)


def test_successful_operation_completes_within_timeout():
    reliability = ExecutionReliability(
        max_retries=0,
        timeout_seconds=1,
    )

    result = reliability.execute(lambda: "completed")

    assert result["status"] == "success"
    assert result["result"] == "completed"
    assert result["attempts"] == 1
    assert result["fallback_used"] is False


def test_slow_operation_returns_controlled_timeout_failure():
    reliability = ExecutionReliability(
        max_retries=0,
        timeout_seconds=0.02,
    )

    def slow_operation():
        time.sleep(0.2)
        return "late result"

    result = reliability.execute(slow_operation)

    assert result["status"] == "failed"
    assert result["result"] is None
    assert result["attempts"] == 1
    assert result["error"]["type"] == "ExecutionTimeoutError"


def test_timeout_retries_respect_configured_limit():
    reliability = ExecutionReliability(
        max_retries=1,
        timeout_seconds=0.02,
    )

    result = reliability.execute(
        lambda: time.sleep(0.2),
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 2
    assert result["fallback_used"] is False
    assert result["error"]["type"] == "ExecutionTimeoutError"


def test_fallback_runs_once_after_primary_timeouts():
    reliability = ExecutionReliability(
        max_retries=0,
        timeout_seconds=0.02,
    )

    fallback_calls = {"count": 0}

    def slow_operation():
        time.sleep(0.2)

    def fallback_operation():
        fallback_calls["count"] += 1
        return "safe fallback"

    result = reliability.execute(
        slow_operation,
        fallback_operation,
    )

    assert result["status"] == "fallback"
    assert result["result"] == "safe fallback"
    assert result["attempts"] == 1
    assert result["fallback_used"] is True
    assert fallback_calls["count"] == 1
    assert result["error"]["type"] == "ExecutionTimeoutError"


def test_per_call_timeout_overrides_default():
    reliability = ExecutionReliability(
        max_retries=0,
        timeout_seconds=1,
    )

    result = reliability.execute(
        lambda: time.sleep(0.2),
        timeout_seconds=0.02,
    )

    assert result["status"] == "failed"
    assert result["error"]["type"] == "ExecutionTimeoutError"


def test_non_positive_timeout_is_rejected():
    with pytest.raises(ValueError):
        ExecutionReliability(timeout_seconds=0)

    reliability = ExecutionReliability()

    with pytest.raises(ValueError):
        reliability.execute(
            lambda: "unused",
            timeout_seconds=-1,
        )


def test_timeout_error_is_a_timeout_error():
    error = ExecutionTimeoutError("deadline exceeded")

    assert isinstance(error, TimeoutError)

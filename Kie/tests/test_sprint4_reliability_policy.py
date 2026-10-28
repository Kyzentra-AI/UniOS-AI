
from app.core.reliability import ExecutionReliability


def test_connection_error_is_retried():
    reliability = ExecutionReliability(max_retries=2)
    calls = {"count": 0}

    def operation():
        calls["count"] += 1
        if calls["count"] < 3:
            raise ConnectionError("Connection temporarily unavailable")
        return "recovered"

    result = reliability.execute(operation)

    assert result["status"] == "success"
    assert result["result"] == "recovered"
    assert result["attempts"] == 3
    assert calls["count"] == 3


def test_timeout_error_is_retried():
    reliability = ExecutionReliability(max_retries=1)
    calls = {"count": 0}

    def operation():
        calls["count"] += 1
        if calls["count"] == 1:
            raise TimeoutError("Temporary timeout")
        return "recovered"

    result = reliability.execute(operation)

    assert result["status"] == "success"
    assert result["attempts"] == 2


def test_value_error_is_not_retried():
    reliability = ExecutionReliability(max_retries=3)
    calls = {"count": 0}

    def operation():
        calls["count"] += 1
        raise ValueError("Invalid input")

    result = reliability.execute(operation)

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert calls["count"] == 1
    assert result["error"]["type"] == "ValueError"


def test_non_retryable_error_uses_fallback_once():
    reliability = ExecutionReliability(max_retries=3)
    fallback_calls = {"count": 0}

    def operation():
        raise ValueError("Invalid request")

    def fallback():
        fallback_calls["count"] += 1
        return "safe fallback"

    result = reliability.execute(operation, fallback)

    assert result["status"] == "fallback"
    assert result["result"] == "safe fallback"
    assert result["attempts"] == 1
    assert fallback_calls["count"] == 1


def test_runtime_error_respects_retry_limit():
    reliability = ExecutionReliability(max_retries=2)
    calls = {"count": 0}

    def operation():
        calls["count"] += 1
        raise RuntimeError("Temporary service failure")

    result = reliability.execute(operation)

    assert result["status"] == "failed"
    assert result["attempts"] == 3
    assert calls["count"] == 3

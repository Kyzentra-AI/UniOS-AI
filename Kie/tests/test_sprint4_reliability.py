from app.core.reliability import ExecutionReliability


def test_successful_operation_returns_success():
    reliability = ExecutionReliability()

    result = reliability.execute(
        lambda: "learning result"
    )

    assert result["status"] == "success"
    assert result["result"] == "learning result"
    assert result["attempts"] == 1
    assert result["fallback_used"] is False


def test_failed_operation_retries_within_limit():
    reliability = ExecutionReliability(
        max_retries=2
    )

    attempts = {"count": 0}

    def failing_operation():
        attempts["count"] += 1
        raise RuntimeError("AI service unavailable")

    result = reliability.execute(
        failing_operation
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 3
    assert attempts["count"] == 3
    assert result["fallback_used"] is False


def test_retry_can_recover_from_temporary_failure():
    reliability = ExecutionReliability(
        max_retries=2
    )

    attempts = {"count": 0}

    def temporary_failure():
        attempts["count"] += 1

        if attempts["count"] < 2:
            raise RuntimeError("Temporary AI failure")

        return "recovered result"

    result = reliability.execute(
        temporary_failure
    )

    assert result["status"] == "success"
    assert result["result"] == "recovered result"
    assert result["attempts"] == 2
    assert result["fallback_used"] is False


def test_fallback_is_used_after_retries_fail():
    reliability = ExecutionReliability(
        max_retries=2
    )

    def primary_operation():
        raise RuntimeError("Primary AI service failed")

    def fallback_operation():
        return "fallback response"

    result = reliability.execute(
        primary_operation,
        fallback_operation,
    )

    assert result["status"] == "fallback"
    assert result["result"] == "fallback response"
    assert result["attempts"] == 3
    assert result["fallback_used"] is True


def test_fallback_is_not_used_when_primary_succeeds():
    reliability = ExecutionReliability(
        max_retries=2
    )

    fallback_called = {"value": False}

    def primary_operation():
        return "primary response"

    def fallback_operation():
        fallback_called["value"] = True
        return "fallback response"

    result = reliability.execute(
        primary_operation,
        fallback_operation,
    )

    assert result["status"] == "success"
    assert result["result"] == "primary response"
    assert result["fallback_used"] is False
    assert fallback_called["value"] is False


def test_fallback_failure_returns_controlled_failure():
    reliability = ExecutionReliability(
        max_retries=1
    )

    def primary_operation():
        raise RuntimeError("Primary failure")

    def fallback_operation():
        raise RuntimeError("Fallback failure")

    result = reliability.execute(
        primary_operation,
        fallback_operation,
    )

    assert result["status"] == "failed"
    assert result["result"] is None
    assert result["fallback_used"] is True
    assert "error" in result
    assert "original_error" in result


def test_zero_retries_means_single_primary_attempt():
    reliability = ExecutionReliability(
        max_retries=0
    )

    attempts = {"count": 0}

    def failing_operation():
        attempts["count"] += 1
        raise RuntimeError("Failure")

    result = reliability.execute(
        failing_operation
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert attempts["count"] == 1


def test_negative_retry_configuration_is_bounded_to_zero():
    reliability = ExecutionReliability(
        max_retries=-5
    )

    attempts = {"count": 0}

    def failing_operation():
        attempts["count"] += 1
        raise RuntimeError("Failure")

    result = reliability.execute(
        failing_operation
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 1
    assert attempts["count"] == 1


def test_error_is_normalized():
    reliability = ExecutionReliability(
        max_retries=0
    )

    def failing_operation():
        raise ValueError("Invalid model response")

    result = reliability.execute(
        failing_operation
    )

    assert result["status"] == "failed"
    assert result["error"]["type"] == "ValueError"
    assert (
        result["error"]["message"]
        == "Invalid model response"
    )


def test_fallback_receives_no_unbounded_retry():
    reliability = ExecutionReliability(
        max_retries=1
    )

    primary_attempts = {"count": 0}
    fallback_attempts = {"count": 0}

    def primary_operation():
        primary_attempts["count"] += 1
        raise RuntimeError("Primary failure")

    def fallback_operation():
        fallback_attempts["count"] += 1
        return "safe fallback"

    result = reliability.execute(
        primary_operation,
        fallback_operation,
    )

    assert result["status"] == "fallback"
    assert primary_attempts["count"] == 2
    assert fallback_attempts["count"] == 1
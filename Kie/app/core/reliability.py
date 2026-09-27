from typing import Any, Callable


class ExecutionReliability:
    """
    Sprint 4 Execution Reliability Layer.

    Provides bounded retry and fallback handling for
    KIE execution failures.

    The reliability layer:
    - limits retry attempts
    - retries only within the configured budget
    - supports fallback execution
    - returns normalized success/failure results
    - prevents unbounded execution
    - preserves the original error information
    """

    DEFAULT_MAX_RETRIES = 2

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.max_retries = max(
            0,
            max_retries,
        )

    def execute(
        self,
        operation: Callable[[], Any],
        fallback: Callable[[], Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an operation with bounded retries.

        If all retries fail and a fallback is available,
        the fallback is executed once.

        The operation itself is never retried indefinitely.
        """

        attempts = 0
        last_error: Exception | None = None

        while attempts <= self.max_retries:
            attempts += 1

            try:
                result = operation()

                return {
                    "status": "success",
                    "result": result,
                    "attempts": attempts,
                    "fallback_used": False,
                }

            except Exception as error:
                last_error = error

        if fallback is not None:
            try:
                fallback_result = fallback()

                return {
                    "status": "fallback",
                    "result": fallback_result,
                    "attempts": attempts,
                    "fallback_used": True,
                    "error": self._error_details(
                        last_error
                    ),
                }

            except Exception as fallback_error:
                return {
                    "status": "failed",
                    "result": None,
                    "attempts": attempts,
                    "fallback_used": True,
                    "error": self._error_details(
                        fallback_error
                    ),
                    "original_error": self._error_details(
                        last_error
                    ),
                }

        return {
            "status": "failed",
            "result": None,
            "attempts": attempts,
            "fallback_used": False,
            "error": self._error_details(
                last_error
            ),
        }

    def _error_details(
        self,
        error: Exception | None,
    ) -> dict[str, str]:
        """
        Normalize execution errors so raw exception
        objects do not leak through the reliability layer.
        """

        if error is None:
            return {
                "type": "UnknownError",
                "message": "Unknown execution failure.",
            }

        return {
            "type": type(error).__name__,
            "message": str(error),
        }
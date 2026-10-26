
import queue
import threading
from typing import Any, Callable


class ExecutionTimeoutError(TimeoutError):
    """Raised when an operation exceeds its configured deadline."""


class ExecutionReliability:
    """
    Sprint 4 execution reliability layer.

    Provides:
    - Configurable per-attempt execution deadlines.
    - Bounded retries for retryable errors.
    - At most one fallback attempt.
    - Structured success and failure responses.

    A timed-out synchronous operation runs in a daemon thread.
    Python cannot safely force-stop that thread, so the operation
    may continue in the background after a timeout is reported.
    """

    DEFAULT_MAX_RETRIES = 2
    DEFAULT_TIMEOUT_SECONDS = 30.0

    RETRYABLE_EXCEPTIONS = (
        ConnectionError,
        TimeoutError,
        RuntimeError,
    )

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.max_retries = max(0, max_retries)

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        self.timeout_seconds = float(timeout_seconds)

    def _run_with_timeout(
        self,
        operation: Callable[[], Any],
        timeout_seconds: float,
    ) -> Any:
        result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(
            maxsize=1
        )

        def run() -> None:
            try:
                result_queue.put((True, operation()))
            except BaseException as error:
                result_queue.put((False, error))

        worker = threading.Thread(
            target=run,
            name="kie-execution",
            daemon=True,
        )
        worker.start()
        worker.join(timeout_seconds)

        if worker.is_alive():
            raise ExecutionTimeoutError(
                f"Operation exceeded {timeout_seconds:g} seconds"
            )

        succeeded, value = result_queue.get_nowait()

        if succeeded:
            return value

        raise value

    def execute(
        self,
        operation: Callable[[], Any],
        fallback: Callable[[], Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        timeout = (
            self.timeout_seconds
            if timeout_seconds is None
            else float(timeout_seconds)
        )

        if timeout <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        attempts = 0
        last_error: Exception | None = None

        while attempts < self.max_retries + 1:
            attempts += 1

            try:
                result = self._run_with_timeout(operation, timeout)
                return {
                    "status": "success",
                    "result": result,
                    "attempts": attempts,
                    "fallback_used": False,
                }
            except Exception as error:
                last_error = error

                if not isinstance(error, self.RETRYABLE_EXCEPTIONS):
                    break

        if fallback is not None:
            try:
                fallback_result = self._run_with_timeout(
                    fallback,
                    timeout,
                )
                return {
                    "status": "fallback",
                    "result": fallback_result,
                    "attempts": attempts,
                    "fallback_used": True,
                    "error": self._error_details(last_error),
                }
            except Exception as fallback_error:
                return {
                    "status": "failed",
                    "result": None,
                    "attempts": attempts,
                    "fallback_used": True,
                    "error": self._error_details(fallback_error),
                    "original_error": self._error_details(last_error),
                }

        return {
            "status": "failed",
            "result": None,
            "attempts": attempts,
            "fallback_used": False,
            "error": self._error_details(last_error),
        }

    @staticmethod
    def _error_details(
        error: Exception | None,
    ) -> dict[str, str]:
        if error is None:
            return {
                "type": "UnknownError",
                "message": "Unknown execution failure.",
            }

        return {
            "type": type(error).__name__,
            "message": str(error),
        }

import math
import threading
import time
from collections import deque

from fastapi import HTTPException, Request, status

from src.config import settings

_login_attempts: dict[str, deque[float]] = {}
_login_attempts_lock = threading.Lock()


class RateLimitConfigurationError(RuntimeError):
    """Raised when login rate-limit configuration is unsafe."""


def validate_login_rate_limit_configuration() -> None:
    """Ensure login rate-limit configuration is safe."""

    if settings.login_rate_limit_attempts <= 0:
        raise RateLimitConfigurationError(
            "LOGIN_RATE_LIMIT_ATTEMPTS "
            "must be greater than zero."
        )

    if settings.login_rate_limit_window_seconds <= 0:
        raise RateLimitConfigurationError(
            "LOGIN_RATE_LIMIT_WINDOW_SECONDS "
            "must be greater than zero."
        )


def _client_identifier(request: Request) -> str:
    """Return the direct client IP used for login rate limiting."""

    if request.client is None:
        return "unknown"

    return request.client.host


def enforce_login_rate_limit(
    request: Request,
) -> None:
    """Reject login requests that exceed the per-client limit."""

    client_id = _client_identifier(request)
    now = time.monotonic()
    cutoff = now - settings.login_rate_limit_window_seconds

    with _login_attempts_lock:
        attempts = _login_attempts.setdefault(
            client_id,
            deque(),
        )

        while attempts and attempts[0] <= cutoff:
            attempts.popleft()

        if len(attempts) >= settings.login_rate_limit_attempts:
            retry_after = max(
                1,
                math.ceil(
                    settings.login_rate_limit_window_seconds
                    - (now - attempts[0])
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts.",
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        attempts.append(now)


def reset_login_rate_limit() -> None:
    """Clear login rate-limit state."""

    with _login_attempts_lock:
        _login_attempts.clear()

import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request, Response

logger = logging.getLogger(__name__)

RequestHandler = Callable[[Request], Awaitable[Response]]


async def log_requests(
    request: Request,
    call_next: RequestHandler,
) -> Response:
    """Log HTTP request method, path, status, and processing time."""

    start_time = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - start_time) * 1000

        logger.exception(
            "%s %s status=500 duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise

    duration_ms = (perf_counter() - start_time) * 1000

    logger.info(
        "%s %s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response

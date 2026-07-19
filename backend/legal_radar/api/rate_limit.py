"""Small process-local rate limiter for expensive API operations."""

from __future__ import annotations

import math
import time
from collections import OrderedDict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

from backend.legal_radar.settings import get_settings


class SlidingWindowRateLimiter:
    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        max_clients: int = 10_000,
    ) -> None:
        if max_requests < 1 or window_seconds < 1 or max_clients < 1:
            raise ValueError("Rate-limit values must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._requests: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    def check(self, key: str, *, now: float | None = None) -> int | None:
        """Record one request and return retry seconds when the client is limited."""
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            timestamps = self._requests.get(key)
            if timestamps is None:
                if len(self._requests) >= self.max_clients:
                    self._requests.popitem(last=False)
                timestamps = deque()
                self._requests[key] = timestamps
            else:
                self._requests.move_to_end(key)
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.max_requests:
                return max(1, math.ceil(timestamps[0] + self.window_seconds - current))
            timestamps.append(current)
        return None


settings = get_settings()
qa_rate_limiter = SlidingWindowRateLimiter(
    max_requests=settings.qa_rate_limit,
    window_seconds=settings.rate_limit_window_seconds,
)


def enforce_qa_rate_limit(request: Request) -> None:
    """Raise HTTP 429 if the client has exceeded the configured QA rate limit."""
    client_key = request.client.host if request.client else "unknown"
    retry_after = qa_rate_limiter.check(client_key)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quá nhiều yêu cầu phân tích. Vui lòng thử lại sau.",
            headers={"Retry-After": str(retry_after)},
        )

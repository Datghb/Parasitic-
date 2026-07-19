from backend.legal_radar.api.rate_limit import SlidingWindowRateLimiter


def test_sliding_window_rejects_requests_over_limit() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

    assert limiter.check("client-a", now=100.0) is None
    assert limiter.check("client-a", now=101.0) is None
    assert limiter.check("client-a", now=102.0) == 58


def test_sliding_window_recovers_after_window_and_isolates_clients() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=10)

    assert limiter.check("client-a", now=100.0) is None
    assert limiter.check("client-b", now=101.0) is None
    assert limiter.check("client-a", now=110.0) is None

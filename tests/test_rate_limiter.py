from .test_data_helper import rate_limited_headers
from webexevents.rate_limiter import RateLimiter


def test_rate_limiter():
    rate_limiter = RateLimiter(rate_limited_headers)

    assert rate_limiter.daily_based_cost_threshold == 2000
    assert rate_limiter.used_daily_based_cost == 62
    assert rate_limiter.second_based_cost_threshold == 500
    assert rate_limiter.used_second_based_cost == 1
    assert rate_limiter.daily_retry_after_in_second == 10
    assert rate_limiter.secondly_retry_after_in_ms == 20


def test_rate_limiter_empty_header():
    standard_header = {
        "DATE": "Tue, 23 Jul 2024 20:03:47 GMT",
        "CONTENT-TYPE": "application/json; charset=utf-8",
        "CONTENT-LENGTH": "245"
    }

    rate_limiter = RateLimiter(standard_header)

    assert rate_limiter.daily_based_cost_threshold is None
    assert rate_limiter.used_daily_based_cost is None
    assert rate_limiter.second_based_cost_threshold is None
    assert rate_limiter.used_second_based_cost is None

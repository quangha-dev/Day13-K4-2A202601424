import pytest
from app.metrics import (
    percentile,
    record_error,
    record_request,
    reset_metrics,
    snapshot,
)


@pytest.fixture(autouse=True)
def reset_metrics_state():
    """Reset global metrics state before and after each test case."""
    reset_metrics()
    yield
    reset_metrics()


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100
    assert percentile([], 50) == 0.0
    assert percentile([100], 95) == 100.0


def test_error_rate_zero_requests() -> None:
    data = snapshot()
    assert data["traffic"] == 0
    assert data["error_rate_pct"] == 0.0
    assert data["error_breakdown"] == {}


def test_error_rate_all_success() -> None:
    record_request(latency_ms=100, cost_usd=0.01, tokens_in=50, tokens_out=20, quality_score=0.9)
    record_request(latency_ms=150, cost_usd=0.02, tokens_in=60, tokens_out=30, quality_score=0.85)
    
    data = snapshot()
    assert data["traffic"] == 2
    assert data["error_rate_pct"] == 0.0
    assert data["total_cost_usd"] == 0.03
    assert data["tokens_in_total"] == 110
    assert data["tokens_out_total"] == 50


def test_error_rate_mixed() -> None:
    # 3 success requests
    record_request(latency_ms=100, cost_usd=0.01, tokens_in=50, tokens_out=20, quality_score=0.9)
    record_request(latency_ms=120, cost_usd=0.01, tokens_in=50, tokens_out=20, quality_score=0.9)
    record_request(latency_ms=110, cost_usd=0.01, tokens_in=50, tokens_out=20, quality_score=0.9)

    # 1 error
    record_error("timeout_error")

    data = snapshot()
    assert data["traffic"] == 3
    assert data["error_breakdown"]["timeout_error"] == 1
    # 1 error out of 4 total requests = 25.0%
    assert data["error_rate_pct"] == 25.0


def test_error_rate_all_errors() -> None:
    record_error("internal_server_error")
    record_error("internal_server_error")
    record_error("rate_limit_exceeded")

    data = snapshot()
    assert data["traffic"] == 0
    assert data["error_breakdown"]["internal_server_error"] == 2
    assert data["error_breakdown"]["rate_limit_exceeded"] == 1
    # 3 errors out of 3 total requests = 100.0%
    assert data["error_rate_pct"] == 100.0


def test_snapshot_structure() -> None:
    data = snapshot()
    expected_keys = {
        "traffic",
        "latency_p50",
        "latency_p95",
        "latency_p99",
        "avg_cost_usd",
        "total_cost_usd",
        "tokens_in_total",
        "tokens_out_total",
        "error_breakdown",
        "error_rate_pct",
        "quality_avg",
    }
    assert expected_keys.issubset(data.keys())


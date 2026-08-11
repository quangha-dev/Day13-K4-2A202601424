from __future__ import annotations

from datetime import datetime, timezone

from scripts.render_dashboard import calculate, render


def test_runtime_dashboard_contains_six_required_panels() -> None:
    timestamp = datetime.now(timezone.utc)
    records = [
        {"event": "request_received", "_timestamp": timestamp},
        {
            "event": "response_sent",
            "_timestamp": timestamp,
            "latency_ms": 150,
            "cost_usd": 0.002,
            "tokens_in": 30,
            "tokens_out": 100,
            "quality_score": 0.9,
        },
    ]

    page = render(calculate(records), "Test dashboard", "data/logs.jsonl")

    for panel_title in (
        "Latency P50 / P95 / P99",
        "Traffic",
        "Error rate",
        "Total cost",
        "Input / Output tokens",
        "Quality proxy",
    ):
        assert panel_title in page
    assert "150 / 150 / 150 ms" in page
    assert "0.00% (0 lỗi)" in page

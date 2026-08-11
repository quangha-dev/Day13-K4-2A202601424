from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.render_dashboard import calculate, load_records, render


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


def test_load_records_can_select_latest_run(tmp_path: Path) -> None:
    path = tmp_path / "logs.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(
                {
                    "ts": f"2026-08-11T10:00:0{index}Z",
                    "event": "request_received",
                    "sequence": index,
                }
            )
            for index in range(5)
        ),
        encoding="utf-8",
    )

    records = load_records(path, take_last=2)

    assert [record["sequence"] for record in records] == [3, 4]

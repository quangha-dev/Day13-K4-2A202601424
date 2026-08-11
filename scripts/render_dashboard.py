from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    index = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[index])


def load_records(
    path: Path,
    window_minutes: int = 60,
    take_first: int | None = None,
    take_last: int | None = None,
) -> list[dict]:
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        records.append({**record, "_timestamp": timestamp})

    if take_first is not None:
        records = records[:take_first]
    if take_last is not None:
        records = records[-take_last:]
    if not records:
        return []
    newest = max(record["_timestamp"] for record in records)
    start = newest - timedelta(minutes=window_minutes)
    return [record for record in records if record["_timestamp"] >= start]


def calculate(records: list[dict]) -> dict[str, float | int]:
    received = [record for record in records if record.get("event") == "request_received"]
    responses = [record for record in records if record.get("event") == "response_sent"]
    failures = [record for record in records if record.get("event") == "request_failed"]
    latencies = [float(record.get("latency_ms", 0)) for record in responses]
    qualities = [float(record.get("quality_score", 0)) for record in responses]

    return {
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "traffic": len(received),
        "errors": len(failures),
        "error_rate_pct": round(len(failures) / len(received) * 100, 2) if received else 0.0,
        "total_cost_usd": round(sum(float(record.get("cost_usd", 0)) for record in responses), 6),
        "tokens_in_total": sum(int(record.get("tokens_in", 0)) for record in responses),
        "tokens_out_total": sum(int(record.get("tokens_out", 0)) for record in responses),
        "quality_avg": round(mean(qualities), 3) if qualities else 0.0,
    }


def card(title: str, value: str, detail: str, status: str) -> str:
    return (
        f'<section class="card {html.escape(status)}">\n'
        f'  <div class="card-title">{html.escape(title)}</div>\n'
        f'  <div class="card-value">{html.escape(value)}</div>\n'
        f'  <div class="card-detail">{html.escape(detail)}</div>\n'
        "</section>\n"
    )


def render(metrics: dict[str, float | int], title: str, source: Path) -> str:
    latency_status = "ok" if float(metrics["latency_p95"]) <= 3000 else "alert"
    error_status = "ok" if float(metrics["error_rate_pct"]) <= 2 else "alert"
    cost_status = "ok" if float(metrics["total_cost_usd"]) <= 2.5 else "alert"
    total_tokens = int(metrics["tokens_in_total"]) + int(metrics["tokens_out_total"])
    token_status = "ok" if total_tokens <= 50000 else "alert"
    quality_status = "ok" if float(metrics["quality_avg"]) >= 0.75 else "alert"

    cards = "".join(
        [
            card(
                "Latency P50 / P95 / P99",
                f"{metrics['latency_p50']:.0f} / {metrics['latency_p95']:.0f} / {metrics['latency_p99']:.0f} ms",
                "SLO: P95 ≤ 3000 ms",
                latency_status,
            ),
            card("Traffic", f"{metrics['traffic']} requests", "Cửa sổ 60 phút", "ok"),
            card(
                "Error rate",
                f"{metrics['error_rate_pct']:.2f}% ({metrics['errors']} lỗi)",
                "SLO: ≤ 2%",
                error_status,
            ),
            card(
                "Total cost",
                f"${metrics['total_cost_usd']:.6f}",
                "Ngưỡng: ≤ $2.50",
                cost_status,
            ),
            card(
                "Input / Output tokens",
                f"{metrics['tokens_in_total']} / {metrics['tokens_out_total']}",
                "Ngưỡng tổng: ≤ 50,000 tokens",
                token_status,
            ),
            card(
                "Quality proxy",
                f"{metrics['quality_avg']:.3f}",
                "SLO: ≥ 0.75",
                quality_status,
            ),
        ]
    )
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, Segoe UI, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #07111f; color: #e8f0fa; }}
    main {{ width: 1180px; min-height: 720px; margin: 0 auto; padding: 42px; }}
    header {{ display: flex; justify-content: space-between; align-items: end; margin-bottom: 28px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .subtitle, .meta {{ color: #9fb0c5; font-size: 14px; }}
    .badge {{ padding: 8px 12px; border: 1px solid #31506d; border-radius: 999px; color: #9fd4ff; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
    .card {{ min-height: 190px; padding: 24px; border-radius: 16px; border: 1px solid #243b53; background: linear-gradient(145deg, #0d1b2b, #101f32); box-shadow: 0 10px 30px #0005; }}
    .card.ok {{ border-top: 4px solid #35d07f; }}
    .card.alert {{ border-top: 4px solid #ff5d6c; background: linear-gradient(145deg, #25131b, #161b2a); }}
    .card-title {{ color: #9fb0c5; text-transform: uppercase; letter-spacing: .08em; font-size: 13px; }}
    .card-value {{ margin: 28px 0 18px; font-size: 29px; font-weight: 750; }}
    .card-detail {{ color: #b9c8d8; font-size: 14px; }}
    footer {{ margin-top: 26px; display: flex; justify-content: space-between; color: #7f94aa; font-size: 12px; }}
  </style>
</head>
<body>
  <main>
    <header>
      <div><h1>{html.escape(title)}</h1><div class="subtitle">6 Golden Signals · dữ liệu runtime thật từ JSONL</div></div>
      <div class="badge">Time range: 60 phút · Refresh: 30 giây</div>
    </header>
    <div class="grid">{cards}</div>
    <footer><span>Nguồn: {html.escape(str(source))}</span><span>Generated UTC: {generated_at}</span></footer>
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render dashboard evidence từ log JSONL thật")
    parser.add_argument("--input", type=Path, default=Path("data/logs.jsonl"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("submission/evidence/cp2-dashboard-runtime.html"),
    )
    parser.add_argument("--title", default="Day 13 AI Observability — Baseline")
    parser.add_argument(
        "--take-first",
        type=int,
        help="Chỉ dùng số record đầu tiên để tái tạo một snapshot evidence đã ghi nhận.",
    )
    parser.add_argument(
        "--take-last",
        type=int,
        help="Chỉ dùng số record cuối cùng để tạo snapshot của lượt chạy mới nhất.",
    )
    args = parser.parse_args()

    if args.take_first is not None and args.take_last is not None:
        parser.error("--take-first và --take-last không được dùng đồng thời")
    records = load_records(
        args.input,
        take_first=args.take_first,
        take_last=args.take_last,
    )
    if not records:
        raise SystemExit(f"Không có log hợp lệ trong {args.input}")
    metrics = calculate(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(metrics, args.title, args.input), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"Dashboard đã tạo: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

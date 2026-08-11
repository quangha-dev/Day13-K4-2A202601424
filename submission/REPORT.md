# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-DAY13-2A202601424
- Repository URL: https://github.com/quangha-dev/Day13-K4-2A202601424
- Commit SHA kỹ thuật dùng làm mốc: `f0302ce`; khi nộp lấy SHA mới nhất bằng `git rev-parse HEAD`.
- Thành viên và vai trò:
  - Thành viên A (Raijuz): API & Middleware.
  - Thành viên B (Huy): Security Engineer.
  - Thành viên C (Nguyễn Trần Nghĩa): Metrics & Dashboard.
  - Thành viên D (Hải): SRE & Alerts Engineer.
  - Thành viên E (Nguyễn Quang Hà): QA & Chief Investigator.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 — [`evidence/cp1-validate-logs.txt`](evidence/cp1-validate-logs.txt)
- Tổng số traces: Chưa thu thập — Langfuse chưa được cấu hình trên máy tích hợp.
- Số PII leak còn lại: 0.
- Link/đường dẫn dashboard: [`../config/dashboard.yaml`](../config/dashboard.yaml) và [`evidence/cp2-dashboard-6-panels.png`](evidence/cp2-dashboard-6-panels.png).
- Public tests: 50 tests pass, 2 warning deprecation không ảnh hưởng kết quả.

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/cp1-correlation-log.json`](evidence/cp1-correlation-log.json) — `request_received` và `response_sent` cùng ID `req-df839ca4`.
- Evidence PII redaction: [`evidence/cp1-pii-redacted.json`](evidence/cp1-pii-redacted.json) — email, số điện thoại và credit card đều được thay bằng marker.
- Evidence trace waterfall: Chưa thu thập — cần bổ sung `evidence/cp2-trace-waterfall.png` sau khi bật Langfuse.
- Giải thích một span đáng chú ý: Component timing CP3 đo `retrieve=2512.5 ms` và `generate=150.7 ms`; retrieval chiếm khoảng 94.3%. Cần đối chiếu bằng waterfall Langfuse trước khi nộp.

## 4. Prompt versioning

- Prompt name: Dự kiến `day13-chat` theo contract; chưa tạo trên project Langfuse.
- Version/label baseline: Chưa có evidence thật.
- Version/label candidate: Chưa có evidence thật.
- Trace ID của mỗi version: Chưa có.
- Bằng chứng đổi label hoặc rollback: Chưa có. Các file ảnh bắt buộc còn thiếu được liệt kê trong [`EVIDENCE_CHECKLIST.md`](EVIDENCE_CHECKLIST.md).

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: [`evidence/cp2-dashboard-6-panels.png`](evidence/cp2-dashboard-6-panels.png), [`evidence/cp2-dashboard-runtime.html`](evidence/cp2-dashboard-runtime.html) và [`evidence/cp2-dashboard-validator.txt`](evidence/cp2-dashboard-validator.txt). Quy cách tại [`../docs/dashboard-spec.md`](../docs/dashboard-spec.md) và contract [`../config/dashboard.yaml`](../config/dashboard.yaml). Dashboard được tạo từ log runtime thật và thể hiện **4 Trụ cột AI Observability (Performance, Cost, Quality, Reliability)**:
  - **Layer 1 (Overview - Leadership)**: Sức khỏe hệ thống tổng thể, Uptime, Total Spend, CSAT/Quality score.
  - **Layer 2 (Detail - Engineering)**: 6 Tier-1 Core Golden Signals (Latency P95, Traffic RPM, Error Rate %, Total Cost USD, Input/Output Tokens, Quality Score) + Tier-2 Enterprise Metrics (TTFT, RAG Search Latency, Cost by Feature, Token Speed).
  - **Layer 3 (Drill-down - Debugging)**: Langfuse Traces Waterfall & Structured JSON Logs Search via `correlation_id`.
- SLO đã chọn và lý do: 
  - Latency P95 <= 3000ms (Sử dụng P95 thay vì Average để loại bỏ bóp méo do hiện tượng long-tail latency đặc thù của LLM).
  - Error rate <= 2% (Áp dụng công thức zero-safe hợp nhất cả System errors và Model/API errors).
  - Total cost <= 2.5 USD (Giám sát rủi ro bùng nổ chi phí phi tuyến tính do prompt quá dài hoặc truy vấn lặp).
  - Total tokens <= 50000 (Phân tách và kiểm soát Input Tokens vs Output Tokens để phát hiện nghẽn xử lý).
  - Quality score >= 0.75 (Đóng vai trò phanh an toàn - Safety Guardrail - phát hiện sự thoái hóa chất lượng/hallucination ngay cả khi HTTP 200 OK).

- Alert rules và runbook: [`../config/alert_rules.yaml`](../config/alert_rules.yaml) và [`../docs/alerts.md`](../docs/alerts.md). Ba rule gồm high latency P95, elevated error rate và cost budget exceeded; đều symptom-based, có owner và ba bước điều tra đầu tiên.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (`rag_slow`, affected feature `monitoring`, threshold 2000 ms).
- Triệu chứng từ metrics: P95 tăng từ 152 ms lên 2652 ms; error rate vẫn 0%. Sau disable/restart, P95 hồi phục về 151 ms. Evidence: [`evidence/cp3-metrics-incident.png`](evidence/cp3-metrics-incident.png), [`evidence/cp3-metrics-baseline.json`](evidence/cp3-metrics-baseline.json), [`evidence/cp3-metrics-incident.json`](evidence/cp3-metrics-incident.json), [`evidence/cp3-metrics-recovery.json`](evidence/cp3-metrics-recovery.json).
- Trace ID liên quan: Chưa có — Langfuse chưa được cấu hình. Component timing thật cho thấy `retrieve=2512.5 ms`, `generate=150.7 ms`; xem [`evidence/cp3-component-timing.json`](evidence/cp3-component-timing.json). Cần bổ sung trace ID/waterfall Langfuse trước khi nộp.
- Log line/correlation ID liên quan: `req-939a54c9`, `response_sent.latency_ms=2651`; xem [`evidence/cp3-correlated-log.json`](evidence/cp3-correlated-log.json).
- Root cause: incident `rag_slow` thêm khoảng 2.5 giây trong RAG retrieval. Retrieval chiếm khoảng 94.3% thời gian hai component. Việc gọi sync `agent.run()` trong async endpoint còn khuếch đại client tail latency khi concurrency cao.
- Fix action: disable route chậm; dùng cache/fallback retrieval; áp dụng timeout/circuit breaker; đưa tác vụ blocking sang worker/thread pool phù hợp.
- Preventive measure: giữ sub-span retrieval/generation, alert P95 theo feature, load test concurrency trong CI và theo dõi chênh lệch client/internal latency. Báo cáo đầy đủ: [`evidence/cp3-investigation.md`](evidence/cp3-investigation.md).

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Raijuz (Thành viên A) | Correlation ID middleware, enrichment, response headers, exception handling và load-test error path. | [Commit 103fc50](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/103fc50) | Contextvars phải được clear/bind theo request; error response vẫn cần correlation ID. |
| Huy (Thành viên B) | Recursive PII scrubbing, regex email/phone/CCCD/card/passport/address và security tests. | [Commit d8069a2](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/d8069a2) | Scrubber phải chạy trước serializer và cần negative test để không phá metadata kỹ thuật. |
| Nguyễn Trần Nghĩa (Thành viên C) | `error_rate_pct` zero-safe, unit tests và dashboard spec 6 Golden Signals. | [Commit 77d7033](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/77d7033) | Percentile/error rate cần zero-safe; dashboard AI phải theo dõi thêm cost và quality. |
| Hải (Thành viên D) | SLO và nền tảng runbook symptom-based; phần còn thiếu được hoàn thiện trong tích hợp CP2. | [Commit 167edaf](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/167edaf) | Alert nên dựa trên triệu chứng/SLO và có ba bước điều tra đầu tiên rõ ràng. |
| Nguyễn Quang Hà (Thành viên E) | QA tích hợp, sub-span RAG/LLM, correlation trace metadata, dashboard runtime, điều tra CP3 và tổng hợp evidence/report. | Commits `05b5ab8`, `868771b`, `f0302ce`; xem [`BAO_CAO_THANH_VIEN_E.md`](BAO_CAO_THANH_VIEN_E.md) | Metrics phát hiện triệu chứng; component trace khoanh vùng; correlation log chứng minh request/root cause. Không dùng trace/key giả khi chưa có Langfuse. |



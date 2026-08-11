# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-DAY13-2A202601424
- Repository URL: https://github.com/quangha-dev/Day13-K4-2A202601424
- Commit hoàn tất kỹ thuật/evidence: `9c335d9`; khi nộp dùng SHA mới nhất từ `git rev-parse HEAD`.
- Nhóm có 5 thành viên, được ánh xạ vào 4 workstream chính của README: Logging & PII (A, B); Tracing & Prompt Version (E); Dashboard/SLO/Alert (C, D); Incident/Report/Demo (E).
- Thành viên và phần việc:
  - Thành viên A (Raijuz): API & Middleware.
  - Thành viên B (Huy): Security Engineer.
  - Thành viên C (Nguyễn Trần Nghĩa): Metrics & Dashboard.
  - Thành viên D (Hải): SRE & Alerts Engineer.
  - Thành viên E (Nguyễn Quang Hà): QA & Chief Investigator.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 — [`evidence/cp1-validate-logs.txt`](evidence/cp1-validate-logs.txt)
- Baseline starter phục dựng từ commit gốc `b95464c`: 30/100, 10 request đều có correlation ID `MISSING`; xem [`evidence/cp0-baseline-validator.txt`](evidence/cp0-baseline-validator.txt). Sau CP1 đạt 100/100.
- Health/API: `ok=true`, tracing bật, tất cả incident tắt; xem [`evidence/cp0-health.png`](evidence/cp0-health.png) và [`evidence/cp0-health.json`](evidence/cp0-health.json).
- Tổng số traces: đã xác minh hơn 10 traces; riêng baseline có 10 trace ID trong [`evidence/cp2-trace-summary.json`](evidence/cp2-trace-summary.json) và ảnh danh sách [`evidence/cp2-trace-list-10.jpg`](evidence/cp2-trace-list-10.jpg).
- Số PII leak còn lại: 0.
- Link/đường dẫn dashboard: [`../config/dashboard.yaml`](../config/dashboard.yaml) và [`evidence/cp2-dashboard-6-panels.png`](evidence/cp2-dashboard-6-panels.png).
- Public và regression tests: 51 tests pass, 2 warning deprecation không ảnh hưởng kết quả.

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/cp1-correlation-log.json`](evidence/cp1-correlation-log.json) — `request_received` và `response_sent` cùng ID `req-df839ca4`.
- Evidence PII redaction: [`evidence/cp1-pii-redacted.json`](evidence/cp1-pii-redacted.json) — email, số điện thoại và credit card đều được thay bằng marker.
- Evidence trace waterfall: [`evidence/cp2-trace-waterfall.jpg`](evidence/cp2-trace-waterfall.jpg) hiển thị đầy đủ `run/retrieve/generate`.
- Giải thích một span đáng chú ý: waterfall incident đo `retrieve=2501 ms`, `generate=151 ms`; retrieval là span gây chậm. Kết quả khớp phép đo runtime độc lập `retrieve=2512.5 ms`, `generate=150.7 ms`.

### 3.1. Kết quả phần việc Security Engineer (Huy — Thành viên B)

Phạm vi thực hiện gồm `app/pii.py`, processor `scrub_event` trong `app/logging_config.py` và kiểm thử tại `tests/test_pii.py`.

- Bổ sung nhận diện passport và địa chỉ Việt Nam bên cạnh email, số điện thoại Việt Nam, CCCD và thẻ tín dụng.
- Nâng `scrub_event` từ xử lý riêng `payload`/`event` thành scrub toàn bộ giá trị chuỗi trong log, bao gồm cấu trúc lồng nhau dạng `dict`, `list` và `tuple`.
- Đăng ký `scrub_event` trong pipeline trước `JsonlFileProcessor` và `JSONRenderer`, bảo đảm PII được che trước khi log được ghi xuống file hoặc render ra output.
- Bổ sung kiểm thử positive cho các định dạng PII và negative cases để giữ nguyên correlation ID, timestamp, tên model, token, cost và session ID hợp lệ.

| Loại dữ liệu | Ví dụ đầu vào kiểm thử | Marker đầu ra mong đợi |
|---|---|---|
| Email | `student@vinuni.edu.vn` | `[REDACTED_EMAIL]` |
| Điện thoại Việt Nam | `0901234567`, `+84 90 123 4567` | `[REDACTED_PHONE_VN]` |
| CCCD | `001234567890` | `[REDACTED_CCCD]` |
| Thẻ tín dụng | `4111-1111-1111-1111` | `[REDACTED_CREDIT_CARD]` |
| Passport | `B1234567` | `[REDACTED_PASSPORT]` |
| Địa chỉ Việt Nam | `123 Đường Nguyễn Trãi`, `Phường Bến Nghé` | `[REDACTED_ADDRESS_VI]` |

Kết quả chạy `python3 scripts/validate_logs.py`:

```text
Total log records analyzed: 23
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 11
Potential PII leaks detected: 0
Estimated Score: 100/100
```

Lệnh kiểm tra phần việc:

```bash
python -m pytest tests/test_pii.py tests/test_validate_logs.py -q
python scripts/validate_logs.py
```

> Evidence terminal/ảnh minh họa: `[TỰ ĐIỀN ĐƯỜNG DẪN SAU KHI CHỤP]`.

## 4. Prompt versioning

- Prompt name: `day13-chat` trên project Langfuse thật.
- Version/label baseline: v1, labels `baseline` và `production` sau rollback.
- Version/label candidate: v2, labels `candidate` và `latest` sau rollback.
- Trace mỗi version: baseline v1 `686ab6ff4d29e9c63166872f3f02de45`; candidate v2 `8893a6f33bd250aa8f21850da9c6f410`. Evidence: [`evidence/cp2-prompt-baseline-trace.jpg`](evidence/cp2-prompt-baseline-trace.jpg), [`evidence/cp2-prompt-candidate-trace.jpg`](evidence/cp2-prompt-candidate-trace.jpg) và [`evidence/cp2-prompt-version-evidence.json`](evidence/cp2-prompt-version-evidence.json).
- Rollback thật: gán `production` cho v2 và tạo trace `b248cf5fd57de58321ad05caffaf67b5`, sau đó chuyển `production` về v1 và tạo trace `7c127e4ab129ed90ced9a101720b380b`. Ảnh trước/sau thật: [`evidence/cp2-prompt-production-v2-before-rollback.jpg`](evidence/cp2-prompt-production-v2-before-rollback.jpg), [`evidence/cp2-prompt-production-v1-after-rollback.jpg`](evidence/cp2-prompt-production-v1-after-rollback.jpg); đối chiếu [`evidence/cp2-prompt-rollback.json`](evidence/cp2-prompt-rollback.json).

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
- Triệu chứng từ metrics: baseline P95 152 ms; trong lượt challenge có tracing, P95 tăng lên 3626 ms và error rate vẫn 0%. Sau disable/restart, P50 hồi phục 152 ms, P95 1127 ms (cold fetch managed prompt) và vẫn dưới SLO 3000 ms. Evidence: [`evidence/cp3-metrics-incident.png`](evidence/cp3-metrics-incident.png), [`evidence/cp3-metrics-baseline.json`](evidence/cp3-metrics-baseline.json), [`evidence/cp3-metrics-incident.json`](evidence/cp3-metrics-incident.json), [`evidence/cp3-metrics-recovery.json`](evidence/cp3-metrics-recovery.json).
- Trace ID liên quan: `61a5c25ea8a6d57fce2a3c4ea16489df`; waterfall thật cho thấy `run=3628 ms`, `retrieve=2501 ms`, `generate=151 ms`. Evidence: [`evidence/cp3-trace-waterfall.jpg`](evidence/cp3-trace-waterfall.jpg), [`evidence/cp3-trace-summary.json`](evidence/cp3-trace-summary.json) và [`evidence/cp3-component-timing.json`](evidence/cp3-component-timing.json).
- Log line/correlation ID liên quan: `req-49c5faf5`, `response_sent.latency_ms=3626`; metrics, trace và log đều thuộc cùng lượt challenge. Xem [`evidence/cp3-correlated-log.json`](evidence/cp3-correlated-log.json).
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
| Nguyễn Quang Hà (Thành viên E) | QA tích hợp, sub-span RAG/LLM, correlation trace metadata, dashboard runtime, Prompt Management, điều tra CP3 và tổng hợp evidence/report. | Commits `05b5ab8`, `868771b`, `f0302ce`, `c77f491`, `b9ef61b`, `9c335d9`; xem [`BAO_CAO_THANH_VIEN_E.md`](BAO_CAO_THANH_VIEN_E.md) | Metrics phát hiện triệu chứng; waterfall khoanh vùng retrieval; correlation ID nối trace với log. API key thật chỉ lưu cục bộ trong `.env`, không commit. |


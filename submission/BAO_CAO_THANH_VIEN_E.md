# Báo cáo thực hiện — Thành viên E (Nguyễn Quang Hà)

## Vai trò

QA & Chief Investigator: kiểm thử tích hợp, tracing cho RAG/LLM, điều tra challenge theo Metrics → Traces → Logs, tổng hợp evidence và báo cáo nhóm.

## Nhật ký thực hiện

### Khảo sát sau khi pull

- Đã đọc lại code, tests, cấu hình, tài liệu và yêu cầu nộp bài.
- Xác nhận A/B/C/D đã có thay đổi trên `main`, nhưng alert rules/runbook và toàn bộ evidence vẫn chưa hoàn tất.
- Ban đầu chưa có `.env`; sau khi được chủ project cho phép đã tạo key thật, lưu cục bộ trong `.env` bị Git ignore và không đưa secret vào evidence/commit.
- Xác nhận `config/challenge.json` là bản release K4, không chỉnh sửa file này.

### CP0 — Setup & baseline

- Tạo và sử dụng `.venv` cục bộ; dependencies cài từ `requirements.txt`.
- Phục dựng commit starter gốc `b95464c` trong thư mục tạm bị Git ignore, chạy API và 10 query thật.
- Baseline thật: 30/100; 20 records thiếu required fields, 20 records thiếu enrichment, 0 correlation ID hợp lệ và cả 10 response trả `MISSING`.
- Chạy health check bản hoàn thiện: API trả `ok=true`, tracing bật, tất cả incident tắt.
- Evidence: `evidence/cp0-baseline-validator.txt`, `evidence/cp0-health.png`, `evidence/cp0-health.json`, `evidence/cp0-pytest.txt`.

### CP1 — Structured logging, correlation ID và PII

- Chạy API và load test thật với 10 query, concurrency 5.
- Phát hiện regex passport làm hỏng một số correlation ID dạng `req-c7040763`; validator vẫn báo 100/100 nên đã bổ sung kiểm tra thủ công.
- Sửa regex để vẫn che passport chữ thường nhưng loại trừ prefix `req-`; thêm regression test bảo vệ correlation ID.
- Chạy lại log sạch: 21 records, 10 correlation ID hợp lệ/duy nhất, không thiếu metadata, PII leak = 0, validator = 100/100.
- Lưu evidence correlation request/response và ba loại redaction email/phone/credit card.
- Evidence: `evidence/cp1-validate-logs.txt`, `evidence/cp1-correlation-log.json`, `evidence/cp1-pii-redacted.json`, `evidence/cp1-metrics-baseline.json`.

## Phần đang thực hiện tiếp

- [x] CP2 code: thêm sub-span `retrieve`/`generate` và gắn correlation ID vào trace metadata.
- [x] CP2 dashboard: tạo renderer đọc log JSONL thật, dashboard 6 panel và ảnh baseline runtime.
- [x] CP2 SRE: hoàn thiện ba alert rules, ba runbook và đồng bộ ngưỡng SLO.
- [x] CP2: Langfuse ≥10 traces, prompt v1/v2 và rollback thật.
- [x] CP3 metrics/log: chạy challenge chính thức, lưu baseline/incident/recovery, component timing và correlated log thật.
- [x] CP3 trace Langfuse: lấy trace ID, waterfall và nối với log bằng correlation ID thật.
- [x] Hoàn tất `REPORT.md`, danh sách evidence và kiểm tra nộp bài.

### CP2 — Phần đã xác minh không cần Langfuse

- Dashboard validator: 6/6 panel hợp lệ.
- Dashboard runtime baseline đọc 21 log records trong cửa sổ 60 phút: P95 152 ms, 10 requests, error rate 0%, cost 0.021645 USD, 330/1377 tokens, quality 0.88.
- Ảnh thật: `evidence/cp2-dashboard-6-panels.png`; HTML nguồn: `evidence/cp2-dashboard-runtime.html`.
- Alert rules không còn TODO; mỗi rule có severity, symptom-based condition, owner và runbook.
- Full test sau thay đổi CP2 và renderer evidence: 51 tests pass.
- Langfuse thật có 10 baseline traces; trace waterfall chứa `run/retrieve/generate` và metadata correlation ID.
- Tạo prompt `day13-chat` v1 (`baseline`) và v2 (`candidate`), chạy trace cho từng version.
- Gán `production` cho v2 để kiểm chứng rồi rollback về v1; lưu trace ID và ảnh trạng thái thật trước/sau. Hai ảnh trace hiển thị trực tiếp `prompt_name`, `prompt_label`, `prompt_version`.

### CP3 — Điều tra challenge thật

- Challenge: `day13-k4-observability-v1`, incident `rag_slow`, feature `monitoring`, threshold 2000 ms.
- Metrics: baseline P95 152 ms; lượt challenge có tracing tăng lên 3626 ms, error rate vẫn 0%; sau disable/restart P50 về 152 ms và P95 1127 ms, vẫn dưới SLO.
- Component timing: `retrieve=2512.5 ms`, `generate=150.7 ms`; retrieval chiếm khoảng 94.3%.
- Langfuse waterfall: trace `61a5c25ea8a6d57fce2a3c4ea16489df`, `run=3628 ms`, `retrieve=2501 ms`, `generate=151 ms`.
- Log: correlation ID `req-49c5faf5` nối đúng metrics/trace trên với `request_received` và `response_sent.latency_ms=3626` trong cùng lượt chạy.
- Phát hiện thêm: client tail latency 8–13 giây do sync `agent.run()` block async event loop khi concurrency=5.
- Root cause, mitigation, fix và preventive measure được ghi trong `evidence/cp3-investigation.md`.

### Kiểm kê nộp bài

- Đã tạo `EVIDENCE_CHECKLIST.md` và đối chiếu từng yêu cầu của `SUBMISSION.md`/`docs/grading-evidence.md`.
- Đã đủ CP0, CP1, dashboard, SLO/alerts/runbook, CP2 Langfuse/Prompt Management và CP3 Metrics → Traces → Logs/recovery.
- Các ảnh Langfuse, trace IDs và JSON đối chiếu đều lấy từ project thật; không dùng ảnh, key hay trace giả.

### Nghiệm thu cuối

- `pytest`: 51 passed, 2 warning deprecation; lần chạy đầu gặp lỗi quyền thư mục temp hệ thống Windows, chạy lại với `--basetemp` trong `.venv` đã pass đầy đủ.
- `validate_logs.py`: 100/100 trên 111 records, 54 correlation IDs, PII leak = 0.
- `validate_dashboard.py`: hợp lệ 6/6 panel.
- `.env` và `.venv` đều bị Git ignore; secret scan file tracked không phát hiện key thật; `config/challenge.json` không khác `origin/main`.

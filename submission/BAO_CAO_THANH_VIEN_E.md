# Báo cáo thực hiện — Thành viên E (Nguyễn Quang Hà)

## Vai trò

QA & Chief Investigator: kiểm thử tích hợp, tracing cho RAG/LLM, điều tra challenge theo Metrics → Traces → Logs, tổng hợp evidence và báo cáo nhóm.

## Nhật ký thực hiện

### Khảo sát sau khi pull

- Đã đọc lại code, tests, cấu hình, tài liệu và yêu cầu nộp bài.
- Xác nhận A/B/C/D đã có thay đổi trên `main`, nhưng alert rules/runbook và toàn bộ evidence vẫn chưa hoàn tất.
- Xác nhận chưa có `.env`; tracing Langfuse chưa bật và không có evidence trace thật.
- Xác nhận `config/challenge.json` là bản release K4, không chỉnh sửa file này.

### CP0 — Setup & baseline sau merge

- Tạo và sử dụng `.venv` cục bộ; dependencies cài từ `requirements.txt`.
- Chạy health check thật: API trả `ok=true`, tất cả incident tắt, tracing chưa bật vì chưa có key.
- Chạy toàn bộ public tests: 48 tests pass, chỉ có 2 warning deprecation.
- Evidence: `evidence/cp0-health.json`, `evidence/cp0-pytest.txt`.

Lưu ý trung thực: baseline starter trước khi A/B/C/D sửa không còn trong working tree sau khi pull. Kết quả ghi ở đây là baseline tích hợp hiện tại, không giả lập lại điểm thấp của starter.

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
- [ ] CP2: Langfuse ≥10 traces, prompt v1/v2 và rollback — cần key/project Langfuse thật.
- [x] CP3 metrics/log: chạy challenge chính thức, lưu baseline/incident/recovery, component timing và correlated log thật.
- [ ] CP3 trace Langfuse: cần đăng nhập/project key để lấy trace ID và waterfall thật.
- [ ] Hoàn tất `REPORT.md`, danh sách evidence và kiểm tra nộp bài.

### CP2 — Phần đã xác minh không cần Langfuse

- Dashboard validator: 6/6 panel hợp lệ.
- Dashboard runtime baseline đọc 21 log records trong cửa sổ 60 phút: P95 152 ms, 10 requests, error rate 0%, cost 0.021645 USD, 330/1377 tokens, quality 0.88.
- Ảnh thật: `evidence/cp2-dashboard-6-panels.png`; HTML nguồn: `evidence/cp2-dashboard-runtime.html`.
- Alert rules không còn TODO; mỗi rule có severity, symptom-based condition, owner và runbook.
- Full test sau thay đổi CP2: 50 tests pass.
- Trình duyệt Langfuse hiện dừng tại trang đăng nhập. Không dùng key giả và không ghi nhận trace giả.

### CP3 — Điều tra challenge thật

- Challenge: `day13-k4-observability-v1`, incident `rag_slow`, feature `monitoring`, threshold 2000 ms.
- Metrics: P95 tăng từ 152 ms lên 2652 ms; error rate vẫn 0%; sau disable/restart P95 hồi phục về 151 ms.
- Component timing: `retrieve=2512.5 ms`, `generate=150.7 ms`; retrieval chiếm khoảng 94.3%.
- Log: correlation ID `req-939a54c9` nối `request_received` với `response_sent.latency_ms=2651`.
- Phát hiện thêm: client tail latency 8–13 giây do sync `agent.run()` block async event loop khi concurrency=5.
- Root cause, mitigation, fix và preventive measure được ghi trong `evidence/cp3-investigation.md`.

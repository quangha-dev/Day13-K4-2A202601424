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

- [ ] CP2: sub-span RAG/LLM, trace metadata correlation ID, dashboard runtime, SLO/alerts/runbook.
- [ ] CP2: Langfuse ≥10 traces, prompt v1/v2 và rollback — cần key/project Langfuse thật.
- [ ] CP3: chạy challenge chính thức, lưu metrics/trace/log thật và kết luận root cause.
- [ ] Hoàn tất `REPORT.md`, danh sách evidence và kiểm tra nộp bài.

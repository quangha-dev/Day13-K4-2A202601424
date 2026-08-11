# Tự chấm theo Rubric Day 13

Ngày đối chiếu: 11/08/2026. Đây là kết quả tự đánh giá dựa trên `RUBRIC.md`, không thay thế điểm chính thức của Lab Coach.

## Kết quả dự kiến

| Mục rubric | Điểm tối đa | Điểm dự kiến | Bằng chứng chính |
|---|---:|---:|---|
| A1. Triển khai kỹ thuật | 30 | 30 | `validate_logs.py` 100/100; trace/prompt v1-v2/rollback thật; dashboard validator 6/6; SLO, alerts và runbook đầy đủ. |
| A2. Điều tra incident | 10 | 10 | `evidence/cp3-investigation.md` nối cùng lượt chạy bằng metric P95 3626 ms, trace `61a5c25ea8a6d57fce2a3c4ea16489df` và log `req-49c5faf5`; có fix và preventive measure. |
| A3. Demo và giải thích | 20 | 20 (có điều kiện) | Hệ thống/tests chạy được và evidence đã sẵn sàng; điểm này chỉ được xác nhận khi nhóm demo trực tiếp đúng evidence. |
| B1. Báo cáo và mức độ hiểu bài | 20 | 20 (có điều kiện) | `REPORT.md` và báo cáo cá nhân mô tả rõ phần việc; phần hỏi đáp vẫn do từng thành viên thể hiện trong buổi chấm. |
| B2. Bằng chứng đóng góp | 20 | 20 | Báo cáo dẫn commit cụ thể của A/B/C/D và chuỗi commit tích hợp/evidence của E; thay đổi có thể kiểm tra trong Git. |
| Bonus | +10 | 0 | Nhóm ưu tiên hoàn thiện toàn bộ yêu cầu bắt buộc; không khai báo bonus. |

**Tổng dự kiến: 100/100 nếu demo và hỏi đáp đạt yêu cầu.** Phần có thể xác minh hoàn toàn từ repository hiện đạt 70/70; 30 điểm còn lại phụ thuộc demo trực tiếp và câu trả lời của thành viên.

## Đối chiếu A1 — 30/30

- Logging 10/10: JSON log có `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; PII scrub đệ quy trước khi serialize. Evidence: `evidence/cp1-correlation-log.json`, `evidence/cp1-pii-redacted.json`, `evidence/cp1-validate-logs.txt`.
- Tracing và prompt 10/10: có hơn 10 trace, waterfall `run/retrieve/generate`, prompt `day13-chat` v1/v2, metadata name/label/version và rollback `production` thật. Evidence nằm trong nhóm file `evidence/cp2-*trace*` và `evidence/cp2-prompt-*`.
- Dashboard/SLO/alert 10/10: contract đủ 6 panel, time range 60 phút, refresh 30 giây, threshold và unit; có SLO, ba alert symptom-based và ba runbook. Evidence: `evidence/cp2-dashboard-6-panels.png`, `evidence/cp2-dashboard-validator.txt`, `../config/slo.yaml`, `../config/alert_rules.yaml`, `../docs/alerts.md`.

## Đối chiếu A2 — 10/10

1. Metrics phát hiện triệu chứng: P95 tăng từ 152 ms lên 3626 ms, error rate vẫn 0%.
2. Trace khoanh vùng: trace `61a5c25ea8a6d57fce2a3c4ea16489df` có `retrieve=2501 ms`, lớn hơn rõ rệt `generate=151 ms`.
3. Logs chứng minh: correlation ID `req-49c5faf5` có `response_sent.latency_ms=3626` trong đúng lượt challenge.
4. Root cause: incident `rag_slow` thêm khoảng 2.5 giây vào retrieval; lời giải thích không dựa trên suy đoán đơn lẻ.
5. Fix/prevention: cache/fallback, timeout/circuit breaker, xử lý blocking phù hợp, alert P95 theo feature và load test concurrency trong CI.

## Kịch bản bảo vệ 30 điểm chấm trực tiếp

### Demo A3 trong 3–5 phút

1. Chạy `python -m pytest -q`, `python scripts/validate_logs.py`, `python scripts/validate_dashboard.py`.
2. Mở dashboard incident, chỉ P95 3626 ms và ngưỡng SLO 3000 ms.
3. Mở waterfall trace `61a5c25ea8a6d57fce2a3c4ea16489df`, chỉ span `retrieve=2501 ms`.
4. Dùng `req-49c5faf5` mở `evidence/cp3-correlated-log.json`, chỉ log `response_sent.latency_ms=3626`.
5. Kết luận root cause, nêu fix/prevention và mở recovery P95 1127 ms.

### Nội dung từng thành viên cần trả lời

- A: vòng đời correlation ID, contextvars và vì sao response lỗi vẫn phải có `x-request-id`.
- B: vì sao scrub trước JSON serializer, PII nào được che và vì sao validator 100/100 chưa đủ để kết luận sạch toàn diện.
- C: công thức `error_rate_pct`, xử lý zero-safe, ý nghĩa P50/P95/P99 và sáu panel dashboard.
- D: quan hệ SLI/SLO/threshold, vì sao alert symptom-based cần duration, severity, owner và runbook.
- E: trace ID khác correlation ID, prompt label/version/rollback và cách Metrics → Traces → Logs chứng minh root cause.

## Kết quả nghiệm thu cuối

- `pytest`: 51 passed; hai cảnh báo FastAPI deprecation không ảnh hưởng kết quả.
- `validate_logs.py`: 100/100 trên 111 records, 54 correlation ID, 0 PII leak.
- `validate_dashboard.py`: hợp lệ 6/6 panel.
- 37/37 liên kết tương đối trong `REPORT.md` tồn tại; 13/13 file evidence JSON parse hợp lệ.
- `.env` và `.venv` bị ignore; không phát hiện Langfuse key thật trong file tracked.
- `config/challenge.json` giống `origin/main`, không bị chỉnh sửa.

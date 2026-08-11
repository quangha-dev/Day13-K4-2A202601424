# Kiểm kê evidence trước khi nộp

Cập nhật sau lần chạy tích hợp thật ngày 11/08/2026. Ký hiệu: ✅ đã có và kiểm tra được; ❌ còn thiếu, không được khai báo hoàn tất khi chưa bổ sung.

## CP0 — Setup

| Yêu cầu | Trạng thái | File |
|---|---:|---|
| Health/API chạy | ✅ | `evidence/cp0-health.json` |
| Public tests pass | ✅ | `evidence/cp0-pytest.txt` |
| Baseline starter trước khi sửa | ❌ | Không thể tái tạo trung thực sau khi đã pull code của A–D; report đã ghi rõ hạn chế này. |

## CP1 — Logging, correlation ID và PII

| Yêu cầu | Trạng thái | File |
|---|---:|---|
| Validator cuối 100/100 | ✅ | `evidence/cp1-validate-logs.txt` |
| Correlation ID và metadata | ✅ | `evidence/cp1-correlation-log.json` |
| PII đã redact | ✅ | `evidence/cp1-pii-redacted.json` |
| Metrics baseline | ✅ | `evidence/cp1-metrics-baseline.json` |
| Raw PII leak = 0 | ✅ | `evidence/cp1-validate-logs.txt` |

## CP2 — Metrics, traces, prompt, dashboard và alerts

| Yêu cầu | Trạng thái | File cần nộp |
|---|---:|---|
| Dashboard validator 6/6 | ✅ | `evidence/cp2-dashboard-validator.txt` |
| Dashboard runtime đủ 6 panel | ✅ | `evidence/cp2-dashboard-6-panels.png` |
| Dashboard HTML có thể kiểm tra | ✅ | `evidence/cp2-dashboard-runtime.html` |
| SLO | ✅ | `../config/slo.yaml` |
| Ba alert rules | ✅ | `../config/alert_rules.yaml` |
| Ba runbook | ✅ | `../docs/alerts.md` |
| Danh sách ít nhất 10 Langfuse traces | ❌ | Cần chụp `evidence/cp2-trace-list-10.png`. |
| Một trace waterfall có run/retrieve/generate | ❌ | Cần chụp `evidence/cp2-trace-waterfall.png`. |
| Prompt v1/v2 và labels | ❌ | Cần chụp `evidence/cp2-prompt-versions.png`. |
| Hai trace gắn đúng prompt version/label | ❌ | Cần `evidence/cp2-prompt-baseline-trace.png` và `evidence/cp2-prompt-candidate-trace.png`. |
| Đổi label hoặc rollback production | ❌ | Cần chụp `evidence/cp2-prompt-rollback.png`. |

## CP3 — Challenge

| Yêu cầu | Trạng thái | File |
|---|---:|---|
| Metrics baseline | ✅ | `evidence/cp3-metrics-baseline.json` |
| Metrics incident | ✅ | `evidence/cp3-metrics-incident.json`, `evidence/cp3-metrics-incident.png` |
| Load test challenge thật | ✅ | `evidence/cp3-load-test.txt` |
| Correlated log thật | ✅ | `evidence/cp3-correlated-log.json` |
| Component timing thật | ✅ | `evidence/cp3-component-timing.json` |
| Root cause/fix/prevention | ✅ | `evidence/cp3-investigation.md` |
| Recovery | ✅ | `evidence/cp3-metrics-recovery.json` |
| Trace waterfall/trace ID Langfuse của incident | ❌ | Cần chụp `evidence/cp3-trace-waterfall.png` và ghi trace ID vào report. |

## Việc bắt buộc trước khi push/nộp

1. Đăng nhập hoặc cung cấp project credentials Langfuse trong `.env` cục bộ.
2. Tạo prompt `day13-chat` v1/v2, labels baseline/candidate/production và thực hiện rollback thật.
3. Restart API với `.env`, chạy load test để có ≥10 traces, sau đó chạy lại challenge để lấy waterfall incident.
4. Bổ sung sáu ảnh Langfuse còn thiếu và thay các dòng “Chưa có/Chưa thu thập” trong `REPORT.md`.
5. Chạy lại tests, validators, secret/PII scan và cập nhật SHA nộp cuối.

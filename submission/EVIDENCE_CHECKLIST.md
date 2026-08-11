# Kiểm kê evidence trước khi nộp

Cập nhật sau lần chạy tích hợp và thu thập Langfuse thật ngày 11/08/2026. Ký hiệu: ✅ đã có và kiểm tra được.

## CP0 — Setup

| Yêu cầu | Trạng thái | File |
|---|---:|---|
| Health/API chạy | ✅ | `evidence/cp0-health.png`, `evidence/cp0-health.json` |
| Public tests pass | ✅ | `evidence/cp0-pytest.txt` |
| Baseline starter trước khi sửa | ✅ | `evidence/cp0-baseline-validator.txt` — phục dựng commit gốc `b95464c`, score 30/100. |

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
| Danh sách ít nhất 10 Langfuse traces | ✅ | `evidence/cp2-trace-list-10.jpg`, `evidence/cp2-trace-summary.json` |
| Một trace waterfall có run/retrieve/generate | ✅ | `evidence/cp2-trace-waterfall.jpg` |
| Prompt v1/v2 và labels | ✅ | `evidence/cp2-prompt-versions.jpg`, `evidence/cp2-prompt-version-evidence.json` |
| Hai trace gắn đúng prompt version/label | ✅ | `evidence/cp2-prompt-baseline-trace.jpg`, `evidence/cp2-prompt-candidate-trace.jpg` — thấy trực tiếp name/label/version. |
| Đổi label hoặc rollback production | ✅ | `evidence/cp2-prompt-production-v2-before-rollback.jpg`, `evidence/cp2-prompt-production-v1-after-rollback.jpg`, `evidence/cp2-prompt-rollback.json` |

## CP3 — Challenge

| Yêu cầu | Trạng thái | File |
|---|---:|---|
| Metrics baseline | ✅ | `evidence/cp3-metrics-baseline.json` |
| Metrics incident cùng lượt trace/log | ✅ | `evidence/cp3-metrics-incident.json`, `evidence/cp3-metrics-incident.png` |
| Load test challenge thật | ✅ | `evidence/cp3-load-test.txt` |
| Correlated log thật | ✅ | `evidence/cp3-correlated-log.json` |
| Component timing thật | ✅ | `evidence/cp3-component-timing.json` |
| Root cause/fix/prevention | ✅ | `evidence/cp3-investigation.md` |
| Recovery | ✅ | `evidence/cp3-metrics-recovery.json` |
| Trace waterfall/trace ID Langfuse của incident | ✅ | `evidence/cp3-trace-waterfall.jpg`, `evidence/cp3-trace-summary.json` |

## Việc trước khi push/nộp

1. Chạy lại tests, validators và secret/PII scan lần cuối.
2. Dùng `git status --short` kiểm tra `.env`, `.venv`, cache và log runtime không nằm trong commit.
3. Sau khi tự push, lấy SHA mới nhất bằng `git rev-parse HEAD` để nộp cùng URL repository.

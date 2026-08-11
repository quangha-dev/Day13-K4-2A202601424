# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: Quy cách chi tiết tại [`docs/dashboard-spec.md`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/docs/dashboard-spec.md) và contract [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml).
- SLO đã chọn và lý do: 
  - Latency P95 <= 3000ms (Sử dụng P95 thay vì Average để loại bỏ bóp méo do hiện tượng long-tail latency đặc thù của LLM).
  - Error rate <= 2% (Áp dụng công thức zero-safe hợp nhất cả System errors và Model/API errors).
  - Total cost <= 2.5 USD (Giám sát rủi ro bùng nổ chi phí phi tuyến tính do prompt quá dài hoặc truy vấn lặp).
  - Total tokens <= 50000 (Phân tách và kiểm soát Input Tokens vs Output Tokens để phát hiện nghẽn xử lý).
  - Quality score >= 0.75 (Đóng vai trò phanh an toàn - Safety Guardrail - phát hiện sự thoái hóa chất lượng/hallucination ngay cả khi HTTP 200 OK).
  - Tuân thủ toàn diện chuẩn quốc tế **OpenTelemetry GenAI Semantic Conventions**.

- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nghĩa (Thành viên C) | **Metrics & Dashboard Spec**: Bổ sung `error_rate_pct` zero-safe trong `app/metrics.py`, viết 6 unit tests trong `tests/test_metrics.py`, chuẩn hóa `docs/dashboard-spec.md` theo chuẩn OpenTelemetry GenAI Semantic Conventions. | [Commit 77d7033](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/77d70332e62ee9afc371d9f1da2840dce1670dbd) / PR `dev/nghia` | Nắm vững 6 GenAI Golden Signals (Latency P95, Traffic, Error rate zero-safe, Cost, Tokens, Quality Proxy) và quy trình điều tra 3 tầng Observability (Metrics $\rightarrow$ Traces $\rightarrow$ Logs). |


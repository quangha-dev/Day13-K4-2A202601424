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
- **Bảng Tổng hợp 6 GenAI SLOs và Lập luận Kỹ thuật**:

| Chỉ số (Panel) | OTel Metric Standard | Target SLO | Lập luận Kiến trúc & Lý do Kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Latency** | `gen_ai.client.operation.duration` | $P95 \le 3000\text{ ms}$ | Dùng P95 thay vì Average để bắt trúng hiện tượng long-tail latency đặc thù của LLM. |
| **Traffic** | `http.server.request.count` / RPM | $\text{Rate} \ge 1\text{ rpm}$ | Giám sát lưu lượng thực tế, phát hiện sớm Outage (Drop) hoặc DDoS/Loop bug (Spike). |
| **Error Rate** | `gen_ai.client.error_rate` | $\text{Error Rate} \le 2\%$ | Công thức zero-safe hợp nhất cả System errors và Model/API errors. |
| **Cost** | `gen_ai.usage.cost` | $\text{Total Cost} \le \$2.5$ | Kiểm soát rủi ro bùng nổ chi phí phi tuyến tính do prompt quá dài hoặc truy vấn lặp. |
| **Tokens** | `gen_ai.usage.input_tokens` & `output_tokens` | $\text{Tokens} \le 50000$ | Phân tách Input (Prefill) vs Output (Decode) tokens để tìm chính xác điểm nghẽn. |
| **Quality** | `gen_ai.quality.score` | $\text{Mean} \ge 0.75$ | Đóng vai trò Phanh an toàn (Safety Guardrail) phát hiện hallucination khi HTTP vẫn 200. |

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


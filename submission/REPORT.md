# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-DAY13-2A202601424
- Repository URL: https://github.com/quangha-dev/Day13-K4-2A202601424
- Commit SHA cuối: Cập nhật sau commit hoàn tất cuối cùng
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
- Link/đường dẫn dashboard: [`../config/dashboard.yaml`](../config/dashboard.yaml), evidence runtime bổ sung tại CP2.

## 3. Logging và tracing

- Evidence correlation ID: [`evidence/cp1-correlation-log.json`](evidence/cp1-correlation-log.json) — `request_received` và `response_sent` cùng ID `req-df839ca4`.
- Evidence PII redaction: [`evidence/cp1-pii-redacted.json`](evidence/cp1-pii-redacted.json) — email, số điện thoại và credit card đều được thay bằng marker.
- Evidence trace waterfall: Chưa thu thập — bổ sung sau khi bật Langfuse.
- Giải thích một span đáng chú ý: Sẽ hoàn thiện bằng kết quả điều tra CP3 thật.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: Quy cách chi tiết tại [`docs/dashboard-spec.md`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/docs/dashboard-spec.md) và contract [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml). Đã thiết lập dựa trên **4 Trụ cột AI Observability (Performance, Cost, Quality, Reliability)** và **Mô hình Dashboard 3 Layer cho Stakeholders**:
  - **Layer 1 (Overview - Leadership)**: Sức khỏe hệ thống tổng thể, Uptime, Total Spend, CSAT/Quality score.
  - **Layer 2 (Detail - Engineering)**: 6 Tier-1 Core Golden Signals (Latency P95, Traffic RPM, Error Rate %, Total Cost USD, Input/Output Tokens, Quality Score) + Tier-2 Enterprise Metrics (TTFT, RAG Search Latency, Cost by Feature, Token Speed).
  - **Layer 3 (Drill-down - Debugging)**: Langfuse Traces Waterfall & Structured JSON Logs Search via `correlation_id`.
- SLO đã chọn và lý do: 
  - Latency P95 <= 3000ms (Sử dụng P95 thay vì Average để loại bỏ bóp méo do hiện tượng long-tail latency đặc thù của LLM).
  - Error rate <= 2% (Áp dụng công thức zero-safe hợp nhất cả System errors và Model/API errors).
  - Total cost <= 2.5 USD (Giám sát rủi ro bùng nổ chi phí phi tuyến tính do prompt quá dài hoặc truy vấn lặp).
  - Total tokens <= 50000 (Phân tách và kiểm soát Input Tokens vs Output Tokens để phát hiện nghẽn xử lý).
  - Quality score >= 0.75 (Đóng vai trò phanh an toàn - Safety Guardrail - phát hiện sự thoái hóa chất lượng/hallucination ngay cả khi HTTP 200 OK).

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
| Nghĩa (Thành viên C) | **Metrics & Dashboard Spec**: Bổ sung `error_rate_pct` zero-safe trong `app/metrics.py`, viết 6 unit tests trong `tests/test_metrics.py`, chuẩn hóa & mở rộng `docs/dashboard-spec.md` theo chuẩn kiến trúc Dashboard 2-Tier OpenTelemetry GenAI. | [Commit 1039dd7](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/1039dd7) / PR `dev/nghia` | Nắm vững 6 GenAI Golden Signals cốt lõi (Tier-1) và 6 chỉ số nâng cao Enterprise Tier-2 (TTFT, RAG Latency, Cost per User, Generation Speed, Faithfulness, Token Ratio). |



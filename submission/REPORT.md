# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: `[TỰ ĐIỀN]`
- Repository URL: `[TỰ ĐIỀN]`
- Commit SHA cuối: `[TỰ ĐIỀN SAU KHI HOÀN TẤT BÀI]`
- Thành viên và vai trò: `[TỰ ĐIỀN DANH SÁCH NHÓM]`

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100` (23 log records, kiểm tra ngày 11/08/2026)
- Tổng số traces:
- Số PII leak còn lại: `0`
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction: `[TỰ ĐIỀN ĐƯỜNG DẪN ẢNH, ví dụ: evidence/pii-redaction.png]`
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

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
| Huy (Thành viên B) | **Security Engineer — PII Redaction**: Bổ sung regex passport/địa chỉ Việt Nam; scrub đệ quy mọi trường string trong `dict`, `list`, `tuple`; đưa processor scrub vào logging pipeline trước bước ghi/render JSON; bổ sung test matrix và negative cases bảo vệ dữ liệu kỹ thuật. | [Commit d8069a2](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/d8069a290c553ad645b297049a0a778ec1ad3837) / nhánh `dev/huy` | Hiểu cách thiết kế PII redaction theo hướng defense-in-depth, thứ tự processor trong structured logging và cách cân bằng giữa khả năng phát hiện PII với việc tránh che nhầm metadata phục vụ observability. |
| Nghĩa (Thành viên C) | **Metrics & Dashboard Spec**: Bổ sung `error_rate_pct` zero-safe trong `app/metrics.py`, viết 6 unit tests trong `tests/test_metrics.py`, chuẩn hóa & mở rộng `docs/dashboard-spec.md` theo chuẩn kiến trúc Dashboard 2-Tier OpenTelemetry GenAI. | [Commit 1039dd7](https://github.com/quangha-dev/Day13-K4-2A202601424/commit/1039dd7) / PR `dev/nghia` | Nắm vững 6 GenAI Golden Signals cốt lõi (Tier-1) và 6 chỉ số nâng cao Enterprise Tier-2 (TTFT, RAG Latency, Cost per User, Generation Speed, Faithfulness, Token Ratio). |


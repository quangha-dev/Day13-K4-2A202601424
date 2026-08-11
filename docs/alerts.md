# Alert rules và runbook xử lý sự cố

Các alert dựa trên triệu chứng người dùng hoặc mức tiêu thụ ngân sách, không phụ thuộc tên hàm hay implementation nội bộ. Ngưỡng được đồng bộ với `config/slo.yaml` và `config/dashboard.yaml`.

## Alert 1: High latency P95

- **Tên rule:** `high_latency_p95`
- **Severity:** Warning
- **SLI/SLO:** `latency_p95_ms`; SLO P95 không vượt 3000 ms.
- **Điều kiện:** `latency_p95_ms > 3000` liên tục trong 5 phút.
- **Ảnh hưởng người dùng:** Phản hồi chậm, tăng nguy cơ client timeout/retry và người dùng rời bỏ phiên.
- **Owner:** `on-call-engineer`

### Ba bước kiểm tra đầu tiên

1. Mở dashboard, xác định time window và feature có latency P95/P99 vượt ngưỡng.
2. Mở các trace chậm trong cùng time window, so sánh duration của span `retrieve` và `generate`.
3. Lấy `correlation_id` từ trace, lọc `data/logs.jsonl` và đối chiếu `request_received` với `response_sent`/`request_failed`.

### Mitigation tạm thời

- Bật cache/fallback retrieval nếu span RAG chậm.
- Áp dụng timeout/circuit breaker cho dependency chậm và giới hạn concurrency nếu quá tải.
- Rollback deployment gần nhất nếu sự cố xuất hiện ngay sau thay đổi.

## Alert 2: Elevated error rate

- **Tên rule:** `elevated_error_rate`
- **Severity:** Critical
- **SLI/SLO:** `error_rate_pct`; SLO tỷ lệ lỗi không vượt 2%.
- **Điều kiện:** `error_rate_pct > 5` liên tục trong 3 phút.
- **Ảnh hưởng người dùng:** Request thất bại hoặc trả HTTP 5xx, tính năng AI không sử dụng được.
- **Owner:** `on-call-engineer`

### Ba bước kiểm tra đầu tiên

1. Mở panel Error rate, xác định thời điểm tăng và `error_breakdown` theo loại lỗi.
2. Lọc trace lỗi trong time window, kiểm tra trạng thái và span đầu tiên phát sinh exception.
3. Dùng `correlation_id` lọc log `request_failed`, đọc `error_type` và payload đã redact để xác nhận nguyên nhân.

### Mitigation tạm thời

- Chuyển sang dependency/fallback đang hoạt động hoặc cô lập feature bị lỗi.
- Bật retry có backoff cho lỗi tạm thời; không retry lỗi đầu vào không hợp lệ.
- Rollback cấu hình/deployment gây lỗi và giảm traffic bằng rate limit nếu cần.

## Alert 3: Cost budget exceeded

- **Tên rule:** `cost_budget_exceeded`
- **Severity:** Warning
- **SLI/SLO:** `daily_cost_usd`; ngân sách không vượt 2.5 USD/ngày.
- **Điều kiện:** `daily_cost_usd > 2.5` trong ngày hiện tại.
- **Ảnh hưởng người dùng:** Không gây lỗi tức thời nhưng có nguy cơ hết ngân sách, bị giới hạn dịch vụ hoặc phải tắt tính năng.
- **Owner:** `team-lead`

### Ba bước kiểm tra đầu tiên

1. Mở panel Cost/Tokens, xác định thời điểm cost tăng và mức tăng của output tokens.
2. Lọc trace có cost/token cao, nhóm theo feature, model và session để tìm nguồn tiêu thụ.
3. Dùng `correlation_id` kiểm tra log `response_sent`, đối chiếu `tokens_in`, `tokens_out` và `cost_usd`.

### Mitigation tạm thời

- Giới hạn output tokens và độ dài context; bật cache cho truy vấn lặp.
- Rate limit feature/session tiêu thụ bất thường.
- Chuyển model chi phí thấp hơn khi vẫn đáp ứng quality SLO.

## Quan hệ giữa SLO và alert

SLO error rate là 2%, trong khi alert critical dùng 5% duy trì 3 phút. Khoảng đệm tránh cảnh báo do dao động ngắn nhưng vẫn phát hiện nhanh sự cố ảnh hưởng rõ tới người dùng. Alert latency bám trực tiếp SLO 3000 ms và yêu cầu duy trì 5 phút để giảm noise.

# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1: High latency P95

### SLI/SLO liên quan
- SLI: `latency_p95_ms`
- SLO: P95 không vượt quá 3000ms trong cửa sổ 28 ngày

### Mức độ quan trọng: Warning

### Điều kiện kích hoạt 

Alert kích hoạt khi latency P95 vượt 3000 ms liên tục trong 5 phút.

### Ảnh hưởng người dùng

Người dùng chờ lâu hơn khi gửi yêu cầu. Người dùng dễ từ bỏ chuyển sang nền tảng khác. Timeout request gửi lại thì sẽ tăng traffic và chi phí.

### Ba bước kiểm tra đầu tiên

1. Mở dashboard, xác định thời điểm latency bắt đầu tăng và feature bị ảnh hưởng.
2. Mở các trace bất thường trong cùng time window, so sánh duration của các span `retrieve` và `generate`.
3. Lấy correlation ID từ trace và lọc `data/logs.jsonl` để kiểm tra các event `request_received`, `response_sent` hoặc `request_failed` của cùng request.

### Mitigation

- Nếu retrieval chậm, bật cache hoặc fallback retrieval.
- Áp dụng timeout/circuit breaker cho dependency chậm.
- Giảm concurrency hoặc rate limit nếu hệ thống quá tải.
- Rollback thay đổi gần nhất nếu latency tăng sau deployment.

### Owner

SRE & Alerts Engineer phối hợp với Tracing/Incident Investigator.

1. Mở dashboard, xác định khởi điểm

- Tên:
- Severity:
- SLI/SLO liên quan:
- Điều kiện và thời gian duy trì:
- Ảnh hưởng tới người dùng:
- Ba bước kiểm tra đầu tiên:
- Mitigation tạm thời:
- Owner:

## Alert 2: Cost Budget Exceeded

- Tên:
- Severity:
- SLI/SLO liên quan:
- Điều kiện và thời gian duy trì:
- Ảnh hưởng tới người dùng:
- Ba bước kiểm tra đầu tiên:
- Mitigation tạm thời:
- Owner:

## Alert 3

- Tên:
- Severity:
- SLI/SLO liên quan:
- Điều kiện và thời gian duy trì:
- Ảnh hưởng tới người dùng:
- Ba bước kiểm tra đầu tiên:
- Mitigation tạm thời:
- Owner:

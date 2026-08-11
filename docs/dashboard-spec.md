# Chi tiết Quy cách Dashboard & Tiêu chuẩn AI Observability (Dashboard Specification)

Tài liệu này quy định chi tiết 6 nhóm panel cho **Day 13 AI Observability Dashboard**, tuân thủ theo tiêu chuẩn **Google SRE Golden Signals**, **OpenTelemetry GenAI Semantic Conventions** và **Datadog / Langfuse Observability Framework**.

Contract chuẩn được lưu tại [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml) và hướng dẫn thiết lập runtime tại [`docs/DASHBOARD_SETUP.md`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/docs/DASHBOARD_SETUP.md).

---

## 1. Cơ sở Kỹ thuật: Mở rộng SRE Golden Signals cho GenAI

Hệ thống SRE truyền thống (Google SRE Book) định nghĩa **4 Golden Signals**: Latency, Traffic, Errors, Saturation. 
Đối với ứng dụng **GenAI / LLM**, hệ thống mở rộng thành **6 GenAI Golden Signals**:

```
GenAI Observability = Latency + Traffic + Errors + Cost + Tokens + Quality Proxy
```

### Ánh xạ Tiêu chuẩn OpenTelemetry GenAI Semantic Conventions

| Panel ID | Tên Panel (Dashboard) | OpenTelemetry GenAI Metric Standard | Event & Field Nguồn | Đơn vị & Ngưỡng SLO |
| :--- | :--- | :--- | :--- | :--- |
| `latency` | Latency percentiles | `gen_ai.client.operation.duration` | `response_sent` -> `latency_ms` | `ms` (`P95 <= 3000 ms`) |
| `traffic` | Request traffic | `http.server.request.count` / RPM | `request_received` -> `event` | `RPM` (`rate >= 1 rpm`) |
| `errors` | Error rate and breakdown | `gen_ai.client.error_rate` | `request_failed` -> `error_type` | `%` (`error_rate <= 2 %`) |
| `cost` | Cost over time | `gen_ai.usage.cost` | `response_sent` -> `cost_usd` | `USD` (`total <= $2.5`) |
| `tokens` | Input and output tokens | `gen_ai.usage.input_tokens` & `output_tokens` | `response_sent` -> `tokens_in`, `tokens_out` | `tokens` (`total <= 50000`) |
| `quality` | Quality proxy | `gen_ai.quality.score` | `response_sent` -> `quality_score` | `score` (`mean >= 0.75`) |

---

## 2. Cấu hình Chung (Global Dashboard Settings)

- **Source File**: `data/logs.jsonl`
- **Time Range Mặc định**: 60 phút (`time_range_minutes: 60`)
- **Refresh Interval**: 15 – 30 giây (`refresh_seconds: 30`)
- **Phạm vi hiển thị**: Đúng 6 panel chính đại diện cho 6 nhóm chỉ số quan trọng.

---

## 3. Chi tiết 6 Nhóm Panel

### 3.1. Latency Percentiles (`latency`)
- **Title**: Latency percentiles
- **Event nguồn**: `response_sent`
- **Field nguồn**: `latency_ms`
- **Aggregations**: `p50`, `p95`, `p99`
- **Query / Formula**: `event == "response_sent" | percentile(latency_ms, [50, 95, 99])`
- **Đơn vị**: `ms` (milliseconds)
- **Threshold / SLO Line**: `p95 <= 3000 ms`
- **Lý do Kỹ thuật**: Trong các hệ thống LLM, độ trễ sinh từ có hiện tượng "long-tail latency". Dùng phân vị P95 và P99 thay vì Average giúp phát hiện chính xác các request bị nghẽn mà không bị san bằng bởi các request ngắn.

### 3.2. Request Traffic (`traffic`)
- **Title**: Request traffic
- **Event nguồn**: `request_received`
- **Field nguồn**: `event`
- **Aggregations**: `count`, `rate_per_minute`
- **Query / Formula**: `event == "request_received" | count() by 1m`
- **Đơn vị**: `requests_per_minute` (RPM)
- **Threshold / SLO Line**: `rate_per_minute >= 1`
- **Lý do Kỹ thuật**: Giám sát lưu lượng thực tế để phát hiện sớm hiện tượng sụt giảm lưu lượng (Outage/Network drop) hoặc tăng vọt bất thường (Loop bug / DDoS).

### 3.3. Error Rate & Breakdown (`errors`)
- **Title**: Error rate and breakdown
- **Event nguồn**: `request_received`, `request_failed`
- **Field nguồn**: `error_type`
- **Aggregations**: `error_rate_pct`, `count_by_value`
- **Query / Formula**: `count(event == "request_failed") / count(event == "request_received") * 100; count_by(error_type)`
- **Đơn vị**: `percent` (`%`)
- **Threshold / SLO Line**: `error_rate_pct <= 2 %`
- **Lý do Kỹ thuật**: Công thức tính toán Zero-safe:
  $$\text{error\_rate\_pct} = \begin{cases} \left(\frac{\text{Total Errors}}{\text{TRAFFIC} + \text{Total Errors}}\right) \times 100 & \text{nếu Total Requests} > 0 \\ 0.0 & \text{nếu Total Requests} = 0 \end{cases}$$
  Giúp đo lường chính xác tỷ lệ thất bại của hệ thống và phân loại nguyên nhân lỗi (Internal Server Error, Timeout, Rate Limit API, etc.).

### 3.4. Cost Over Time (`cost`)
- **Title**: Cost over time
- **Event nguồn**: `response_sent`
- **Field nguồn**: `cost_usd`
- **Aggregations**: `sum_by_minute`, `total`
- **Query / Formula**: `event == "response_sent" | sum(cost_usd) by 1m; sum(cost_usd)`
- **Đơn vị**: `usd` (`$`)
- **Threshold / SLO Line**: `total <= 2.5 USD`
- **Lý do Kỹ thuật**: Mô hình GenAI phát sinh chi phí trực tiếp theo token. Cần kiểm soát tổng ngân sách chi trả cho LLM API trong cửa sổ 60 phút để tránh bùng nổ chi phí ngoài dự kiến.

### 3.5. Input & Output Tokens (`tokens`)
- **Title**: Input and output tokens
- **Event nguồn**: `response_sent`
- **Field nguồn**: `tokens_in`, `tokens_out`
- **Aggregations**: `sum_by_field`
- **Query / Formula**: `event == "response_sent" | sum(tokens_in), sum(tokens_out)`
- **Đơn vị**: `tokens`
- **Threshold / SLO Line**: `sum_by_field <= 50000 tokens`
- **Lý do Kỹ thuật**: Phân tách rõ ràng giữa Input Tokens (Prompt / Context memory) và Output Tokens (Generation response). Output Tokens tiêu tốn nhiều thời gian xử lý và chi phí cao hơn đáng kể.

### 3.6. Quality Proxy (`quality`)
- **Title**: Quality proxy
- **Event nguồn**: `response_sent`
- **Field nguồn**: `quality_score`
- **Aggregations**: `mean`
- **Query / Formula**: `event == "response_sent" | mean(quality_score)`
- **Đơn vị**: `score_0_to_1` (Thang điểm 0.0 đến 1.0)
- **Threshold / SLO Line**: `mean >= 0.75`
- **Lý do Kỹ thuật**: Đo lường chất lượng câu trả lời từ AI (độ chính xác RAG, hallucination check hoặc user feedback) để đảm bảo mô hình không chỉ "chạy được" mà còn trả về nội dung có giá trị.

---

## 4. Quy trình Điều tra 3 Tầng Observability (Triad Workflow)

Khi xảy ra sự cố (Incident), quy trình điều tra tiêu chuẩn được thực hiện qua 3 bước:

```
[1. Metrics Dashboard] ---> [2. Traces Waterfall] ---> [3. Structured JSON Logs]
   Phát hiện bất thường        Định vị Span bị chậm/lỗi       Xem bằng chứng Root Cause (Redacted PII)
```

1. **Metrics Dashboard**: Quan sát panel bị vượt ngưỡng (Ví dụ: `latency` P95 > 3000ms hoặc `errors` > 2%).
2. **Langfuse Traces**: Mở waterfall trace tìm span cụ thể bị chậm (Step Retrieval RAG hay Step LLM Call).
3. **JSON Logs**: Lọc log theo `correlation_id` từ `data/logs.jsonl` để lấy bằng chứng root cause chi tiết.

---

## 5. Quy trình Kiểm tra & Nghiệm thu

1. **Kiểm tra Validator**:
   ```bash
   python scripts/validate_dashboard.py
   ```
   *Yêu cầu đầu ra*: `HỢP LỆ: 6/6 panel có trong dashboard contract.`

2. **Yêu cầu Bằng chứng Runtime (Evidence)**:
   - Chụp ảnh màn hình dashboard hiển thị rõ tên panel, khung thời gian (60m) và các threshold / SLO line.
   - Bàn giao ảnh cho Thành viên E để đóng gói báo cáo nộp bài trong `submission/evidence/`.

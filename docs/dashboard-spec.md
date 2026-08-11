# Chi tiết Quy cách Dashboard & Tiêu chuẩn AI Observability (Dashboard Specification)

Tài liệu này quy định chi tiết 6 nhóm panel cho **Day 13 AI Observability Dashboard**, tuân thủ theo tiêu chuẩn **Google SRE Golden Signals**, **OpenTelemetry GenAI Semantic Conventions** và **Datadog / Langfuse Observability Framework**.

Contract chuẩn được lưu tại [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml) và hướng dẫn thiết lập runtime tại [`docs/DASHBOARD_SETUP.md`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/docs/DASHBOARD_SETUP.md).

---

## 1. So sánh 4 Golden Signals Truyền thống vs. 6 GenAI Golden Signals

| Chỉ số | SRE Truyền thống (SOA / Web) | LLM Observability Extension (GenAI) | Rủi ro Kỹ thuật / Kinh tế khi bỏ qua |
| :--- | :--- | :--- | :--- |
| **Latency** | Phản ánh CPU/DB/RAM. Dùng Average hoặc P95. | Dùng phân vị P95/P99. Bắt buộc đo Time to First Token (TTFT) & Generation Time. | Khách hàng bị nghẽn do long-tail latency của thuật toán sinh token. |
| **Traffic** | Thống kê số lượng Request/sec (QPS). | Thống kê Requests Per Minute (RPM) & Số lượng Agent Runs. | Bị che giấu các cuộc tấn công nhồi prompt hoặc vòng lặp vô tận (Loop bug). |
| **Errors** | Đếm lỗi HTTP 5xx / 4xx từ Server. | Phân loại lỗi Kỹ thuật (5xx/429) & Lỗi Nghiệp vụ AI (Timeout/Schema Fail). | Bỏ sót các request trả về HTTP 200 OK nhưng bị rỗng hoặc rò rỉ lỗi. |
| **Cost (Mới)** | Chi phí phần cứng cố định (hàng tháng). | Chi phí phi tuyến tính tính theo từng Token ($/1k tokens). | Bùng nổ chi phí tài khoản API chỉ trong vài phút (Runaway spend). |
| **Tokens (Mới)**| Không tồn tại trong Web 2.0. | Phân tách Input Tokens (Prompt) vs Output Tokens (Completion). | Tràn bộ nhớ Context Window (Lost in the Middle) & nghẽn GPU Decode phase. |
| **Quality (Mới)**| Giám sát Uptime (99.9% availability). | Phanh An toàn (Quality Proxy / LLM-as-a-judge score 0.0 - 1.0). | Mô hình AI trả về câu trả lời sai lệch (Hallucination) dù server vẫn 200 OK. |

---

## 2. Bảng Ánh xạ Tiêu chuẩn OpenTelemetry GenAI Semantic Conventions

| Panel ID | Tên Panel (Dashboard) | OTel Metric Standard | Event Nguồn | Field Log Nguồn | Đơn vị | Ngưỡng SLO Target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `latency` | Latency percentiles | `gen_ai.client.operation.duration` | `response_sent` | `latency_ms` | `ms` | $P95 \le 3000\text{ ms}$ |
| `traffic` | Request traffic | `http.server.request.count` / RPM | `request_received` | `event` | `RPM` | $\text{Rate} \ge 1\text{ rpm}$ |
| `errors` | Error rate and breakdown | `gen_ai.client.error_rate` | `request_failed` | `error_type` | `%` | $\text{Error Rate} \le 2\%$ |
| `cost` | Cost over time | `gen_ai.usage.cost` | `response_sent` | `cost_usd` | `USD` | $\text{Total Cost} \le \$2.5$ |
| `tokens` | Input and output tokens | `gen_ai.usage.input_tokens` & `output_tokens` | `response_sent` | `tokens_in`, `tokens_out` | `tokens` | $\text{Tokens} \le 50000$ |
| `quality` | Quality proxy | `gen_ai.quality.score` | `response_sent` | `quality_score` | `score` | $\text{Mean} \ge 0.75$ |

---

## 3. Cấu hình Chi tiết 6 Panel Dashboard (Dashboard Contract Specification)

### 3.1. Latency Percentiles (`latency`)
- **Query / Formula**: `event == "response_sent" | percentile(latency_ms, [50, 95, 99])`
- **Lý do SRE**: Loại bỏ sai lệch của độ trễ trung bình. Phân vị P95 đảm bảo 95% khách hàng đạt trải nghiệm mượt mà dưới 3000ms.

### 3.2. Request Traffic (`traffic`)
- **Query / Formula**: `event == "request_received" | count() by 1m`
- **Lý do SRE**: Giám sát biến động lưu lượng thực tế (RPM) để phát hiện sự cố Outage (Drop) hoặc DDoS/Loop (Spike).

### 3.3. Error Rate & Breakdown (`errors`)
- **Query / Formula**: `count(event == "request_failed") / count(event == "request_received") * 100; count_by(error_type)`
- **Công thức Zero-Safe**:
  $$ErrorRate_{pct} = \begin{cases} \left(\frac{\sum ERRORS}{\text{TRAFFIC} + \sum ERRORS}\right) \times 100 & \text{nếu } (\text{TRAFFIC} + \sum ERRORS) > 0 \\ 0.0 & \text{nếu } (\text{TRAFFIC} + \sum ERRORS) = 0 \end{cases}$$
- **Lý do SRE**: Đảm bảo không bị lỗi chia cho 0 khi khởi tạo và gom đủ cả System Errors lẫn Model/API Errors.

### 3.4. Cost Over Time (`cost`)
- **Query / Formula**: `event == "response_sent" | sum(cost_usd) by 1m; sum(cost_usd)`
- **Lý do SRE**: Kiểm soát tổng chi phí tài khoản LLM API trong cửa sổ 60 phút, ngăn ngừa rủi ro tài chính phi tuyến tính.

### 3.5. Input & Output Tokens (`tokens`)

| Pha xử lý Token | Tên Field | Thuật toán GPU / Đặc tính | Chi phí Relative | Tác động Latency |
| :--- | :--- | :--- | :--- | :--- |
| **Prefill Phase (Prompt)** | `tokens_in` | Song song (*Parallel Compute*) | Rẻ hơn ($1\times$) | Tăng nhẹ thời gian TTFT |
| **Decode Phase (Completion)**| `tokens_out` | Tự đẳng hồi (*Autoregressive Sequential*) | Đắt hơn ($3\times - 4\times$) | Tỷ lệ thuận trực tiếp với Latency sinh từ |

- **Query / Formula**: `event == "response_sent" | sum(tokens_in), sum(tokens_out)`

### 3.6. Quality Proxy (`quality`)
- **Query / Formula**: `event == "response_sent" | mean(quality_score)`
- **Lý do SRE**: Đóng vai trò phanh an toàn (*Safety Guardrail*). Nếu chất lượng câu trả lời rơi xuống dưới 0.75, hệ thống sẽ cảnh báo sự thoái hóa của mô hình ngay cả khi HTTP status vẫn 200 OK.

---

## 4. Quy trình Điều tra Sự cố 3 Tầng Observability (Triad Workflow Matrix)

| Tầng Observability | Công cụ / Nguồn dữ liệu | Tác vụ trong OODA Loop | Hành động tiêu chuẩn của SRE |
| :--- | :--- | :--- | :--- |
| **Tầng 1: Metrics** | Dashboard 6 Panel (`data/logs.jsonl`) | **Phát hiện (Observe)** | Phát hiện chỉ số vọt ngưỡng SLO (VD: Latency P95 > 3000ms). |
| **Tầng 2: Traces** | Langfuse Waterfall UI | **Định vị (Orient & Decide)** | Mở trace tương ứng, xác định Step bị chậm (`retrieve` RAG hay `generate` LLM). |
| **Tầng 3: Logs** | Structured JSON Logs (`correlation_id`) | **Bằng chứng (Act)** | Trích xuất log chi tiết (đã redact PII) để xác nhận nguyên nhân gốc rễ (Root Cause). |

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

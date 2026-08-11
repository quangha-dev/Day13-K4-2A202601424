# Chi tiết Quy cách Dashboard & Tiêu chuẩn AI Observability (Dashboard Specification)

Tài liệu này quy định chi tiết cấu trúc Dashboard cho **Day 13 AI Observability Dashboard**, tuân thủ theo tiêu chuẩn **Google SRE Golden Signals**, **OpenTelemetry GenAI Semantic Conventions**, **Datadog LLM Observability** và **Langfuse Observability Framework**.

Contract chuẩn đáp ứng tự động hóa nằm tại [`config/dashboard.yaml`](../config/dashboard.yaml) và hướng dẫn thiết lập runtime tại [`docs/DASHBOARD_SETUP.md`](DASHBOARD_SETUP.md).

---

## 1. Cơ sở Kỹ thuật & Khung Kiến trúc Observability

### 1.1. 4 Trụ cột AI Observability (4 Pillars of AI Observability)

Một hệ thống AI Agent / LLM sản xuất quy mô lớn cần được quản trị toàn diện qua **4 Trụ cột cốt lõi**:

```
+-----------------------------------------------------------------------------------+
|                           4 PILLARS OF AI OBSERVABILITY                           |
+-------------------+-------------------+-------------------+-----------------------+
|  1. PERFORMANCE   |      2. COST      |    3. QUALITY     |    4. RELIABILITY     |
| Latency P50/95/99 | Tokens/req (in/out| Hallucination /   | Error rate & Uptime   |
| TTFT (Streaming)  | Cost/req/task     | Faithfulness      | Tool-call success rate|
| Throughput (tok/s)| Cost/user/feature | Task completion   | Retry rate, Loop rate |
| LLM call duration | Cache hit rate    | Thumbs UP/DOWN    | Retrieval recall      |
+-------------------+-------------------+-------------------+-----------------------+
```

### 1.2. Mở rộng Google SRE 4 Golden Signals thành 6 Signals cho AI Agent

Hệ thống SRE truyền thống (Google SRE Book) định nghĩa **4 Golden Signals**: Latency, Traffic, Errors, Saturation. 
Đối với ứng dụng **AI Agent / GenAI**, hệ thống bổ sung thêm 2 tín hiệu đặc thù bắt buộc: **Cost** và **Quality**.

```
AI Agent Golden Signals = Latency + Traffic + Errors + Saturation + Cost + Quality
```

---

## 2. Kiến trúc Dashboard 3 Layer cho Stakeholders (3-Layer Architecture)

Nhằm tối ưu hóa khả năng quan sát cho các đối tượng sử dụng khác nhau, Dashboard được phân tách theo **Nguyên tắc Phân quyền Stakeholder (Stakeholder Isolation Principle)**: *Mỗi stakeholder chỉ cần nhìn đúng 1 layer phù hợp với nhu cầu quyết định.*

```
+-----------------------------------------------------------------------------------+
| LAYER 1: OVERVIEW DASHBOARD (Cho Leadership / C-Suite)                            |
| Target: Health, Uptime, Total Spend, High-level Quality/CSAT, Key Active Alerts   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| LAYER 2: DETAIL DASHBOARD (Cho Engineering & DevOps / SRE)                        |
| Target: 6 Core Golden Signals + Tier-2 Performance, Cost by Feature, Token splits |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| LAYER 3: DRILL-DOWN DASHBOARD (Cho Incident Responders & Debugging)               |
| Target: Langfuse Traces Waterfall, Span Duration, Log Search via Correlation ID   |
+-----------------------------------------------------------------------------------+
```

* **Layer 1 (Overview - Leadership)**: Tập trung vào chỉ số sức khỏe tổng thể và tài chính. Leadership không cần xem raw trace hay log chi tiết.
* **Layer 2 (Detail - Engineering)**: Tập trung vào hiệu năng hệ thống, tỷ lệ lỗi, đếm token và rủi ro SLO.
* **Layer 3 (Drill-down - Debugging)**: Tập trung vào việc truy vết sự cố, xem waterfall trace và tìm nguyên nhân gốc rễ (Root Cause Analysis).

---

## 3. Tier 1: 6 Panel Cốt lõi (Core Dashboard Contract)

Được định nghĩa trong [`config/dashboard.yaml`](../config/dashboard.yaml) đảm bảo pass `python scripts/validate_dashboard.py` (báo `6/6 panel`).

### 3.1. Latency Percentiles (`latency`)
- **Title**: Latency percentiles
- **OpenTelemetry Metric**: `gen_ai.client.operation.duration`
- **Pillar**: Performance
- **Event nguồn**: `response_sent` | **Field nguồn**: `latency_ms`
- **Aggregations**: `p50`, `p95`, `p99`
- **Query / Formula**: `event == "response_sent" | percentile(latency_ms, [50, 95, 99])`
- **Đơn vị**: `ms` (milliseconds) | **Threshold / SLO Line**: `p95 <= 3000 ms`
- **Phân tích Chuyên sâu SRE**: Độ trễ sinh từ có hiện tượng "long-tail latency" đặc thù. Đo lường phân vị P95 và P99 giúp phát hiện chính xác các câu truy vấn bị nghẽn (do nhồi context quá dài hoặc RAG retrieval chậm) mà không bị san bằng bởi các giá trị trung bình (Average).

### 3.2. Request Traffic (`traffic`)
- **Title**: Request traffic
- **OpenTelemetry Metric**: `http.server.request.count` / RPM
- **Pillar**: Reliability & Performance
- **Event nguồn**: `request_received` | **Field nguồn**: `event`
- **Aggregations**: `count`, `rate_per_minute`
- **Query / Formula**: `event == "request_received" | count() by 1m`
- **Đơn vị**: `requests_per_minute` (RPM) | **Threshold / SLO Line**: `rate_per_minute >= 1`
- **Phân tích Chuyên sâu SRE**: Giám sát lưu lượng thực tế để phát hiện sớm hiện tượng sụt giảm lưu lượng (Outage / đứt kết nối mạng) hoặc tăng vọt bất thường do vòng lặp truy vấn vô hạn (*runaway loops*) hoặc tấn công DDoS.

### 3.3. Error Rate & Breakdown (`errors`)
- **Title**: Error rate and breakdown
- **OpenTelemetry Metric**: `gen_ai.client.error_rate`
- **Pillar**: Reliability
- **Event nguồn**: `request_received`, `request_failed` | **Field nguồn**: `error_type`
- **Aggregations**: `error_rate_pct`, `count_by_value`
- **Query / Formula**: `count(event == "request_failed") / count(event == "request_received") * 100; count_by(error_type)`
- **Đơn vị**: `percent` (`%`) | **Threshold / SLO Line**: `error_rate_pct <= 2 %`
- **Phân tích Chuyên sâu SRE**: Sử dụng công thức Zero-Safe:
  $$\text{error\_rate\_pct} = \begin{cases} \left(\frac{\text{Total Errors}}{\text{TRAFFIC} + \text{Total Errors}}\right) \times 100 & \text{nếu Total Requests} > 0 \\ 0.0 & \text{nếu Total Requests} = 0 \end{cases}$$
  Giúp hợp nhất và phân loại chính xác giữa lỗi hạ tầng (HTTP 500, Network Timeout) và lỗi ứng dụng AI (Rate Limit 429 API, Context Length Exceeded 400).

### 3.4. Cost Over Time (`cost`)
- **Title**: Cost over time
- **OpenTelemetry Metric**: `gen_ai.usage.cost`
- **Pillar**: Cost
- **Event nguồn**: `response_sent` | **Field nguồn**: `cost_usd`
- **Aggregations**: `sum_by_minute`, `total`
- **Query / Formula**: `event == "response_sent" | sum(cost_usd) by 1m; sum(cost_usd)`
- **Đơn vị**: `usd` (`$`) | **Threshold / SLO Line**: `total <= 2.5 USD`
- **Phân tích Chuyên sâu SRE**: Ứng dụng GenAI có mô hình chi phí phi tuyến tính dựa trên lượng token gửi/nhận. Việc giám sát tổng ngân sách chi trả cho LLM API trong cửa sổ 60 phút giúp ngăn ngừa rủi ro bùng nổ tài chính ngoài dự kiến.

### 3.5. Input & Output Tokens (`tokens`)
- **Title**: Input and output tokens
- **OpenTelemetry Metric**: `gen_ai.usage.input_tokens` & `gen_ai.usage.output_tokens`
- **Pillar**: Cost & Performance
- **Event nguồn**: `response_sent` | **Field nguồn**: `tokens_in`, `tokens_out`
- **Aggregations**: `sum_by_field`
- **Query / Formula**: `event == "response_sent" | sum(tokens_in), sum(tokens_out)`
- **Đơn vị**: `tokens` | **Threshold / SLO Line**: `sum_by_field <= 50000 tokens`
- **Phân tích Chuyên sâu SRE**: Phân tách rõ ràng giữa Input Tokens (Prompt/Context) và Output Tokens (Completion). Output Tokens tiêu tốn nhiều thời gian xử lý GPU hơn và có đơn giá đắt hơn gấp 3-4 lần so với Input Tokens.

### 3.6. Quality Proxy (`quality`)
- **Title**: Quality proxy
- **OpenTelemetry Metric**: `gen_ai.quality.score`
- **Pillar**: Quality
- **Event nguồn**: `response_sent` | **Field nguồn**: `quality_score`
- **Aggregations**: `mean`
- **Query / Formula**: `event == "response_sent" | mean(quality_score)`
- **Đơn vị**: `score_0_to_1` (Thang điểm 0.0 đến 1.0) | **Threshold / SLO Line**: `mean >= 0.75`
- **Phân tích Chuyên sâu SRE**: Đo lường chất lượng nội dung sinh ra (RAG relevance, hallucination score hay user feedback) để đảm bảo mô hình không chỉ "hoạt động được" (200 OK) mà còn cung cấp thông tin chính xác.

---

## 4. Tier 2: 6 Panel Nâng cao cho Hệ thống GenAI Enterprise (Extended Observability)

### 4.1. Time to First Token - TTFT (`time_to_first_token`)
- **Title**: Time to first token (TTFT)
- **Pillar**: Performance | **OpenTelemetry Metric**: `gen_ai.client.time_to_first_token`
- **Event nguồn**: `response_sent` / `streaming_chunk` | **Field nguồn**: `ttft_ms`
- **Aggregations**: `p50`, `p95`, `p99` | **Threshold / SLO Line**: `p95 <= 800 ms`
- **Phân tích Chuyên sâu SRE**: TTFT đo thời gian từ lúc gửi prompt tới khi chữ đầu tiên hiện ra trên màn hình. Trong kiến trúc Streaming LLM, TTFT mới là yếu tố quyết định độ nhạy cảm nhận (*Perceived Speed*) của người dùng thay vì tổng độ trễ end-to-end.

### 4.2. RAG Vector Retrieval Latency (`rag_retrieval_latency`)
- **Title**: RAG vector retrieval latency
- **Pillar**: Performance & Reliability | **OpenTelemetry Metric**: `db.client.operation.duration` (Vector DB)
- **Event nguồn**: `rag_search_completed` | **Field nguồn**: `retrieval_latency_ms`
- **Aggregations**: `p50`, `p95`, `mean` | **Threshold / SLO Line**: `p95 <= 300 ms`
- **Phân tích Chuyên sâu SRE**: Cô lập hoàn toàn độ trễ của bước tìm kiếm tri thức trong Vector Database (Pinecone, Chroma, Qdrant) khỏi độ trễ sinh từ của LLM. Giúp định vị ngay điểm nghẽn nằm ở hạ tầng Vector DB hay ở LLM API.

### 4.3. Cost Attribution per Feature / User (`cost_attribution`)
- **Title**: Cost attribution by feature / user
- **Pillar**: Cost | **OpenTelemetry Metric**: `gen_ai.usage.cost` (grouped by `feature` or `user_id_hash`)
- **Event nguồn**: `response_sent` | **Field nguồn**: `cost_usd`, `feature`, `user_id_hash`
- **Aggregations**: `sum_by_group` | **Threshold / SLO Line**: `cost_per_feature <= 1.5 USD`
- **Phân tích Chuyên sâu SRE**: Phân bổ và theo dõi chi phí theo từng tính năng (`chat`, `monitoring`, `rag_agent`) hoặc từng nhóm tài khoản. Giúp nhận diện chính xác tính năng nào đang tiêu tốn ngân sách vô lý hoặc tài khoản bị lạm dụng API.

### 4.4. Token Generation Speed (`token_generation_speed`)
- **Title**: Token generation speed
- **Pillar**: Performance | **OpenTelemetry Metric**: `gen_ai.client.token_rate`
- **Event nguồn**: `response_sent` | **Field nguồn**: `tokens_out`, `generation_time_ms`
- **Aggregations**: `mean_rate`, `min_rate` | **Threshold / SLO Line**: `mean_rate >= 25 tokens/sec`
- **Phân tích Chuyên sâu SRE**: Giám sát tốc độ nhè từ (Generation throughput) của GPU / LLM Inference Server. Nếu chỉ số này sụt giảm sâu, báo hiệu cụm Server Inference đang bị nghẽn GPU vRAM hoặc bị hụt băng thông.

### 4.5. Faithfulness & Grounding Score (`faithfulness_score`)
- **Title**: Faithfulness grounding score
- **Pillar**: Quality | **OpenTelemetry Metric**: `gen_ai.eval.faithfulness`
- **Event nguồn**: `response_sent` / `evaluation_completed` | **Field nguồn**: `faithfulness_score`
- **Aggregations**: `mean`, `p10` | **Threshold / SLO Line**: `mean >= 0.85`
- **Phân tích Chuyên sâu SRE**: Sử dụng cơ chế LLM-as-a-Judge đánh giá xem câu trả lời có được trích dẫn trung thực từ ngữ cảnh RAG hay không. Giúp ngăn chặn hiện tượng Hallucination (AI "bốc phét" thông tin không tồn tại trong tài liệu).

### 4.6. Prompt Token Ratio - Input/Output Ratio (`token_ratio`)
- **Title**: Input to output token ratio
- **Pillar**: Cost & Performance | **OpenTelemetry Metric**: `gen_ai.usage.input_tokens / gen_ai.usage.output_tokens`
- **Event nguồn**: `response_sent` | **Field nguồn**: `tokens_in`, `tokens_out`
- **Aggregations**: `ratio_mean` | **Threshold / SLO Line**: `ratio_mean <= 10.0`
- **Phân tích Chuyên sâu SRE**: Phát hiện bất cân bằng giữa prompt và response. Tỷ lệ quá cao ($\ge 10$) cảnh báo hiện tượng "Context Bloating" (nhồi prompt quá lớn nhưng trả lời quá ngắn); tỷ lệ quá thấp ($\le 0.1$) cảnh báo hiện tượng "Runaway Output" (LLM lặp từ vô tận).

---

## 5. Quy trình Điều tra 3 Tầng Observability (Triad Workflow)

Khi xảy ra sự cố (Incident), quy trình điều tra tiêu chuẩn được thực hiện qua 3 bước:

```
[Layer 1/2 Metrics Dashboard] ---> [Layer 3 Langfuse Traces] ---> [Structured JSON Logs]
     Phát hiện bất thường              Định vị Span bị chậm/lỗi        Xem bằng chứng Root Cause (Redacted PII)
```

1. **Metrics Dashboard (Layer 1 & 2)**: Quan sát panel bị vượt ngưỡng (Ví dụ: `latency` P95 > 3000ms hoặc `errors` > 2%).
2. **Langfuse Traces (Layer 3)**: Mở waterfall trace tìm span cụ thể bị chậm (Step Retrieval RAG hay Step LLM Call).
3. **JSON Logs (Layer 3)**: Lọc log theo `correlation_id` từ `data/logs.jsonl` để lấy bằng chứng root cause chi tiết.

---

## 6. Quy trình Kiểm tra & Nghiệm thu

1. **Kiểm tra Validator**:
   ```bash
   python scripts/validate_dashboard.py
   ```
   *Yêu cầu đầu ra*: `HỢP LỆ: 6/6 panel có trong dashboard contract.`

2. **Yêu cầu Bằng chứng Runtime (Evidence)**:
   - Chụp ảnh màn hình dashboard hiển thị rõ tên panel, khung thời gian (60m) và các threshold / SLO line.
   - Bàn giao ảnh cho Thành viên E để đóng gói báo cáo nộp bài trong `submission/evidence/`.

# Chi tiết Quy cách Dashboard & Tiêu chuẩn AI Observability (Dashboard Specification)

Tài liệu này quy định chi tiết cấu trúc Dashboard cho **Day 13 AI Observability Dashboard**, tuân thủ theo tiêu chuẩn **Google SRE Golden Signals**, **OpenTelemetry GenAI Semantic Conventions** và **Datadog / Langfuse Observability Framework**.

Contract chuẩn đáp ứng tự động hóa nằm tại [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml) và hướng dẫn thiết lập runtime tại [`docs/DASHBOARD_SETUP.md`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/docs/DASHBOARD_SETUP.md).

---

## 1. Cơ sở Kỹ thuật: Mở rộng SRE Golden Signals cho GenAI

Hệ thống SRE truyền thống (Google SRE Book) định nghĩa **4 Golden Signals**: Latency, Traffic, Errors, Saturation. 
Đối với ứng dụng **GenAI / LLM**, hệ thống mở rộng thành **6 Core GenAI Golden Signals** ở Tier-1 (bắt buộc) và các **Advanced Signals** ở Tier-2 (nâng cao).

```
GenAI Observability Core = Latency + Traffic + Errors + Cost + Tokens + Quality Proxy
```

---

## 2. Tier 1: 6 Panel Cốt lõi (Core Dashboard Contract)

Được định nghĩa trong [`config/dashboard.yaml`](file:///d:/VSC/VinAI_ThucChien/Lab/Day13-K4-2A202601424/config/dashboard.yaml) đảm bảo pass `python scripts/validate_dashboard.py` (báo `6/6 panel`).

| Panel ID | Tên Panel (Dashboard) | OpenTelemetry GenAI Metric Standard | Event & Field Nguồn | Đơn vị & Ngưỡng SLO |
| :--- | :--- | :--- | :--- | :--- |
| `latency` | Latency percentiles | `gen_ai.client.operation.duration` | `response_sent` -> `latency_ms` | `ms` (`P95 <= 3000 ms`) |
| `traffic` | Request traffic | `http.server.request.count` / RPM | `request_received` -> `event` | `RPM` (`rate >= 1 rpm`) |
| `errors` | Error rate and breakdown | `gen_ai.client.error_rate` | `request_failed` -> `error_type` | `%` (`error_rate <= 2 %`) |
| `cost` | Cost over time | `gen_ai.usage.cost` | `response_sent` -> `cost_usd` | `USD` (`total <= $2.5`) |
| `tokens` | Input and output tokens | `gen_ai.usage.input_tokens` & `output_tokens` | `response_sent` -> `tokens_in`, `tokens_out` | `tokens` (`total <= 50000`) |
| `quality` | Quality proxy | `gen_ai.quality.score` | `response_sent` -> `quality_score` | `score` (`mean >= 0.75`) |

---

## 3. Tier 2: 6 Panel Nâng cao cho Hệ thống GenAI Enterprise (Extended Observability)

Trong các hệ thống AI sản xuất quy mô lớn (Production Enterprise), bên cạnh 6 panel cơ bản, kiến trúc sư hệ thống thường bổ sung **6 Panel Nâng cao (Tier 2)** để tối ưu hóa sâu hiệu năng và chi phí:

### 3.1. Time to First Token - TTFT (`time_to_first_token`)
- **Metric OTel**: `gen_ai.client.time_to_first_token`
- **Mô tả**: Độ trễ từ khi phát request đến khi nhận được token đầu tiên trên màn hình.
- **Ý nghĩa Kỹ thuật**: Đây là thước đo trực tiếp quyết định trải nghiệm phản hồi nhanh (*Perceived Latency*) của người dùng trong các giao diện Streaming Chat.
- **Ngưỡng khuyến nghị**: $TTFT_{P95} \le 800\text{ ms}$.

### 3.2. RAG Vector Retrieval Latency (`rag_retrieval_latency`)
- **Metric OTel**: `db.client.operation.duration` (Vector DB)
- **Mô tả**: Thời gian thực hiện tìm kiếm ngữ cảnh liên quan trong Vector Database (Pinecone, Chroma, Qdrant).
- **Ý nghĩa Kỹ thuật**: Phân tách độ trễ của bước RAG Search khỏi bước LLM Generation để định vị đúng điểm nghẽn.
- **Ngưỡng khuyến nghị**: $P95 \le 300\text{ ms}$.

### 3.3. Cost Attribution per Feature / User (`cost_attribution`)
- **Metric OTel**: `gen_ai.usage.cost` grouped by `feature` or `user_id_hash`
- **Mô tả**: Phân bổ chi phí tiêu tốn theo từng tính năng (`chat`, `monitoring`, `rag_agent`) hoặc từng user.
- **Ý nghĩa Kỹ thuật**: Giúp phát hiện tính năng nào đang "ngốn" nhiều tiền nhất hoặc phát hiện các tài khoản user lạm dụng hệ thống.

### 3.4. Token Generation Speed (`token_generation_speed`)
- **Metric OTel**: `gen_ai.client.token_rate` (tokens/sec)
- **Mô tả**: Tốc độ sinh ra từ của mô hình (Số token đầu ra trên mỗi giây).
- **Ý nghĩa Kỹ thuật**: Giám sát hiệu năng của cụm GPU/Inference Server. Nếu chỉ số này sụt giảm, chứng tỏ cụm inference đang bị bão hòa tài nguyên.
- **Ngưỡng khuyến nghị**: $\ge 25\text{ tokens/sec}$.

### 3.5. Faithfulness & Grounding Score (`faithfulness_score`)
- **Metric OTel**: `gen_ai.eval.faithfulness`
- **Mô tả**: Điểm số LLM-as-a-Judge đánh giá độ trung thực của câu trả lời so với tài liệu RAG đã trích xuất.
- **Ý nghĩa Kỹ thuật**: Bắt kịp các trường hợp Hallucination (AI "bốc phét" thông tin không có trong tài liệu).
- **Ngưỡng khuyến nghị**: $\ge 0.85$.

### 3.6. Prompt Token Ratio - Input/Output Ratio (`token_ratio`)
- **Metric OTel**: `gen_ai.usage.input_tokens / gen_ai.usage.output_tokens`
- **Mô tả**: Tỷ lệ giữa Token đầu vào (Prompt/Context) và Token đầu ra (Completion).
- **Ý nghĩa Kỹ thuật**: Phát hiện hiện tượng "Context Bloating" (Prompt quá dài nhưng trả lời ngắn) hoặc hiện tượng "Runaway Output" (LLM bị lặp từ vô tận).

---

## 4. Mô hình Dashboard Tổng thể Enterprise (Full Dashboard Architecture)

```
+-----------------------------------------------------------------------------------+
|                        TIER 1: CORE GOLDEN SIGNALS (6 PANELS)                     |
|  [1. Latency P95]   [2. Traffic RPM]   [3. Error Rate]   [4. Total Cost]          |
|  [5. Token Usage]   [6. Quality Proxy]                                            |
+-----------------------------------------------------------------------------------+
|                   TIER 2: ADVANCED ENTERPRISE EXTENSIONS (6 PANELS)               |
|  [7. TTFT Streaming] [8. RAG Search Latency] [9. Cost by Feature/User]            |
|  [10. Generation Speed] [11. Faithfulness Score] [12. Input/Output Token Ratio]   |
+-----------------------------------------------------------------------------------+
```

---

## 5. Quy trình Điều tra 3 Tầng Observability (Triad Workflow)

Khi xảy ra sự cố (Incident), quy trình điều tra tiêu chuẩn được thực hiện qua 3 bước:

```
[1. Metrics Dashboard] ---> [2. Traces Waterfall] ---> [3. Structured JSON Logs]
   Phát hiện bất thường        Định vị Span bị chậm/lỗi       Xem bằng chứng Root Cause (Redacted PII)
```

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

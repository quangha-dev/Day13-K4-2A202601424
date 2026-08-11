# Điều tra CP3 — day13-k4-observability-v1

## 1. Metrics — phát hiện triệu chứng

- Baseline P95: **152 ms**.
- Khi bật challenge `rag_slow`: P95 tăng lên **2652 ms**, vượt threshold challenge **2000 ms** khoảng 32.6%.
- Error rate vẫn 0%, cost và quality gần như không đổi. Sự cố thuộc nhóm latency, không phải lỗi HTTP hay cost spike.
- Evidence: `cp3-metrics-baseline.json`, `cp3-metrics-incident.json`, `cp3-metrics-incident.png`.

## 2. Traces/component timing — khoanh vùng

- Code đã gắn `@observe(as_type="span")` cho `retrieve` và `generate`.
- Phép đo runtime cùng scenario cho thấy `retrieve=2512.5 ms`, `generate=150.7 ms`; retrieval chiếm khoảng **94.3%** tổng thời gian hai component.
- Waterfall/trace ID Langfuse chưa thể lấy vì máy tích hợp chưa có key và trình duyệt dừng ở trang đăng nhập. Không tạo trace ID giả.
- Evidence tạm thời có thể kiểm chứng: `cp3-component-timing.json`. Evidence Langfuse bắt buộc vẫn phải bổ sung sau khi cấu hình key thật.

## 3. Logs — chứng minh request bị ảnh hưởng

- Control log xác nhận `incident_enabled` với payload `rag_slow` lúc `2026-08-11T09:19:15.326710Z`.
- Request `req-939a54c9`, feature `monitoring`, session `k4-challenge-s05` có `response_sent.latency_ms=2651`.
- Bốn request challenge còn lại đều có latency nội bộ 2651–2652 ms.
- Evidence: `cp3-correlated-log.json`, `cp3-load-test.txt`.

## 4. Root cause và yếu tố khuếch đại

- **Root cause:** scenario `rag_slow` thêm khoảng 2.5 giây trong RAG retrieval (`app/mock_rag.py`), đúng với component timing và mức tăng P95.
- **Yếu tố khuếch đại:** `agent.run()` là hàm đồng bộ nhưng được gọi trực tiếp trong async endpoint. Khi concurrency=5, event loop xử lý phần blocking lần lượt nên client tail latency đạt 8–13 giây dù log nội bộ mỗi request khoảng 2.65 giây.

## 5. Fix và phòng ngừa

- Mitigation: tắt incident/dependency route chậm, bật cache hoặc fallback retrieval.
- Fix production: timeout + circuit breaker cho vector store; chuyển tác vụ blocking sang worker/thread pool phù hợp.
- Preventive: span riêng cho retrieval/generation; alert theo P95 và feature; load test concurrency trong CI; theo dõi chênh lệch client latency và internal latency.

## 6. Recovery

- Sau khi disable incident và restart process để reset metrics, chạy lại đúng 5 query challenge.
- P95 hồi phục từ 2652 ms về **151 ms**, error rate vẫn 0%.
- Evidence: `cp3-metrics-recovery.json`.

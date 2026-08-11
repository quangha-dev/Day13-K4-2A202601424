# Điều tra CP3 — day13-k4-observability-v1

## 1. Metrics — phát hiện triệu chứng

- Baseline P95: **152 ms**.
- Khi bật challenge `rag_slow`: P95 tăng lên **3626 ms**, vượt threshold challenge **2000 ms** khoảng 81.3%.
- Error rate vẫn 0%, cost và quality gần như không đổi. Sự cố thuộc nhóm latency, không phải lỗi HTTP hay cost spike.
- Evidence: `cp3-metrics-baseline.json`, `cp3-metrics-incident.json`, `cp3-metrics-incident.png`.

## 2. Traces/component timing — khoanh vùng

- Code đã gắn `@observe(as_type="span")` cho `retrieve` và `generate`.
- Phép đo runtime cùng scenario cho thấy `retrieve=2512.5 ms`, `generate=150.7 ms`; retrieval chiếm khoảng **94.3%** tổng thời gian hai component.
- Waterfall Langfuse thật của trace `61a5c25ea8a6d57fce2a3c4ea16489df` cho thấy `run=3628 ms`, `retrieve=2501 ms`, `generate=151 ms`, correlation ID `req-49c5faf5`.
- Evidence: `cp3-component-timing.json`, `cp3-trace-summary.json`, `cp3-trace-waterfall.jpg`.

## 3. Logs — chứng minh request bị ảnh hưởng

- Control log xác nhận `incident_enabled` với payload `rag_slow` lúc `2026-08-11T10:25:48.148542Z`.
- Request `req-49c5faf5`, feature `monitoring`, session `k4-challenge-s02` có `response_sent.latency_ms=3626` và khớp metadata trace Langfuse.
- Bốn request challenge còn lại có latency nội bộ 2652–2657 ms; request được chọn có cold fetch managed prompt nên đạt 3626 ms và trở thành P95.
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
- Sau restart có tracing, P50 hồi phục về **152 ms**; P95 là **1127 ms** do lần tải managed prompt đầu tiên nhưng vẫn thấp hơn SLO 3000 ms. Error rate vẫn 0%.
- Evidence: `cp3-metrics-recovery.json`.

# Kế hoạch hoàn thiện Lab 13 cho nhóm 5 thành viên

## 1. Mục tiêu chung và Definition of Done

Nhóm hoàn thành bài khi đồng thời đạt tất cả điều kiện sau:

- API chạy được; `data/logs.jsonl` có ít nhất 10 bản ghi JSON hợp lệ.
- Mỗi request có correlation ID xuyên suốt middleware, response, log và metadata trace.
- Log API có `user_id_hash`, `session_id`, `feature`, `model`, `env`; không còn PII thô.
- `python scripts/validate_logs.py` đạt mục tiêu cuối 100/100 (CP1 tối thiểu 80/100).
- `python -m pytest -q` pass toàn bộ public tests.
- Langfuse có ít nhất 10 traces, một waterfall đầy đủ, prompt v1/v2 và evidence đổi label/rollback.
- Dashboard có đúng 6 nhóm chỉ số, `python scripts/validate_dashboard.py` báo `6/6 panel`.
- SLO, 3 alert rules và 3 runbook hoàn chỉnh, nhất quán về ngưỡng và owner.
- CP3 được điều tra theo đúng luồng Metrics → Traces → Logs, có trace ID/correlation ID cụ thể.
- `submission/REPORT.md` đầy đủ, evidence dùng đường dẫn tương đối, đóng góp cá nhân khớp commit/PR.
- Không commit `.env`, secret, `.venv/`, cache, log chứa PII; tuyệt đối không sửa `config/challenge.json`.

## 2. Hiện trạng repository trước khi bắt đầu

Kết quả khảo sát ban đầu:

- Các TODO chính còn ở `app/middleware.py`, `app/main.py`, `app/logging_config.py`, `app/pii.py` và `config/alert_rules.yaml`.
- `app/metrics.py` chưa trả về `error_rate_pct`.
- `app/agent.py` đã có prompt metadata nhưng chưa gắn `correlation_id` vào trace metadata.
- `app/mock_rag.py` và `app/mock_llm.py` chưa có sub-span Langfuse.
- `config/dashboard.yaml` đã đủ contract và validator hiện báo `HỢP LỆ: 6/6 panel`; vẫn cần C rà soát spec/runtime evidence.
- `config/slo.yaml` còn ghi chú placeholder; `docs/alerts.md` và alert rules chưa hoàn thiện.
- `submission/REPORT.md` vẫn là template trống; chưa có `data/logs.jsonl` để lấy baseline.
- Public tests trên máy khảo sát chưa chạy được do thiếu `structlog` và `langfuse`. Đây là việc CP0 phải xử lý bằng cài `requirements.txt` trong virtual environment.
- Challenge K4 đã được release: `day13-k4-observability-v1`, scenario `rag_slow`, affected feature `monitoring`, threshold 2000 ms. File này chỉ được đọc/chạy, không được sửa.

## 3. Nguyên tắc Git và phối hợp

### 3.1 Nhánh đề xuất

- `main`: chỉ chứa trạng thái đã tích hợp và đã kiểm tra.
- `feature/a-api-middleware`
- `feature/b-pii-security`
- `feature/c-metrics-dashboard`
- `feature/d-slo-alerts`
- `feature/e-qa-tracing-report`

Mỗi người chỉ sửa vùng file đã được giao. Nếu cần chạm file của người khác, trao đổi trước và để đúng owner thực hiện hoặc cùng review. Không dùng `git add -A` trên nhánh cá nhân; chỉ stage đúng file thuộc phạm vi của mình.

### 3.2 Quy ước commit

Mỗi đầu ra nên có commit nhỏ, dễ kiểm chứng, ví dụ:

- `feat(logging): propagate correlation id through requests`
- `feat(security): scrub pii across structured log fields`
- `feat(metrics): expose request error rate`
- `docs(alerts): define slo-based incident runbooks`
- `test(observability): verify rag and llm trace spans`

Mỗi PR phải ghi: file đã sửa, lệnh kiểm tra, kết quả, evidence tạo ra và rủi ro còn lại. Không đưa ảnh/evidence của người khác vào commit cá nhân nếu chưa ghi rõ người tạo.

### 3.3 Contract tích hợp chung

- Correlation ID chuẩn: nhận `x-request-id` từ client hoặc sinh `req-<8 ký tự hex>`; trả lại ở header `x-request-id`.
- Log `request_received` và `response_sent` của cùng request phải có cùng correlation ID và metadata.
- `TRAFFIC` hiện đếm request thành công; `ERRORS` đếm request lỗi. Vì vậy C tính `total_requests = TRAFFIC + total_errors`.
- Trace metadata phải giữ nguyên các khóa prompt hiện có và bổ sung `correlation_id`, không thay thế dictionary cũ.
- Error panel/SLO/alert cùng dùng đơn vị phần trăm và cùng tên `error_rate_pct`.
- Dashboard runtime lấy nguồn chuẩn từ `data/logs.jsonl`; `/metrics` được dùng để quan sát nhanh và hỗ trợ điều tra.

## 4. Lịch làm việc tối ưu cho song song

| Mốc | A | B | C | D | E | Cổng tích hợp |
|---|---|---|---|---|---|---|
| 0:00–0:30 CP0 | Cùng dựng môi trường, health check | Cùng lấy baseline PII | Kiểm tra `/metrics` và dashboard validator | Đọc SLO/alert contract | Điều phối load test, ghi baseline vào report | API chạy, logs ≥10, pytest chạy được |
| 0:30–1:15 Wave 1 | Middleware + enrichment | Scrubber + patterns + security tests | `error_rate_pct` + dashboard/spec | SLO + rules + runbook | Sub-spans + prompt/Langfuse chuẩn bị | 5 nhánh làm độc lập |
| 1:15–1:30 Wave 2 | Self-test và PR | Self-test và PR | Self-test và PR | Cross-check ngưỡng với C | Review PR A/B/C/D | PR sẵn sàng merge |
| 1:30–2:10 Merge CP1/CP2 | Sửa xung đột `main.py` nếu có | Chạy audit PII sau merge | Kiểm tra metrics/dashboard | Kiểm tra alert ↔ SLO ↔ dashboard | Merge theo thứ tự, restart API, chạy load test | Tests pass, logs 100/100, dashboard 6/6 |
| 2:10–2:30 Evidence CP2 | Evidence header/error response | Evidence redaction | Evidence dashboard | Evidence rules/runbook | ≥10 traces, prompt v1/v2, waterfall | Checklist CP2 đủ |
| 2:30–3:30 CP3 | Hỗ trợ tra correlation ID | Xác nhận evidence không lộ PII | So sánh metric với baseline | Đối chiếu alert/runbook | Chief Investigator chạy challenge và tổng hợp root cause | Metrics → Trace → Log khớp |
| 3:30–4:00 Final | Review phần API | Secret/PII scan | Review dashboard section | Review SLO/alert section | Hoàn thiện report, chạy kiểm tra cuối | Repo sạch, report/evidence đầy đủ |

Điểm giúp song song tối đa: A/B/C/D/E đều bắt đầu Wave 1 cùng lúc. Chỉ E cần chờ A/B/C merge trước khi tạo evidence cuối; E vẫn làm được tracing, prompt versioning, chuẩn hóa report và chuẩn bị kịch bản điều tra trong lúc chờ.

## 5. Phân công chi tiết

### Thành viên A — API & Middleware

**Phạm vi sở hữu**

- `app/middleware.py`
- Phần enrichment và exception handler trong `app/main.py`
- Phần hiển thị correlation ID khi lỗi trong `scripts/load_test.py`
- Test bổ sung riêng cho middleware/exception nếu cần

**Nhiệm vụ**

1. Hoàn thành bốn TODO của `CorrelationIdMiddleware.dispatch()`:
   - gọi `clear_contextvars()` đầu mỗi request;
   - dùng header `x-request-id` nếu có, nếu không sinh `req-<8hex>`;
   - bind correlation ID vào structlog contextvars;
   - gắn ID vào `request.state` và response header;
   - thêm `x-response-time-ms` theo millisecond.
2. Trong `/chat`, bind `user_id_hash`, `session_id`, `feature`, model thực tế và `APP_ENV` trước `request_received`.
3. Bổ sung generic exception handler để response lỗi 500 vẫn có `x-request-id`. Chú ý luồng hiện tại chuyển lỗi thành `HTTPException`; kiểm tra cả lỗi đi qua handler ứng dụng và lỗi do middleware/ngoài endpoint.
4. Sửa `scripts/load_test.py` để ưu tiên đọc correlation ID từ response header và không giả định body lỗi luôn có cấu trúc thành công.
5. Kiểm tra hai trường hợp: server tự sinh ID và client truyền ID; kiểm tra request đồng thời không dùng lẫn context.

**Không sửa**

- Regex/scrubber của B; công thức metrics của C; SLO/alerts của D; challenge config.

**Nghiệm thu cá nhân**

- Response 200 và 500 đều trả `x-request-id` khi khả thi.
- ID do server sinh khớp `^req-[0-9a-f]{8}$`; ID client cung cấp được propagate nhất quán.
- Mọi log API của một request có cùng ID và đủ enrichment.
- Có test hoặc bằng chứng cho request lỗi; `pytest` phần liên quan pass.

**Evidence bàn giao cho E**

- Một response header có `x-request-id` và `x-response-time-ms`.
- Hai dòng log `request_received`/`response_sent` cùng correlation ID.
- Một response lỗi vẫn truy ra được correlation ID.

### Thành viên B — Security Engineer

**Phạm vi sở hữu**

- `app/pii.py`
- Hàm `scrub_event` và processor pipeline trong `app/logging_config.py`
- `tests/test_pii.py` và test security bổ sung

**Nhiệm vụ**

1. Bật `scrub_event` trước `JsonlFileProcessor` và `JSONRenderer`.
2. Nâng scrubber từ chỉ quét `payload`/`event` thành quét toàn bộ trường string và cấu trúc lồng nhau cần thiết. Nên xử lý an toàn dict/list/tuple thay vì chỉ dict một cấp.
3. Giữ các pattern email, phone VN, CCCD, credit card; bổ sung passport và địa chỉ Việt Nam theo yêu cầu.
4. Viết test matrix tối thiểu:
   - email;
   - phone: liền, dấu cách, dấu chấm, dấu gạch, `+84`;
   - CCCD 12 số;
   - thẻ có/không có khoảng trắng/gạch;
   - passport;
   - từ khóa địa chỉ Việt Nam;
   - PII nằm ở top-level, nested dict và list;
   - negative cases để tránh che nhầm correlation ID, timestamp, token/cost.
5. Sau khi A merge, xóa log cũ, sinh log mới và kiểm tra cả validator lẫn tìm kiếm thủ công. Không commit log nếu còn PII.

**Không sửa**

- Enrichment trong `main.py`; không nới lỏng validator để che lỗi; không hard-code output để qua test.

**Nghiệm thu cá nhân**

- Không còn email, phone, CCCD, credit card, passport/address thô trong log sinh mới.
- Chuỗi được thay bằng `[REDACTED_<TYPE>]` và dữ liệu không nhạy cảm không bị phá.
- `tests/test_pii.py`, `tests/test_validate_logs.py` và full pytest pass sau merge.
- `validate_logs.py` báo `Potential PII leaks detected: 0`.

**Evidence bàn giao cho E**

- File/ảnh terminal validator cuối.
- Một log JSON đã redact nhưng còn đủ context kỹ thuật.
- Bảng test PII đầu vào → marker đầu ra; kết quả tìm `@`, `4111`, số phone thô đều rỗng.

### Thành viên C — Metrics & Dashboard

**Phạm vi sở hữu**

- `app/metrics.py`
- `config/dashboard.yaml`
- `docs/dashboard-spec.md`
- Test metrics/dashboard bổ sung

**Nhiệm vụ**

1. Bổ sung `error_rate_pct` vào `snapshot()`:
   - `total_errors = sum(ERRORS.values())`;
   - `total_requests = TRAFFIC + total_errors`;
   - zero-safe khi chưa có request;
   - làm tròn hai chữ số.
2. Bổ sung tests cho 0 request, toàn success, mixed success/error và toàn error. Test phải cô lập/reset state global để không phụ thuộc thứ tự chạy.
3. Rà soát `config/dashboard.yaml` đủ đúng 6 panel: latency, traffic, errors, cost, tokens, quality. Giữ time range 60 phút, refresh 15–30 giây, đơn vị và threshold.
4. Làm rõ trong `docs/dashboard-spec.md` cho từng panel: tên, event/field nguồn, aggregation/query, đơn vị, time range, threshold/SLO line và cách dựng runtime.
5. Dựng dashboard runtime bằng công cụ nhóm chọn và chụp ảnh đủ tên panel/time range. Contract qua validator chưa thay thế evidence runtime.
6. Đồng bộ ngưỡng với D: latency P95 3000 ms, error SLO 2%, cost 2.5 USD, quality ≥0.75 (hoặc thay đổi có lý do và cập nhật đồng bộ cả ba nơi).

**Không sửa**

- Bộ đếm lỗi trong `main.py` trừ khi đã thống nhất với A; alert rules/runbook thuộc D.

**Nghiệm thu cá nhân**

- `/metrics` có `error_rate_pct` đúng ở mọi trường hợp và không chia cho 0.
- `python scripts/validate_dashboard.py` trả `HỢP LỆ: 6/6 panel`.
- Dashboard runtime đủ 6 nhóm, có threshold/SLO line, đơn vị và time range.
- Tests metrics/dashboard và full pytest pass.

**Evidence bàn giao cho E**

- JSON từ `/metrics` có latency/error/cost/token/quality.
- Kết quả dashboard validator.
- Ảnh dashboard 6 nhóm chỉ số trước incident và trong incident.

### Thành viên D — SRE & Alerts Engineer

**Phạm vi sở hữu**

- `config/slo.yaml`
- `config/alert_rules.yaml`
- `docs/alerts.md`

**Nhiệm vụ**

1. Hoàn thiện bốn SLI/SLO với window 28 ngày; bỏ placeholder và ghi lý do chọn ngưỡng trong report/evidence.
2. Viết ba alert symptom-based:
   - `high_latency_p95`: warning, P95 > 3000 ms trong 5 phút;
   - `elevated_error_rate`: critical, error rate > 5% trong 3 phút;
   - `cost_budget_exceeded`: warning, daily cost > 2.5 USD.
3. Mỗi rule có severity, condition, type, owner và link anchor runbook chính xác.
4. Hoàn thiện ba runbook. Mỗi runbook phải có SLI/SLO, điều kiện, ảnh hưởng người dùng, ba bước kiểm tra đầu tiên, mitigation và owner.
5. Ba bước kiểm tra phải theo luồng điều tra: xem dashboard/time window → mở trace bất thường/span → lọc log theo correlation ID. Mitigation phải phù hợp từng alert, không viết chung chung.
6. Cross-review với C để mọi tên metric, đơn vị, threshold nhất quán; hỗ trợ E dùng runbook thật khi chạy `rag_slow`.

**Không sửa**

- Không đổi metric implementation; không sửa challenge để khớp alert.

**Nghiệm thu cá nhân**

- Không còn `TODO`/placeholder trong ba file sở hữu.
- Link `docs/alerts.md#alert-1/2/3` hoạt động và nội dung khớp rule.
- Alert dựa trên triệu chứng/SLO, không dựa vào tên hàm nội bộ.
- Runbook đủ cụ thể để một thành viên khác làm theo mà không cần hỏi lại.

**Evidence bàn giao cho E**

- Ba rule hoàn chỉnh và ba runbook.
- Bảng mapping Dashboard panel → SLI/SLO → Alert → Runbook.
- Giải thích vì sao alert threshold có thể cao hơn SLO objective để tránh alert noise.

### Thành viên E — QA & Chief Investigator

**Phạm vi sở hữu**

- `app/mock_rag.py`, `app/mock_llm.py`
- Phần trace metadata `correlation_id` trong `app/agent.py`
- `submission/REPORT.md`, `submission/evidence/`
- Điều phối kiểm thử, Langfuse, prompt versioning và CP3

**Nhiệm vụ kỹ thuật trước khi merge**

1. Gắn `@observe(as_type="span")` cho `retrieve()` và `FakeLLM.generate()` để waterfall có `run → retrieve/generate`.
2. Bổ sung `correlation_id` từ `get_contextvars()` vào trace metadata nhưng giữ toàn bộ prompt metadata hiện tại.
3. Kiểm tra decorator không phá `__wrapped__`/public tests và app vẫn chạy khi Langfuse chưa bật.
4. Trên Langfuse tạo prompt v1/v2, gắn label baseline/candidate hoặc production, chạy cùng input, đổi label hoặc rollback và ghi lại trace ID thật. Không giả prompt version trong code.
5. Chuẩn bị cấu trúc evidence và checklist report ngay từ đầu; mỗi ảnh dùng tên mô tả rõ ràng.

**Nhiệm vụ QA sau khi merge**

1. Tạo môi trường sạch, cài dependencies, restart API sau mỗi thay đổi cấu hình.
2. Xóa log cũ trước lần kiểm tra cuối, chạy load test và các lệnh nghiệm thu.
3. Review PR của A/B/C/D theo phạm vi chéo, không tự sửa hộ nếu chưa trao đổi.
4. Thu tối thiểu 10 trace thật; chọn một waterfall thấy rõ `retrieve` và `generate`.

**Nhiệm vụ CP3 — Chief Investigator**

1. Xác thực file release bằng `load_challenge()`; không sửa file.
2. Chụp baseline metrics trước incident.
3. Bật challenge chính thức, chạy `python scripts/load_test.py --challenge --concurrency 5`.
4. Chụp metrics trong incident và so sánh với baseline; với challenge hiện tại kỳ vọng latency của feature `monitoring` vượt threshold 2000 ms.
5. Mở trace trong đúng time window; xác nhận span `retrieve` chiếm phần lớn waterfall, ghi trace ID và correlation ID.
6. Lọc `data/logs.jsonl` theo correlation ID; chỉ ra các event cùng request và latency cụ thể. Với `rag_slow`, log có thể chứng minh độ trễ nhưng không nhất thiết chứa một exception; kết luận phải kết hợp duration span + latency log + trạng thái incident.
7. Ghi root cause, fix action và preventive measure. Ví dụ hướng fix: timeout/circuit breaker, cache/fallback retrieval, latency budget và alert theo feature; chỉ ghi là đề xuất nếu không được yêu cầu triển khai.
8. Tắt incident sau khi thu evidence và xác nhận metrics/request mới hồi phục.
9. Hoàn thiện report; yêu cầu từng thành viên tự kiểm tra phần đóng góp và link commit/PR của mình.

**Nghiệm thu cá nhân**

- Trace waterfall có `run`, `retrieve`, `generate`; trace metadata có correlation ID và prompt metadata.
- Có ≥10 traces, hai prompt version và evidence rollback/label thật.
- CP3 có baseline/incident/recovery, trace ID, correlation ID/log cụ thể.
- Report liên kết đầy đủ evidence và commit của cả 5 người.

## 6. Thứ tự merge và kiểm tra tích hợp

Thứ tự khuyến nghị để giảm xung đột và phát hiện lỗi sớm:

1. **C — Metrics/Dashboard**: độc lập với CP1, merge sớm.
2. **D — SLO/Alerts**: sau khi C và D chốt ngưỡng; chỉ tài liệu/config.
3. **B — PII**: merge processor/patterns trước khi sinh log cuối.
4. **A — API/Middleware**: merge enrichment và error handling; nếu A/B cùng import/chạm `main.py`, A là owner giải quyết.
5. **E — Tracing**: merge sau A để correlation ID context đã tồn tại; sau đó E chạy integration/evidence.
6. **E — Report/Evidence**: merge cuối sau khi tất cả thành viên xác nhận đóng góp.

Sau mỗi PR: rebase/merge `main`, chạy test phạm vi, rồi mới chạy full test. Không merge nếu test đỏ mà chưa ghi rõ nguyên nhân môi trường.

## 7. Test matrix chung

| Hạng mục | Lệnh/kiểm tra | Owner chính | Kết quả cần đạt |
|---|---|---|---|
| Môi trường | `python --version`, cài `requirements.txt` | E | Python ≥3.11, import đủ dependency |
| Public tests | `python -m pytest -q` | E | Pass toàn bộ |
| Log validator | `python scripts/validate_logs.py` | B/E | 100/100 cuối cùng, PII leak = 0 |
| Dashboard contract | `python scripts/validate_dashboard.py` | C | 6/6 panel |
| Health | gọi `/health` | A/E | `ok: true`, tracing đúng trạng thái |
| Middleware | gọi `/chat` có/không có `x-request-id` | A | ID propagate, có response time |
| Error path | practice `tool_fail` | A/E | 500 có thể truy ra correlation ID |
| Metrics | gọi `/metrics` trước/sau success/error | C | error rate và totals đúng |
| PII | load test + scan thủ công | B | Không còn raw PII |
| Tracing | Langfuse list + waterfall | E | ≥10 trace, đủ sub-spans/metadata |
| Prompt | v1/v2 + đổi label/rollback | E | Trace liên kết version thật |
| Challenge | official `--challenge --concurrency 5` | E | M→T→L chứng minh root cause |

Lưu ý: reset/restart process trước phép đo cuối vì metrics được giữ trong biến global in-memory. Xóa `data/logs.jsonl` cũ trước validator cuối để dữ liệu baseline chưa scrub không làm sai kết quả.

## 8. Quy ước evidence và báo cáo

Tên file gợi ý trong `submission/evidence/`:

- `cp0-health.png`, `cp0-baseline-validator.txt`
- `cp1-correlation-log.json`, `cp1-pii-redacted.json`, `cp1-validator-final.txt`
- `cp2-trace-list-10.png`, `cp2-trace-waterfall.png`
- `cp2-prompt-v1.png`, `cp2-prompt-v2.png`, `cp2-prompt-rollback.png`
- `cp2-dashboard-validator.txt`, `cp2-dashboard-6-panels.png`
- `cp2-alert-rules.txt`, `cp2-runbook.md`
- `cp3-metrics-baseline.png`, `cp3-metrics-incident.png`, `cp3-trace-waterfall.png`, `cp3-correlated-log.json`, `cp3-metrics-recovery.png`

Ảnh không được lộ Langfuse secret/API key, email thật hoặc PII. Mọi evidence trong report phải dùng đường dẫn tương đối, ví dụ `evidence/cp2-trace-waterfall.png`.

Phân người điền report:

- A: mục Logging/correlation ID và phần đóng góp A.
- B: mục PII, validator/leak và phần đóng góp B.
- C: dashboard/metrics và phần đóng góp C.
- D: SLO/alerts/runbook và phần đóng góp D.
- E: thông tin nhóm, prompt/tracing, CP3, tổng hợp và commit SHA cuối.

## 9. Checklist final trước khi nộp

- [ ] Repo đúng tên lớp/nhóm và Lab Coach clone được.
- [ ] `.env` có key trên máy chạy nhưng không được Git track.
- [ ] `config/challenge.json` khớp nguyên bản release, không có commit sửa của nhóm.
- [ ] API được restart, incident đã tắt, log cũ đã được làm sạch đúng lúc.
- [ ] `python -m pytest -q` pass.
- [ ] `python scripts/validate_logs.py` đạt 100/100.
- [ ] `python scripts/validate_dashboard.py` đạt 6/6.
- [ ] Có ≥10 traces, waterfall, prompt v1/v2 và rollback/label evidence.
- [ ] Dashboard đủ 6 nhóm; SLO/alerts/runbook nhất quán.
- [ ] CP3 có metric, trace ID, correlation ID/log, root cause, fix và prevention.
- [ ] Report có repo URL, SHA cuối, vai trò, evidence và commit/PR của 5 người.
- [ ] `git status --short` chỉ hiện đúng file dự định commit.
- [ ] Không có secret, `.venv`, cache hoặc PII trong các file sắp push.

## 10. Kịch bản demo ngắn trước Lab Coach

1. Mở dashboard, chỉ ra latency P95 tăng và feature/time window bị ảnh hưởng.
2. Từ time window mở một trace, chỉ ra span `retrieve` chậm so với `generate`.
3. Lấy correlation ID từ trace, lọc log và chỉ ra `request_received`/`response_sent` cùng request cùng latency.
4. Kết luận `rag_slow` ở retrieval là root cause dựa trên ba lớp bằng chứng.
5. Trình bày mitigation tức thời, preventive measure và alert/runbook liên quan.
6. Mỗi thành viên trả lời phần mình: A correlation/contextvars; B processor order/regex; C percentile/error rate; D symptom-based alert; E trace/prompt/incident investigation.


# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phan Dai Cuong | 2A202602510 | Cài harness, chạy thí nghiệm, phân tích kết quả |

- Mô hình: `LAB_MODEL=gpt-6-luna`; `LAB_TEMPERATURE=1`; `recursion_limit=60`.
- Deep Agents 0.7.21; Linux; chạy trực tiếp trong `.venv` Python 3.11.
- Số lần chạy tác vụ: 9 lượt học trước đóng băng; 12 lượt chính thức sau đóng băng (21 tổng). Curator gọi mô hình 1 lần.
- Commit của tag `freeze`: `78757f7`.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán subagents nhỉnh hơn nhẹ về điểm eval nhờ thăm dò độc lập và kiểm tra chéo; trên learn, logs tăng 5/9 lên 6/9, code/data không đổi. Mức tăng chưa chắc bù chi phí: token trung bình learn tăng từ 42.134 lên 73.377 (+74%).
- H2 (skills-auto so với baseline): Dự đoán skills-auto không vượt baseline rõ rệt trên eval. Các skill học từ lỗi quy ước của tập learn có thể chuyển giao quy trình, nhưng eval thêm quy ước mới; tài liệu lab cũng cảnh báo skill do mô hình sinh thường không có lợi trung bình và có thể quá khớp.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm eval thấp hơn learn vì mỗi tác vụ eval thêm quy ước tổ chức chưa quan sát trong feedback của learn; baseline learn đạt 17/18 check kỹ thuật nhưng chỉ 0/9 check quy ước.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` cho phép chạy lệnh shell.
2. `task` tạo subagent tạm thời `general-purpose`; phiên bản mặc định chỉ thấy prompt được gửi trong lần gọi đó và trả một báo cáo cuối. Cần đưa đủ bối cảnh, yêu cầu và dạng đầu ra vào prompt.
3. Từ mô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Từ mô tả `execute`: “Quote paths containing spaces”.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `RULE: every public function ... has type annotations` |
| code-learn | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py ... (at least 3)` |
| code-learn | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under ... ## Unreleased` |
| data-learn | `rule_money_in_cents` | E | `RULE: money values ... are integer cents` |
| data-learn | `rule_meta_block` | E | Thiếu object `meta` với `source`, `rows_in`, `rows_used` theo quy ước. |
| data-learn | `rule_clean_csv` | E | `RULE: write workspace/clean.csv` với schema và định dạng quy định. |
| logs-learn | `counts_by_service` | G | `counts_by_service: wrong values`; trace cho thấy có repeat markers nhưng không xác định chắc nguyên nhân gốc. |
| logs-learn | `rule_service_names` | E | `RULE: service names ... lower-case with '-' replaced by '_'` |
| logs-learn | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending` |
| logs-learn | `rule_schema_header` | E | `RULE: ... schema_version: 2 and generated_by: log-triage` |

Nhận xét: 9/10 check thất bại thuộc nhóm E; lỗi còn lại là sai số liệu tổng hợp, xếp G vì trace không đủ chứng cứ để quy nguyên nhân cho một kiểu dữ liệu bẩn cụ thể. Skill quy trình có thể nhắc kiểm tra quy ước và schema, nhưng không thể khôi phục yêu cầu ẩn nếu tác tử không đọc/áp dụng đúng đặc tả.

## 5. Điều kiện `subagents` (Phần 2.3)

- Định nghĩa: `explorer` đọc đặc tả/dữ liệu và báo cáo; `implementer` thực hiện thay đổi, chạy test; `reviewer` kiểm tra độc lập, không sửa.
- `subagent_calls`: code-learn 2 (`explorer`, `implementer`); data-learn 1 (`explorer`); logs-learn 1 (`explorer`). Baseline cả ba tác vụ có 0. Các lời giao việc nêu đường dẫn, phạm vi, cấm sửa hoặc yêu cầu thực hiện; báo cáo được luồng chính tiếp tục kiểm tra bằng đọc tệp/chạy lệnh ở trace, dù không phải lúc nào cũng kiểm tra mọi quy ước cuối.
- Explorer ở data được yêu cầu kiểm tra cột, quy ước, trùng lặp và tính độc lập; explorer ở logs được yêu cầu nêu định dạng, repeat markers và pitfall. Phạm vi đủ rõ, không thấy yêu cầu mâu thuẫn.
- Token trung bình tăng từ 42.134 (baseline) lên 73.377 (+74%); thời gian trung bình tăng từ 34,2 giây lên 78,5 giây (+130%). Điểm học trung bình chỉ tăng từ 0,625 lên 0,656; logs tăng 1/9, code và data không đổi. Chi phí tăng đáng kể so với lợi ích điểm quan sát được.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Curator chạy 1 lần, sinh 3 skill hợp lệ; không xóa skill nào.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `regression-ready-package-fixes` | Khá tổng quát cho sửa lỗi package; không nêu task ID hay mã riêng. | Hợp lý, nhưng type hints nhắm hàm được sửa/thêm trong khi feedback yêu cầu mọi hàm public trong package; kiểm tra của agent vẫn bỏ regression/changelog. | 9 dòng; trigger nêu package có API/test/changelog checks; code-learn đọc 1 skill. |
| `precise-monetary-data-cleaning` | Tổng quát cho làm sạch số liệu tài chính. | Các ý decimal/cents, dedup, UTC, schema phù hợp; agent đọc skill nhưng vẫn thiếu quy ước tiền cents/meta/CSV. | 9 dòng; trigger rõ dạng tác vụ; data-learn đọc 1 skill. |
| `structured-log-output-validation` | Tổng quát cho chuẩn hóa log. | Hướng dẫn normalize, sort và metadata là đúng; logs-learn vẫn sắp theo thời gian thay vì service rồi timestamp và không hoàn tất hai quy ước còn lại. | 9 dòng; trigger rõ; logs-learn đọc 2 skill (log và monetary). |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Không có lần chạy chính thức nào có `error` hoặc `skills_modified = true`. `verify_freeze.py` xác nhận `OK` cho 6 run skills-auto.

```markdown
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 9/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 5/9 | 6/9 | 6/9 |
| code-eval | 7/11 | 7/11 | 9/11 |
| data-eval | 5/9 | 5/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.63 | 0.66 | 0.73 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.66 |
| **Mean tokens per run** | 40,234 | 83,835 | 71,548 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |
```

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          38,335      0/3
baseline      learn    17/18         0/9           42,133      0/3
subagents     eval     18/18         0/12          94,293      0/3
subagents     learn    18/18         0/9           73,377      0/3
skills-auto   eval     18/18         2/12          63,726      3/3
skills-auto   learn    18/18         2/9           79,370      3/3
```

## 8. Phân tích

1. Trên learn, subagents tăng trung bình từ 0.63 lên 0.66 (chỉ logs tăng 5/9 lên 6/9); skills-auto đạt 0.73, với code 7/10 lên 9/10 và logs 5/9 lên 6/9. Trên eval, subagents không đổi trung bình so với baseline (0.60); skills-auto đạt 0.66 nhờ code-eval 7/11 lên 9/11, còn data/logs không đổi. Không thấy cải thiện learn bị mất hoàn toàn trên eval, nhưng lợi ích tập trung ở code và chỉ có một run mỗi điều kiện nên chưa kết luận được khả năng tổng quát.
2. Toàn bộ điều kiện đạt 18/18 check kỹ thuật eval. Trên learn, baseline đạt 17/18 kỹ thuật, subagents và skills-auto 18/18. House rules learn: baseline 0/9, subagents 0/9, skills-auto 2/9; eval lần lượt 0/12, 0/12, 2/12. Skill code giúp áp dụng type hints/regression tests ở code-eval nhưng vẫn thiếu changelog/version bump. Skill data không giúp các quy ước cents/meta/CSV trên data-eval. Skill logs không giúp quy ước service/sort/header/source-line mới trên logs-eval. Skill không thể nêu đúng quy tắc eval chưa từng có trong feedback nếu tác tử không suy ra từ đề.
3. Ở code-eval, trace cho thấy tác tử đọc `regression-ready-package-fixes`; `rule_type_hints` và `rule_regression_tests` đạt, nhưng `rule_changelog` và `rule_version_bump` trượt. Đây là ví dụ skill giúp một phần. Ở data-learn, trace xác nhận skill tiền tệ được đọc (`skills_read=1`), nhưng run vẫn trượt cả ba quy ước money/meta/CSV; skill được tải không đảm bảo mọi chỉ dẫn được áp dụng hoặc mọi yêu cầu được kiểm tra.
4. Mean tokens/run: baseline 40.234; subagents 83.835 (+108% so với baseline); skills-auto 71.548 (+78%). Điểm trên mỗi token, xấp xỉ theo mean score chia mean tokens: learn 0.0000157 / 0.0000078 / 0.0000102; eval 0.0000149 / 0.0000072 / 0.0000092 cho baseline/subagents/skills-auto. Baseline tiết kiệm nhất theo tỷ lệ thô; skills-auto có điểm eval cao hơn nhưng tốn thêm token; subagents không đáng chi phí trong mẫu này vì điểm eval không tăng.
5. Không thấy rò rỉ eval: curator chỉ đọc run có `role=learn`; ba skill qua `validate_skill`, không chứa marker eval; `verify_freeze.py` xác nhận hash skills khớp và không sửa trong các run chính thức. Có dấu hiệu chuyển giao một phần ở code, nhưng khác biệt code-learn giữa các lần chạy cũng cho thấy nhiễu; chưa có cơ sở khẳng định không overfit chỉ từ sáu tác vụ.
6. Cùng bộ skill, code-learn đạt 8/10 ở Phần 3.4 và 9/10 sau freeze (chênh +1 check); data-learn 5/8 ở cả hai lượt; logs-learn 6/9 ở cả hai. Do không đổi skill mà kết quả code đổi, ít nhất một check dao động theo lần chạy. Vì vậy chênh lệch nhỏ trong bảng, nhất là một check, không đáng tin nếu không lặp nhiều lần.

## 9. Hạn chế và tính hợp lệ

1. Chỉ có 3 tác vụ cho mỗi vai trò và một run cho mỗi condition/task; một check dao động ở code-learn giữa hai run skills-auto, nên không thể ước lượng phương sai hoặc kiểm định ý nghĩa.
2. Chỉ dùng một deployment và cấu hình; hành vi công cụ, độ tuân thủ skill, chi phí token không đại diện cho mô hình khác.
3. Tác vụ và quy ước do bộ lab thiết kế sẵn, có thể ưu tiên một số hành vi như type hints, changelog và schema; kết luận không tự động khái quát sang công việc thực tế.
4. Curator chỉ được gọi một lần và tối đa ba skill; chất lượng/độ bao phủ phụ thuộc đầu ra ngẫu nhiên của LLM. `run.json` eval cố ý làm rỗng `detail`, nên phân tích nguyên nhân eval dựa vào check name và trace chứ không có phản hồi chi tiết.

## 10. Kết luận

Trong thí nghiệm này, subagents tăng mạnh chi phí nhưng không cải thiện điểm eval. Skills-auto đạt điểm eval trung bình cao hơn 0.06 so với baseline, phần tăng nằm ở code-eval; data và logs không đổi. Các skill được đọc trong cả sáu run, nhưng chỉ hai house-rule checks đạt ở mỗi vai trò learn/eval và nhiều quy ước mới vẫn trượt. Kết quả còn nhiễu và số tác vụ nhỏ; bước tiếp theo nên lặp eval nhiều lần và kiểm tra skill theo từng quy tắc.

## Phụ lục

- Lệnh đã chạy (theo thứ tự): `pytest tests/test_01_provided.py`; `python scripts/tour.py`; `pytest tests/test_02_agent.py -k subagents`; `pytest tests/test_02_agent.py`; `pytest tests/test_03_runner.py`; baseline data-learn; baseline code/logs learn và subagents learn (do nhóm chạy trước); `pytest tests/test_04_curator.py`; `python -m lab.curator`; skills-auto learn; toàn bộ 29 test offline; commit `hypotheses`; tag `freeze`; baseline eval; subagents eval; skills-auto all; `verify_freeze.py`; `python -m lab.compare`; `check_breakdown.py`.
- Thử thách mở rộng 6c (red team curator): dùng scripted model để trả về một skill chứa marker thuộc eval và một skill có tên `../evil`. Test `test_curator_writes_only_valid_skills_and_never_leaks` xác nhận chỉ skill hợp lệ được ghi, marker eval bị chặn và đường dẫn traversal không tạo tệp ngoài thư mục skill. Biện pháp phòng vệ là chỉ nạp run `role=learn`, kiểm tra nội dung bằng `validate_skill`/`eval_markers`, xác thực tên bằng allowlist regex rồi mới tạo đường dẫn. Đây là kiểm tra có kiểm soát ngoại tuyến, không phải tấn công prompt injection lên deployment thật.
- Ghi chú: lần `skills-auto --tasks learn` trước freeze được giữ ở `results/skills-auto-dev/`; các lần chính thức ở `results/skills-auto/`. Số lượt benchmark: 3 baseline learn + 3 subagents learn + 3 skills-auto dev + 3 baseline eval + 3 subagents eval + 6 skills-auto chính thức = 21.

# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Phan Dai Cuong | 2A202602510 | Cài harness, chạy thí nghiệm, phân tích kết quả |

- Mô hình: `LAB_MODEL=gpt-6-luna`; `LAB_TEMPERATURE=1`; `recursion_limit=60`.
- Deep Agents 0.7.21; Linux; chạy trực tiếp trong `.venv` Python 3.11.
- Số lần chạy tác vụ: 9 lượt học trước đóng băng; 12 lượt chính thức sau đóng băng (21 tổng). Curator gọi mô hình 1 lần.
- Commit của tag `freeze`: điền sau khi tạo tag.

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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:

"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
      {
        "name": "explorer",
        "description": "Use before implementation when the task requires inspecting unfamiliar files, requirements, tests, or data; report relevant facts and risks without editing files.",
        "system_prompt": "Inspect the requested files and requirements. Report concise findings with file paths and evidence. Do not modify files or claim that tests passed unless you ran them.",
      },
      {
        "name": "implementer",
        "description": "Use for a non-trivial, well-scoped code or data change after the requirements are understood; make the change and run the most relevant tests.",
        "system_prompt": "Implement only the requested change. Inspect the existing conventions first, make focused edits, run relevant tests, and report changed files and actual test results.",
      },
      {
        "name": "reviewer",
        "description": "Use after a change when an independent check is useful; compare the result with the task requirements and look for edge cases without editing files.",
        "system_prompt": "Review the proposed result against the stated requirements and relevant tests. Do not modify files. Report concrete defects or risks with evidence, or say when you found none.",
      },
    ]

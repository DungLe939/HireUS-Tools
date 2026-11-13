# Spec Kit trong workspace HireUS

Bộ skills Spec Kit trong FE/BE là workflow được nhóm điều chỉnh cho HireUS,
dùng chung với các agent có khả năng đọc/sửa file. Chúng mô tả công việc và artifacts,
không phụ thuộc một cú pháp gọi lệnh, tool MCP hoặc hệ thống subagent.

Sửa nhỏ hoặc review làm trực tiếp. Tính năng lớn có thể dùng:
`specify → clarify (nếu cần) → plan → tasks → implement → analyze/converge`.
Không bắt buộc chạy mọi bước cho mỗi thay đổi.

Chạy trong repo sở hữu phần implementation:
- [Frontend](../../frontend/.agents/references/spec-kit.md).
- [Backend](../../backend/.agents/references/spec-kit.md).

Ở gốc workspace, dùng
[hireus-workflow](../skills/hireus-workflow/SKILL.md) để phối hợp.
Nghiệp vụ nằm trong `documents/docs/`; contract HTTP nguồn do backend sở hữu.
Spec cục bộ ghi phạm vi triển khai và dẫn nguồn, không tự trở thành yêu cầu mới.

`python3 .agents/scripts/check_workspace.py` kiểm tra hướng dẫn, tài nguyên,
metadata cơ bản của skills, JSON/TOML và ignore trong phạm vi được liệt kê.
Nó không chạy implementation, gọi AI, tạo nhánh hoặc cài công cụ.

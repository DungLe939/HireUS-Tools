# Dùng bộ skills HireUS

Bắt đầu tại [AGENTS.md](../AGENTS.md). Agent không tự nhận skills vẫn có thể đọc
`SKILL.md` trực tiếp; tên tool/cú pháp gọi theo công cụ thực tế của thành viên.

| Đầu việc | Dùng |
| --- | --- |
| Đọc dự án hoặc tìm yêu cầu mới nhất | [project-navigator](skills/project-navigator/SKILL.md) |
| Làm một tính năng qua nhiều repo | [hireus-workflow](skills/hireus-workflow/SKILL.md) |
| Nhắc cập nhật nhánh, chuẩn bị commit/push hoặc xử lý remote đi trước | [team-sync](skills/team-sync/SKILL.md) |
| Rà tài liệu còn đúng không, cập nhật tổng hợp hoặc bỏ bản lỗi thời | [docs-maintenance](../documents/.agents/skills/docs-maintenance/SKILL.md) |
| Frontend | [hướng dẫn FE](../frontend/AGENTS.md) |
| Backend, contract và dữ liệu | [hướng dẫn BE](../backend/AGENTS.md) |
| Soạn/review bài nộp, kiểm tra hoặc sync tài liệu | [hướng dẫn tài liệu](../documents/AGENTS.md) |
| Lưu spec/plan/tasks cho feature lớn | [Spec Kit](references/spec-kit.md) |

Ví dụ yêu cầu, có thể dùng bằng ngôn ngữ tự nhiên với bất kỳ agent đọc được repo:
- “Đọc AGENTS.md và skill project-navigator; tìm yêu cầu mới nhất cho Job Matching.”
- “Dùng hireus-workflow triển khai phần xác nhận dữ liệu theo tiêu chí đã thống nhất.”
- “Trong backend, dùng backend-quality review diff hiện tại, chỉ báo lỗi có căn cứ.”
- “Trong documents, kiểm tra bản Markdown/HTML theo template Week02, chưa sửa bài nguồn.”
- “Bắt đầu làm Job Matching: kiểm tra nhánh và nhắc phần cần cập nhật trước.”
- “Chuẩn bị push phần vừa làm: lấy thay đổi remote, rà tài liệu cũ, sửa phần sai và tổng hợp kết quả.”
- “Push bị non-fast-forward: kiểm tra upstream, tích hợp thay đổi và kiểm tra lại tài liệu.”

Khi bắt đầu việc có sửa, agent kiểm tra nhánh và nhắc cập nhật một lần nếu cần.
Trước push, agent đối chiếu tài liệu liên quan, sửa/bỏ bản dẫn xuất đã lỗi thời,
chạy kiểm tra và tổng hợp thay đổi rồi công bố trong phạm vi đã được yêu cầu.
Không phải mọi lần push đều cần tải Drive hoặc tạo một báo cáo mới.
Đây là workflow cho agent đọc, không phải hook tự cài hoặc tác vụ chạy nền.

Skills dùng chung nằm ở repo sở hữu chúng; không chép sang config cá nhân.
Các reviewer `.codex/agents/` là adapter riêng, dẫn về các skill review này.
Nội dung Spec Kit được nhóm duy trì; cập nhật upstream cần so sánh trước khi ghi đè.

Kiểm tra từ gốc:
`python3 .agents/scripts/check_workspace.py`.
Kiểm tra bộ script workspace:
`python3 -m unittest discover -s .agents/scripts/tests -v`.

Skills, references, tests, scripts và adapter cần nằm trong Git. Cache/secrets vẫn
được ignore. Chỉ commit/push khi được yêu cầu, theo đúng repo và nhánh đang làm.

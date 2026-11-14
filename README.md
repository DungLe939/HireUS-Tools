# HireUS Tools

Workspace đồ án HireUS Tools gồm ba Git submodule:

| Thư mục | Nội dung |
| --- | --- |
| [frontend](frontend/README.md) | Ứng dụng Next.js |
| [backend](backend/README.md) | Máy chủ NestJS |
| [documents](documents/README.md) | Yêu cầu, thiết kế và bài nộp |

## Lấy dự án

```bash
git clone --recurse-submodules https://github.com/DungLe939/HireUS-Tools.git
cd HireUS-Tools
```

Nếu đã clone nhưng thiếu repo con:

```bash
git submodule update --init --recursive
```

Lệnh trên checkout phiên bản submodule được repo chính ghi nhận; không đồng nghĩa
lấy nhánh tính năng mới nhất. Mỗi submodule có nhánh và lịch sử Git riêng.
Kiểm tra trạng thái local trước khi cập nhật.

## Làm việc cùng AI coding agent

Client Gemini qua Trạm Mây cho công cụ local: [cấu hình và cách gọi](scripts/README.md).

Đọc [AGENTS.md](AGENTS.md) để chọn hướng dẫn phù hợp. Mở workspace ở gốc khi
làm tính năng qua FE/BE; cũng có thể mở riêng từng repo con.

- [Điều hướng dự án](.agents/skills/project-navigator/SKILL.md).
- [Quy trình triển khai tính năng](.agents/skills/hireus-workflow/SKILL.md).
- [Cập nhật nhánh, rà tài liệu và chuẩn bị push](.agents/skills/team-sync/SKILL.md).
- [Đồng bộ gitlink repo cha với repo con](.agents/skills/submodule-sync/SKILL.md).
- [Sửa/gộp/bỏ tài liệu lỗi thời theo bằng chứng](documents/.agents/skills/docs-maintenance/SKILL.md).
- [Spec Kit tùy chọn và môi trường chạy](.agents/references/spec-kit.md).
- [Công cụ tài liệu](documents/.agents/README.md).

Các skills và hướng dẫn được chia sẻ qua Git cùng repo sở hữu chúng. Thành viên
không phải sao chép vào thư mục cá nhân. Nếu agent hỗ trợ tự nạp skills, làm mới
phiên theo cách của công cụ đó. Nếu không, yêu cầu agent đọc `AGENTS.md` và đúng
`SKILL.md` trực tiếp. Khi mở ở gốc, đọc skills repo con theo [AGENTS.md](AGENTS.md).

Nội dung skill không phụ thuộc một hãng agent. Khả năng tự tìm file và cú pháp gọi
skill tùy công cụ. Các file `.codex/agents/*.toml` là adapter reviewer riêng cho
Codex; agent khác có thể thực hiện review bằng các skill chất lượng trong FE/BE.

Khi bắt đầu việc có sửa code/tài liệu chung, agent tự fetch và tích hợp main của repo
liên quan vào nhánh đang làm; giữ việc local, báo trường hợp bị cản trở. Chỉ đọc,
review, plan riêng hoặc chỉ dẫn offline/không sync thì không tự tích hợp. Trước push,
agent đối chiếu tài liệu liên quan, sửa/bỏ bản dẫn xuất lỗi thời có căn cứ và tổng
hợp đã làm gì, đã kiểm tra gì, phần còn thiếu. Đồng bộ tài liệu không mặc định tải
Drive; chỉ commit công việc/push khi được yêu cầu, ngoại lệ là merge commit tích hợp
main an toàn được phép tự tạo ở đầu việc. Xem các skill trên cho working tree bẩn,
conflict, remote đi trước và thứ tự công bố submodule/repo cha.

Để phát hiện repo tổng còn ghim phiên bản cũ của repo con, chọn nhánh đích và chạy:

```bash
python3 .agents/scripts/check_submodules.py --target main --remote
```

Lệnh chỉ đọc; không fetch, merge hoặc push. Nó phân biệt checkout local, tip nhánh
đích và gitlink đã commit/stage/công bố của repo cha. Chỉ báo đồng bộ toàn workspace
khi kiểm tra live sau công bố đạt; sync repo con trên máy chưa cập nhật gitlink GitHub.

Kiểm tra hướng dẫn và khả năng chia sẻ:

```bash
python3 .agents/scripts/check_workspace.py
```

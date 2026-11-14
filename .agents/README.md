# Dùng bộ skills HireUS

Bắt đầu tại [AGENTS.md](../AGENTS.md). Agent không tự nhận skills vẫn có thể đọc
`SKILL.md` trực tiếp; tên tool/cú pháp gọi theo công cụ thực tế của thành viên.

| Đầu việc | Dùng |
| --- | --- |
| Đọc dự án hoặc tìm yêu cầu mới nhất | [project-navigator](skills/project-navigator/SKILL.md) |
| Làm một tính năng qua nhiều repo | [hireus-workflow](skills/hireus-workflow/SKILL.md) |
| Tự cập nhật main đầu việc, chuẩn bị commit/push hoặc xử lý remote đi trước | [team-sync](skills/team-sync/SKILL.md) |
| Sync repo con và gitlink repo cha, xác minh công bố toàn workspace | [submodule-sync](skills/submodule-sync/SKILL.md) |
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
- “Làm Job Matching”: agent tự cập nhật main của repo liên quan trước khi sửa.
- “Chuẩn bị push phần vừa làm: lấy thay đổi remote, rà tài liệu cũ, sửa phần sai và tổng hợp kết quả.”
- “Push bị non-fast-forward: kiểm tra upstream, tích hợp thay đổi và kiểm tra lại tài liệu.”
- “Kiểm tra repo tổng có đang ghim commit cũ của repo con không, đích là main.”
- “Công bố workspace lên main: xử lý repo con, gitlink repo cha và xác minh remote cuối cùng.”

Khi bắt đầu việc có sửa code/tài liệu chung, agent tự fetch và tích hợp main của repo
liên quan một lần, giữ nhánh hiện tại. Có thể tạo merge commit tích hợp khi tree sạch.
Nếu tree bẩn cần tích hợp, conflict hoặc lỗi mạng thì giữ phần local, báo phần chưa
cập nhật và tiếp tục việc độc lập; không tự stash, reset, bỏ hook hoặc ghi đè file ignored.
Trước push, agent đối chiếu tài liệu liên quan, sửa/bỏ bản dẫn xuất đã lỗi thời,
chạy kiểm tra và tổng hợp thay đổi rồi công bố trong phạm vi đã được yêu cầu.
Không phải mọi lần push đều cần tải Drive hoặc tạo một báo cáo mới.
Đây là workflow cho agent đọc, không phải hook tự cài hoặc tác vụ chạy nền.

Helper thực hiện cập nhật (chọn repo đúng phạm vi, đích mặc định `main`):

```bash
python3 .agents/scripts/sync_main.py --repo frontend --repo documents
```

Kết quả JSON: `up_to_date`, `fast_forwarded`, `merged` hoặc `needs_attention`.
Mã thoát 0 = đã tích hợp/đã chứa đích vừa fetch; 2 = có repo cần xử lý thêm.
Đây là cập nhật local, không push, stage gitlink cha hay merge GitHub.
Chỉ đọc/review/plan riêng hoặc được yêu cầu offline/không sync thì không tự cập nhật.

Với nhiều repo, quy trình chỉ hoàn tất công bố sau khi **repo con đã công bố →
gitlink được cập nhật → repo cha đã công bố → xác minh live đạt**. Chỉ sync local
thì báo trạng thái local và phần chưa công bố. Không tự merge mọi nhánh cá nhân.

Kiểm tra submodule (đổi `main` theo nhánh đích):

```bash
python3 .agents/scripts/check_submodules.py --target main --remote
```

Script chỉ đọc. Bỏ `--remote` để kiểm tra cache offline; thêm `--json` để agent xử lý.
Mã thoát 0 = đã khớp live, 1 = cần sync, 2 = chưa xác minh đủ. Giải thích các cột và
giới hạn tại [hướng dẫn checker](skills/submodule-sync/references/checker.md).

Skills dùng chung nằm ở repo sở hữu chúng; không chép sang config cá nhân.
Các reviewer `.codex/agents/` là adapter riêng, dẫn về các skill review này.
Nội dung Spec Kit được nhóm duy trì; cập nhật upstream cần so sánh trước khi ghi đè.

Kiểm tra từ gốc:
`python3 .agents/scripts/check_workspace.py`.
Kiểm tra bộ script workspace:
`python3 -m unittest discover -s .agents/scripts/tests -v`.

Skills, references, tests, scripts và adapter cần nằm trong Git. Cache/secrets vẫn
được ignore. Chỉ commit công việc/push khi được yêu cầu, theo đúng repo và nhánh đang
làm; merge commit tích hợp main an toàn ở đầu việc là ngoại lệ được phép ở trên.

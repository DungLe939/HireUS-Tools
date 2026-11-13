# HireUS Tools — hướng dẫn workspace

## Bắt đầu công việc

Workspace gồm ba Git submodule: `frontend/`, `backend/`, `documents/`.
Đọc `AGENTS.md` trong từng repo liên quan trước khi sửa; khi mở agent ở gốc,
chủ động đọc hướng dẫn và skill của repo con, không giả định chúng đã được nạp.

## Dùng với các agent khác nhau

- `AGENTS.md` và `.agents/skills/*/SKILL.md` là nguồn hướng dẫn dùng chung.
  Nếu công cụ không tự nhận các file này, yêu cầu agent đọc chúng trực tiếp trước khi làm.
  Không giả định mọi agent có cùng cách tự nạp file hoặc cú pháp gọi skill.
- Skills mô tả việc cần làm và kết quả cần kiểm tra. Dùng công cụ đọc/sửa file,
  shell, tìm kiếm hoặc connector tương đương đang có; không bắt buộc tên tool của một hãng.
  Thiếu khả năng cần thiết thì báo giới hạn và tiếp tục phần độc lập.
- `.codex/agents/*.toml` là cấu hình reviewer riêng cho Codex, không phải định dạng
  reviewer chung. Agent khác dùng các skill review FE/BE trực tiếp; không cần có subagent.
- Cấu hình theo từng công cụ chỉ dẫn về nguồn chung; không sao chép quy tắc dự án
  thành nhiều bản riêng cho từng agent. Skills và adapter dùng chung đều giữ trong Git.

| Công việc | Đọc tiếp |
| --- | --- |
| Đọc dự án, tìm nguồn hoặc tiến độ | [.agents/skills/project-navigator/SKILL.md](.agents/skills/project-navigator/SKILL.md) |
| Triển khai tính năng qua nhiều repo | [.agents/skills/hireus-workflow/SKILL.md](.agents/skills/hireus-workflow/SKILL.md) |
| Bắt đầu làm, cập nhật nhánh hoặc chuẩn bị commit/push | [.agents/skills/team-sync/SKILL.md](.agents/skills/team-sync/SKILL.md) |
| Giao diện Next.js | [frontend/AGENTS.md](frontend/AGENTS.md) |
| API, dữ liệu, AI phía máy chủ | [backend/AGENTS.md](backend/AGENTS.md) |
| Yêu cầu, bài nộp, Markdown/HTML, Drive | [documents/AGENTS.md](documents/AGENTS.md) |

## Nguồn và phạm vi

- Quy tắc chọn nguồn nằm tại [documents/.agents/rules/source-of-truth.md](documents/.agents/rules/source-of-truth.md).
  Yêu cầu sản phẩm nằm trong `documents/docs/`; code và kết quả kiểm tra xác nhận việc đã triển khai.
  Khi cùng nội dung có mâu thuẫn, lấy phiên bản nội dung mới nhất làm gốc theo chỉ dẫn nhóm;
  dùng revision/lịch sử thay đổi, không lấy ngày copy file để quyết định.
- Chỉ sửa các repo cần thiết cho yêu cầu. Một tác vụ FE/BE riêng không tự cho phép sửa
  tài liệu chuẩn; yêu cầu phối hợp nhiều repo cho phép sửa các phần liên quan trong từng repo.
  Theo quy ước nhóm, trước bàn giao/push phải đối chiếu và cập nhật tài liệu kỹ thuật,
  tổng hợp liên quan đến phần việc; đọc hướng dẫn repo tài liệu trước khi sửa.
  Không đổi yêu cầu nghiệp vụ để hợp thức hóa code chưa đúng; dùng quyết định mới có nguồn.
- Backend sở hữu hợp đồng HTTP tại `backend/contracts/`. Khi được yêu cầu thiết kế API,
  đề xuất giao diện từ yêu cầu đã rõ, ghi phần còn chưa quyết định; FE tích hợp theo contract
  đã thống nhất. Không tự chọn auth, quyền truy cập hoặc ý nghĩa dữ liệu còn thiếu.
- Sửa nhỏ có thể làm trực tiếp. Tính năng lớn cần phạm vi và tiêu chí nghiệm thu đủ rõ;
  không bắt buộc dùng toàn bộ Spec Kit. Cách dùng tùy chọn nằm tại
  [.agents/references/spec-kit.md](.agents/references/spec-kit.md).

## Git và chia sẻ

- Khi bắt đầu đầu việc có sửa, dùng `team-sync`: kiểm tra upstream/local và nhắc cập
  nhật nhánh nếu chưa làm. Không lặp lại ở mỗi tin nhắn hoặc tự pull khi chỉ đọc local.
- Trước commit/push, tổng hợp cả commit chưa công bố và diff/file mới liên quan;
  đối chiếu code, contract, yêu cầu và tài liệu. Dùng
  [docs-maintenance](documents/.agents/skills/docs-maintenance/SKILL.md) để sửa,
  gộp/bỏ tài liệu dẫn xuất lỗi thời và cập nhật callers; giữ nguồn lịch sử có ghi chú.
  Kết luận không cần sửa tài liệu cũng phải có đối chiếu, không tạo báo cáo cho đủ thủ tục.
- Kiểm tra nhánh và thay đổi local ở repo chính lẫn repo con trước khi sửa.
  Nhánh của repo chính không tự đổi nhánh submodule.
- Quy ước nhánh: `<thành-viên>/<epic>`, ví dụ `dung/job-matching-skill-gap`.
  Giữ nhánh đang làm; chỉ tạo/chuyển nhánh khi tác vụ yêu cầu.
- `AGENTS.md`, `.agents/skills/`, rules, scripts và reviewer `.codex/agents/`
  là tài nguyên dùng chung, phải được Git theo dõi; không thêm chúng vào ignore.
  Chỉ bỏ qua secrets, cache và kết quả sinh tạm.
- Chỉ stage/commit/push khi được yêu cầu. Với thay đổi qua nhiều repo, commit/push
  submodule trước, rồi cập nhật gitlink ở repo chính khi được yêu cầu công bố toàn workspace.
  Báo từng repo; không coi một commit ở gốc là đã lưu nội dung repo con.
- Khi yêu cầu cập nhật hoặc push, fetch các remote liên quan trước khi xác nhận đã
  mới nhất. Xử lý remote đi trước theo
  [hướng dẫn Git](.agents/skills/team-sync/references/git-sync.md), không force-push.
  Bàn giao gồm đã làm gì, kiểm tra, tài liệu sửa/giữ/xóa và phần chưa hoàn thành.

## Kiểm tra và bàn giao

Chạy lệnh từ đúng repo, theo thay đổi thực tế:

| Phần thay đổi | Kiểm tra |
| --- | --- |
| Hướng dẫn dùng chung | `python3 .agents/scripts/check_workspace.py` |
| Script workspace | `python3 -m unittest discover -s .agents/scripts/tests -v` |
| Tài liệu | `python3 documents/.agents/scripts/check_docs.py` |
| Frontend | `npm run lint`, `npx tsc --noEmit`, `npm run build` |
| Backend | `npm test -- --runInBand`, `npm run build`; e2e khi đổi luồng HTTP |

Với chỉnh hướng dẫn, không cần build ứng dụng không đổi. Báo kết quả đã chạy,
các repo/file thay đổi và giới hạn còn lại. Giải thích bằng tiếng Việt các luồng
và lựa chọn kỹ thuật đáng chú ý khi triển khai code.

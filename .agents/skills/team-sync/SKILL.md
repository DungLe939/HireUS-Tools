---
name: team-sync
description: Tự cập nhật từ main khi bắt đầu việc có sửa trong HireUS, giữ công việc local; đối chiếu tài liệu, chuẩn bị commit/push và xử lý remote đi trước.
---

# Đồng bộ công việc của nhóm

Đọc [AGENTS.md](../../../AGENTS.md) và hướng dẫn repo liên quan. Dùng Git/file tools
của agent hiện tại; không cần subagent, connector hoặc cú pháp của một hãng.
Skill hướng dẫn agent, không tự cài hook hay chạy nền sau mỗi lệnh Git.

## Khi bắt đầu một việc có sửa

- Xem nhánh, upstream, thay đổi staged/unstaged/untracked và trạng thái submodule.
  Ghi HEAD làm mốc đầu việc, giữ các thay đổi có sẵn ngoài phạm vi.
- Theo quyền thường trực của nhóm, **tự fetch và tích hợp `origin/main` vào nhánh
  hiện tại** trước khi sửa code/tài liệu chung của đầu việc; không chỉ nhắc và chờ
  người dùng nói “pull”. Đích khác được chỉ định rõ thì ưu tiên đích đó.
  Main là nhánh nền; upstream nhánh cá nhân là đích công bố, không thay main khi sync nền.
- Chỉ chọn repo cần sửa và repo nguồn phụ thuộc thực sự cần cập nhật; không mặc định
  pull cả workspace. Làm một lần cho đầu việc, không mỗi tin nhắn. Khi chỉ đọc/review,
  lập plan riêng, hoặc được yêu cầu offline/không sync thì không tự thay checkout.
- Dùng [sync_main.py](../../../.agents/scripts/sync_main.py) từ root, ví dụ:
  `python3 .agents/scripts/sync_main.py --repo frontend --repo documents`.
  Clone độc lập không có script thì thực hiện tương đương theo `AGENTS.md` tại repo đó.
  Script fetch, fast-forward hoặc tạo merge commit tích hợp khi tree sạch, giữ nhánh;
  nếu conflict thì abort lượt merge nó vừa tạo. Không stash, reset, rebase hoặc push.
- Tree bẩn và cần tích hợp: fetch được nhưng giữ nguyên file/index, báo phần đang
  cản trở và tiếp tục việc độc lập. Detached HEAD/Git operation dở/mạng lỗi báo rõ;
  không khẳng định main mới nhất từ cache. Không bỏ hook hay ghi đè file ignored.
- Quyền tự cập nhật gồm merge commit tích hợp main khi cần, không gồm commit công
  việc chưa lưu, stage gitlink cha, push/merge GitHub hay gửi tài liệu lên Drive.
- Sau cập nhật, đọc lại diff của hướng dẫn, yêu cầu và contract bị ảnh hưởng.
  Fetch nhánh mới không có nghĩa đổi sang nhánh đó hoặc gộp tất cả nhánh vào nhánh cá nhân.
- Nếu thao tác gồm repo con hoặc gitlink, đọc
  [submodule-sync](../submodule-sync/SKILL.md) để phân biệt checkout local,
  nhánh đích remote và con trỏ đã công bố ở repo cha.

Chi tiết về working tree bẩn, nhánh phân kỳ, push bị từ chối và gitlink nằm tại
[xử lý Git](references/git-sync.md); đọc khi thực hiện các thao tác này.

## Trước commit hoặc push

1. Xác định repo/nhánh/phạm vi được công bố. Đọc cả commit chưa push, staged diff,
   working tree và file mới liên quan; không chỉ tóm tắt commit cuối hoặc `git diff`.
2. Đối chiếu thay đổi với README/cách chạy, config mẫu, contract, spec/tasks và
   tài liệu dự án liên quan. Dùng
   [docs-maintenance](../../../documents/.agents/skills/docs-maintenance/SKILL.md)
   cho phần rà tài liệu, kể cả khi kết luận không cần sửa.
3. Cập nhật tài liệu bị tác động trong cùng phần việc. Sửa hướng dẫn kỹ thuật và
   tổng hợp trạng thái từ bằng chứng; không đổi yêu cầu nghiệp vụ cho vừa code lỗi.
   Có yêu cầu chỉ push commit có sẵn hoặc chỉ một repo thì giữ giới hạn đó và báo phần thiếu.
4. Chạy kiểm tra theo phần thay đổi và `git diff --check`. Khi đã được phép commit,
   stage đúng file/hunk, đọc staged diff và chạy kiểm tra index theo repo.
5. Viết bản tổng hợp ngắn: **đã làm gì — bằng chứng/kiểm tra — tài liệu sửa/giữ/xóa
   và lý do — phần chưa làm/chưa kiểm chứng — repo/nhánh/commit**.
   Nêu tài liệu đã đối chiếu nếu không cần sửa. Cập nhật artifact hiện có khi hữu ích;
   mặc định tổng hợp trong phản hồi/PR description, không sinh nhật ký mỗi lần push.
6. Chỉ commit/push khi đã được yêu cầu. Kiểm tra lại remote trước push theo reference;
   sau tích hợp nội dung mới, rà lại tài liệu và chạy lại kiểm tra phần bị ảnh hưởng.

Đồng bộ tài liệu trước push là rà và sửa tài liệu liên quan đến thay đổi, không mặc định
tải Drive. Chỉ dùng `drive-sync` khi yêu cầu gồm nguồn ngoài đó; lỗi truy cập nguồn
không chứng minh tài liệu đã bị xóa hoặc bản local đã mới nhất.

## Bàn giao

Với yêu cầu công bố/merge toàn workspace, hoàn tất chuỗi: **sync nhánh → rà tài liệu
→ kiểm tra → push/merge repo con theo đích được giao → cập nhật gitlink → kiểm tra
và push/merge repo cha → xác minh live cuối cùng** bằng `submodule-sync`.
Đích là nhánh nào phải chọn rõ; checker offline hoặc lỗi mạng không đủ để báo hoàn tất.
Khi chỉ sync local, nêu con trỏ/nhánh còn chưa công bố, không tự mở rộng sang push.

Báo cập nhật được gì, tài liệu nào còn sai hoặc chưa có nguồn, kiểm tra thực sự chạy
và kết quả Git theo từng repo. Khi push, xác minh commit/ref đích từ phản hồi Git;
repo cha chỉ trỏ đến commit submodule đã được công bố theo phạm vi được giao.
Không báo hoàn tất công bố toàn workspace nếu mới push một repo con.

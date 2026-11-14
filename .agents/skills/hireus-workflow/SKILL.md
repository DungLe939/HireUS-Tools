---
name: hireus-workflow
description: Lập kế hoạch hoặc triển khai tính năng HireUS Tools qua nhiều repo, phối hợp yêu cầu nghiệp vụ, API backend và giao diện frontend.
---

# Phối hợp triển khai HireUS

Đọc [AGENTS.md](../../../AGENTS.md), hướng dẫn từng repo bị tác động và dùng
[project-navigator](../project-navigator/SKILL.md) để chọn nguồn mới nhất.
Dùng file/shell/connector của agent hiện tại; không yêu cầu một hãng hay subagent.

## Chốt phạm vi đủ để làm

Xác định phân hệ, hành vi cần hoàn thành, tiêu chí nghiệm thu và repo cần sửa.
Kiểm tra nhánh, code và thay đổi local ở từng repo theo
[team-sync](../team-sync/SKILL.md); tự cập nhật main của repo liên quan trước khi sửa,
giữ các thay đổi local. Việc chỉ lập plan riêng không kích hoạt tích hợp Git tự động.
Ghi nguồn và revision liên quan; hỏi chỉ phần thiếu ảnh hưởng hành vi/quyền/dữ liệu,
đồng thời tiếp tục công việc độc lập.

Đọc [bản đồ phân hệ](references/epics.md) để tìm các ranh giới cần đối chiếu.
Không coi danh sách đó là một đặc tả thay thế tài liệu nguồn.

## Phối hợp theo phần việc

1. **Nghiệp vụ:** truy vết tiêu chí nghiệm thu tới FR/BR/NFR hoặc yêu cầu trực tiếp.
   Sửa nhỏ làm trực tiếp; nếu cần artifacts tính năng lớn, dùng
   [Spec Kit](../../references/spec-kit.md), không tạo tài liệu chỉ để đủ thủ tục.
2. **Contract:** backend thiết kế giao diện từ yêu cầu đủ rõ và thống nhất phần FE cần.
   Contract nguồn nằm tại `backend/contracts/`; FE/spec dẫn tới đó và ghi phiên bản.
   Không dùng contract do FE tự tạo để thay quyết định backend.
3. **Backend:** dùng [nestjs-feature](../../../backend/.agents/skills/nestjs-feature/SKILL.md)
   và [rest-api-contract](../../../backend/.agents/skills/rest-api-contract/SKILL.md).
   Tách tính toán kiểm thử được khỏi nội dung AI không ổn định; bảo toàn dữ liệu khi provider lỗi.
4. **Frontend:** dùng [nextjs-feature](../../../frontend/.agents/skills/nextjs-feature/SKILL.md)
   và [rest-api-consumer](../../../frontend/.agents/skills/rest-api-consumer/SKILL.md).
   UI độc lập có thể làm trước; tích hợp dùng contract đủ chi tiết. Phân biệt rõ dữ liệu mẫu.
5. **Tài liệu:** trước bàn giao/push, dùng
   [docs-maintenance](../../../documents/.agents/skills/docs-maintenance/SKILL.md)
   để đối chiếu và sửa tài liệu liên quan, bỏ bản dẫn xuất lỗi thời có căn cứ.
   Yêu cầu nghiệp vụ chỉ đổi theo quyết định mới có nguồn; không chép toàn bộ yêu cầu
   sang nhiều repo. Hướng dẫn riêng từng repo vẫn phải dùng được khi mở độc lập.

## Hoàn tất

Kiểm tra nghiệp vụ trọng yếu, quyền dữ liệu, lỗi dịch vụ, trạng thái UI và luồng nối API.
Chạy lệnh phù hợp tại từng `AGENTS.md`; chỉ dùng reviewer riêng khi tác vụ cho phép.
Báo kết quả theo từng repo, contract/revision, kiểm tra đã chạy và phần còn thiếu.
Nêu tài liệu đã đối chiếu, sửa/giữ/xóa và lý do; không chỉ liệt kê tên file code.
Giữ nguyên nhánh thành viên; commit/push và cập nhật gitlink theo yêu cầu hiện tại.

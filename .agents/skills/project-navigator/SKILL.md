---
name: project-navigator
description: Đọc tổng quan HireUS Tools, tìm yêu cầu và hiện trạng ở frontend, backend, documents; dùng khi cần hiểu dự án hoặc tìm nguồn cho một đầu việc.
---

# Đọc và điều hướng dự án

Đọc [AGENTS.md](../../../AGENTS.md) và
[quy tắc nguồn](../../../documents/.agents/rules/source-of-truth.md).
Skill dùng được bằng cách đọc file trực tiếp trong agent đang chạy.

## Tìm đúng nguồn

- Nghiệp vụ hiện tại: [Requirements Analysis](../../../documents/docs/Week02/Submission/Requirements_Analysis.md).
  Chỉ đọc phần FR/BR/NFR, use case và prototype của phân hệ liên quan.
- Bối cảnh, nhân sự và kế hoạch ban đầu:
  [Proposal](../../../documents/docs/Week01/Submission/Project_Proposal.md).
- Bài nguồn và research giải thích quá trình hình thành yêu cầu; chúng không tự
  thay thế bản mới hơn. Với mâu thuẫn, ưu tiên phiên bản nội dung mới nhất theo quy tắc nguồn.
- Tiến độ: kiểm tra code, tests và artifacts trên nhánh thực tế.
  Timeline và metadata bài nộp không chứng minh đã triển khai, đã nộp hoặc được duyệt.
- Bài nộp: đọc template/thông báo của đợt tương ứng tại `documents/docs/Week*/Material/`.
  Với PDF hoặc hình, đọc cả nội dung trực quan cần cho câu hỏi.

## Đọc theo phạm vi

Liệt kê file trước, xác định bản trùng bằng nội dung khi đọc toàn repo.
Đọc cả file local bị ignore nếu người dùng yêu cầu toàn bộ tài liệu; ghi rõ trạng thái.
Không tự fetch, pull hoặc lấy Drive chỉ vì đang đọc local.

Sau khi định vị repo cần sửa, đọc `AGENTS.md`, `PROJECT_SOURCES.md` và đúng skill
của repo đó. Với tính năng qua nhiều repo, đọc [hireus-workflow](../hireus-workflow/SKILL.md).

Báo nội dung đã nắm, nguồn/phiên bản đang dùng, mâu thuẫn đã giải quyết và phần chưa đọc
hoặc chưa kiểm chứng. Không báo “đọc hết” nếu còn file không truy cập được.

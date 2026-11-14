---
name: submodule-sync
description: Kiểm tra và đồng bộ gitlink HireUS khi repo con đã cập nhật nhưng repo tổng còn ghim commit cũ; phối hợp công bố repo con, repo cha và xác minh remote cuối cùng.
---

# Đồng bộ repo con và con trỏ repo tổng

Đọc [AGENTS.md](../../../AGENTS.md), hướng dẫn repo bị tác động và
[team-sync](../team-sync/SKILL.md). Đọc trực tiếp bằng agent hiện tại; không cần
subagent hay cấu hình riêng một hãng. Thao tác sửa/push tuân theo phạm vi đã giao.

## Chọn đích và kiểm tra ba lớp

Xác định nhánh đích được yêu cầu: `main`, nhánh feature hoặc bản phát hành đã chọn.
Không gộp nhánh khác chỉ vì có commit mới. Giữ nhánh làm việc và thay đổi local;
đọc `.gitmodules` để tìm đúng submodule thay vì suy từ tên thư mục.

Chạy từ gốc workspace, thay `main` bằng đích đã xác định:

```bash
python3 .agents/scripts/check_submodules.py --target main --remote
```

Script chỉ đọc: dùng `ls-remote`, không fetch, merge, stage, commit hay push.
`--remote` cho phép truy vấn remote; khi chỉ rà offline, bỏ cờ đó, kết quả luôn
ghi chưa xác minh. Nếu commit repo cha chưa có trong local, fetch repo cha trong
phạm vi cập nhật được giao rồi chạy lại; không đoán gitlink từ cache cũ.

Đối chiếu **HEAD repo con ↔ tip nhánh đích trên remote ↔ gitlink repo cha**.
Gitlink được tách thành HEAD cha, index cha và nhánh cha đã công bố:
sync checkout, stage gitlink, commit cha và push/merge cha là các bước khác nhau.
Chi tiết cờ, mã thoát và giới hạn ở [hướng dẫn checker](references/checker.md).

## Khi được giao sync hoặc công bố

1. Nếu chỉ kiểm tra, báo lệch và dừng ở kiểm tra. Nếu sync nhánh, cập nhật đúng nhánh
   repo con, giữ file local; chưa coi gitlink cha là đã commit/push.
2. Khi công bố workspace, rà tài liệu/kiểm thử theo `team-sync`; push phần việc repo
   con. Nếu yêu cầu đích là `main`, merge được phép vào `main` và xác minh tip mới.
3. Checkout repo con phải tương ứng commit được chọn trước khi stage gitlink cha.
   Xem diff gitlink và nội dung commit được thêm/bỏ; không stage con trỏ tới một
   feature HEAD chưa nằm trong đích đã thống nhất.
4. Stage đúng gitlink liên quan khi được phép commit; giữ các thay đổi khác ngoài
   phạm vi. Chạy kiểm tra, commit/push repo cha và merge nếu yêu cầu gồm merge.
5. Chạy lại checker với nhánh đích công bố cuối. Tip remote thay đổi giữa các bước
   thì rà diff và xử lý trong phạm vi, không retry vô hạn hoặc tự force-push.

Chỉ báo **đã đồng bộ toàn workspace** khi các lớp khớp đích và xác minh live đạt.
Nếu intentionally pin phiên bản cũ, ghi đó là snapshot có chủ đích, không gọi là
đã theo tip mới nhất. Lỗi mạng/quyền hoặc repo chưa khởi tạo là chưa xác minh.
Commit khác tip có thể đã công bố ở nhánh khác: không kết luận chưa push từ mỗi
phép so sánh SHA; kiểm tra nhánh công bố có liên quan khi cần.

## Bàn giao

Nêu từng repo: SHA local, đích remote, gitlink cha local/index/remote, phần đã làm
và phần còn chờ. Push một repo con thành công không chứng minh repo cha đã cập nhật.
Với yêu cầu chỉ sync local, nói rõ những gitlink/nhánh chưa được công bố; không tự
commit/push để làm sạch báo cáo.

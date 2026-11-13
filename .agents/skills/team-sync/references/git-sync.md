# Cập nhật nhánh và công bố thay đổi

## Xác định đúng đích

Chạy tại từng repo cần làm: `git status --short --branch`, `git branch -vv`,
`git diff`, `git diff --cached` và kiểm tra file mới liên quan. Xem submodule từ
repo cha; nhánh/working tree/upstream của từng repo là độc lập.

Giữ nhánh `<thành-viên>/<epic>` đang làm. Lấy upstream đã xác minh làm đích cập nhật,
không tự lấy `main` hoặc nhánh có commit mới nhất. Nếu chưa có upstream, xác định
remote/nhánh đích từ yêu cầu và cấu hình; có nhiều đích không rõ mới hỏi phần đó.
Không tạo/chuyển nhánh để xử lý một yêu cầu chỉ cập nhật nhánh hiện tại.

## Fetch và tích hợp

- Fetch remote liên quan khi được yêu cầu cập nhật hoặc chuẩn bị push. Yêu cầu
  lấy mọi nhánh thì cập nhật remote-tracking refs của các repo trong phạm vi;
  không checkout, pull hay merge từng nhánh mới.
- Sau fetch, so sánh ahead/behind và diff so với đúng ref đích. Không lấy thời gian
  commit làm bằng chứng nội dung nào đúng về nghiệp vụ.
- Working tree sạch, nhánh chỉ behind: `git pull --ff-only` theo upstream đã xác minh
  hoặc fast-forward đúng ref vừa fetch. Chạy lại kiểm tra phần tích hợp tác động.
- Working tree bẩn: fetch vẫn được; không tự stash, reset/clean, ghi đè hoặc đưa
  thay đổi ngoài phạm vi vào commit. Khi đã được yêu cầu push, có thể commit phần
  việc liên quan trước khi tích hợp. Nếu thay đổi khác cản trở, dùng checkout/worktree
  tách biệt khi phù hợp hoặc hỏi cách giữ phần chưa rõ; tiếp tục phần độc lập.
- Nhánh phân kỳ: xem hai phía trước. Yêu cầu cập nhật/push cho phép xử lý merge
  thông thường với chính upstream đã xác minh, bảo toàn lịch sử. Không tự rebase
  nhánh đã chia sẻ, đổi upstream hoặc merge nhánh khác để vượt lỗi fast-forward.

## Conflict và push bị từ chối

Phân biệt remote đi trước với lỗi quyền, mạng, hook/check hoặc sai đích.
Không dùng force-push hay bỏ hook như cách sửa chung.

Với non-fast-forward, fetch lại, xem commit mới và tích hợp theo các điều kiện trên.
Giải quyết conflict cơ học và các nội dung có căn cứ rõ. Với tài liệu, đối chiếu
hai phía và nguồn mới nhất của chính nội dung đó; không chọn hàng loạt `ours/theirs`
hoặc bỏ quyết định local chỉ vì remote có timestamp mới hơn.
Chỉ hỏi điểm ảnh hưởng nghiệp vụ/quyền/dữ liệu chưa đủ căn cứ; không hỏi lại quyền
merge thông thường đã nằm trong yêu cầu cập nhật/push.

Sau merge, xem diff kết quả, sửa lại tài liệu bị tác động và chạy kiểm tra cần thiết;
không coi việc hết marker conflict là đã đúng. Thử push lại với ref đích rõ ràng.
Nếu remote lại chạy trước, báo tình trạng và chỉ thêm một vòng fetch/tích hợp/push;
sau đó dừng retry, giữ thay đổi và nêu lý do để tránh vòng lặp công bố vô hạn.
Lỗi quyền/mạng cần nguồn ngoài thì không giả vờ xử lý bằng sửa tài liệu.

## Nhiều repo và submodule

Commit/push các repo con liên quan trước, kiểm tra commit đích đã hiện trên remote,
rồi mới stage gitlink và push repo cha khi yêu cầu gồm công bố workspace.
Không dùng `git submodule update --remote` để thay pull nhánh thành viên: nó có thể
đổi checkout theo cấu hình khác và bỏ nhánh đang làm.

Không tự lấy mọi gitlink đang đổi vào commit cha; có thể chứa phần ngoài tác vụ.
Nếu chỉ một phần push thành công, báo repo/commit đã công bố và repo còn chờ;
không push repo cha trỏ đến commit chưa được công bố và không tự rollback phần đã push.
Khi push lần đầu, chỉ thiết lập upstream cho nhánh/remote được công bố sau khi thành công.

Không ghi `.env`, keys, cache sync hoặc bản incoming vào commit. Không cài global
Git hook/config hay gửi thông báo Jira/Drive/Slack chỉ từ yêu cầu push Git.

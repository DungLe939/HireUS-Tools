# Checker gitlink và nhánh đích

Chạy từ gốc workspace:

```bash
python3 .agents/scripts/check_submodules.py --target main
python3 .agents/scripts/check_submodules.py --target main --remote
python3 .agents/scripts/check_submodules.py --target main --remote --json
```

- `--target` bắt buộc: tên nhánh repo con, không tự mặc định `main`.
- `--parent-target` chọn nhánh công bố của repo cha nếu khác `--target`.
- `--remote-name` mặc định `origin`; `--root` chọn checkout repo cha khác.
- Không có `--remote`: chỉ dùng refs đã cache, không gọi mạng và không xác nhận mới nhất.
- Có `--remote`: đọc tip nhánh qua Git, không fetch hoặc đổi working tree/index/refs.
  Nếu object commit cha chưa có local, cần fetch riêng rồi chạy lại. Thông báo lỗi
  không in remote URL hoặc stderr có thể chứa thông tin riêng.

| Trường | Ý nghĩa |
| --- | --- |
| `local_head` | Checkout repo con trên máy |
| `target_head` | Tip nhánh đích repo con, live hoặc cache theo chế độ |
| `parent_head_pin` | Gitlink trong commit cha local |
| `parent_index_pin` | Gitlink stage 0 trong index, không phải đã commit |
| `parent_published_pin` | Gitlink trong tip nhánh đích cha, không phải working tree |
| `dirty` | Repo con còn thay đổi chưa commit |

Mã thoát **0**: live đã xác minh, các SHA khớp và repo con sạch.
Mã **1**: live đã đọc được nhưng có lệch hoặc repo con còn thay đổi.
Mã **2**: chưa xác minh đầy đủ (offline, lỗi mạng/quyền, thiếu checkout/ref/object).
Mã 1/2 là kết quả chẩn đoán, không tự sửa hoặc tự cấp quyền push.

Checker xét các submodule trực tiếp trong `.gitmodules` của checkout, không tự
đệ quy submodule lồng nhau, không liệt kê mọi nhánh cá nhân và không chứng minh
tests/CI đã đạt. Working tree cha có thể có thay đổi ngoài phạm vi; checker không
coi các file đó là lỗi gitlink. Các remote được đọc theo từng thời điểm, không phải
snapshot nguyên tử; chạy lại sau công bố và xử lý nếu có người cập nhật đồng thời.

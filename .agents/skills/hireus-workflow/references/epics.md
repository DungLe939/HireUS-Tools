# Bản đồ nghiệp vụ để bắt đầu một epic

Nguồn hiện tại:
[Requirements Analysis](../../../../documents/docs/Week02/Submission/Requirements_Analysis.md).
Chọn bản nội dung mới nhất theo
[quy tắc nguồn](../../../../documents/.agents/rules/source-of-truth.md).
Bảng này hướng dẫn cần đọc gì, không thay thế FR/BR/NFR hoặc công thức trong nguồn.

| Phân hệ | Đọc trong nguồn | Ranh giới cần kiểm tra khi triển khai |
| --- | --- | --- |
| CV Builder & SeekerBot | FR/BR/NFR/UC tiền tố CV, prototype CV | Tự điền ô trống, duyệt gợi ý, nội dung dùng chung giữa editor/mẫu/preview; bản sao thành tựu độc lập; GitHub công khai cần xác nhận đóng góp. |
| Voice Mock Interview | Tiền tố VMI | Quyền và kiểm tra mic, xác nhận STT, câu hỏi theo ngữ cảnh, scoring theo quy tắc hiện tại; giữ transcript và tạo lại báo cáo khi lỗi. |
| Job Matching & Skill Gap | Tiền tố JM | Xác nhận bóc tách, bằng chứng CV/JD, yêu cầu và/hoặc, công thức/trọng số/giới hạn điểm, snapshot lịch sử, lỗi gợi ý độc lập. |
| Job Tracking | Tiền tố JT | Theo dõi khác khả năng truy cập; thu thập khác lưu tin cá nhân; thời hạn có căn cứ; AI lọc tin khác matching CV; thao tác cá nhân không xóa dữ liệu dùng chung. |

Profile/Account là phần dùng chung cần phối hợp, chưa được tự suy ra schema từ
tên màn hình. Auth, field mapping và phương thức truy cập nguồn cần đủ quyết định
trước khi triển khai phần phụ thuộc.

Prototype chỉ minh họa; bản mới đã cắt bớt tutorial và song ngữ ở CV Builder.
Kiểm tra lại nguồn trước mỗi feature, không khôi phục chúng từ ảnh cũ.
Tương tự, không lấy số câu hỏi/thang điểm hiển thị trên ảnh phỏng vấn để thay BR mới.

## Cách chọn kiểm tra

Đối chiếu tiêu chí với dữ liệu mẫu có expected outcome từ nguồn:
CV bảo toàn nội dung và chỉ áp phần được duyệt; VMI giữ hỏi đáp khi lỗi;
JM kiểm tra biên công thức và dữ liệu ngoài CV; JT kiểm tra hạn, quyền và trạng thái nguồn.
Đo latency/chất lượng AI khi có integration thật; không dùng ảnh prototype làm kết quả test.

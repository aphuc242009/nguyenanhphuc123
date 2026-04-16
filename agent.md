Đọc toàn bộ project MiniQuiz và refactor phần nhiệm vụ chính của web theo kiến trúc chuẩn, logic rõ ràng, dễ bảo trì, không trộn UI với business logic.

Mục tiêu:
1. Chuẩn hóa toàn bộ logic nghiệp vụ chính của web.
2. Tách rõ frontend, router/controller, service/business logic, repository/data access.
3. Đảm bảo code sạch, đúng trách nhiệm, dễ debug, dễ mở rộng.
4. Không phá phần auth đã sửa ổn.

Yêu cầu bắt buộc:

A. Xác định nghiệp vụ chính của web
- phân tích project để xác định các tính năng cốt lõi
- ví dụ: tạo quiz, chỉnh sửa quiz, làm quiz, nộp bài, chấm điểm, xem kết quả, dashboard
- liệt kê rõ từng luồng nghiệp vụ chính trước khi refactor

B. Refactor backend theo tầng
- router chỉ nhận request, validate cơ bản, gọi service, trả response
- service chứa toàn bộ business logic
- repository chứa truy cập dữ liệu
- model/schema tách riêng rõ ràng
- không để router ôm toàn bộ logic

C. Chuẩn hóa business rule
- viết rõ mọi điều kiện nghiệp vụ:
  - ai được tạo/sửa/xóa
  - quiz ở trạng thái nào thì được làm
  - khi nào được nộp bài
  - khi nào được chấm điểm
  - ai được xem kết quả/thống kê
- không để rule rải rác nhiều nơi

D. Chuẩn hóa trạng thái dữ liệu
- dùng status/state rõ ràng cho thực thể chính
- loại bỏ logic chồng chéo kiểu vừa is_active vừa status vừa published_at nếu không cần
- mọi trạng thái phải có quy tắc chuyển đổi rõ

E. Chuẩn hóa database interaction
- tách query ra repository
- thêm transaction cho nghiệp vụ nhiều bước
- tránh duplicate query và side effects khó kiểm soát
- normalize dữ liệu đầu vào nếu cần

F. Chuẩn hóa response và error handling
- lỗi phải đúng bản chất:
  - not found
  - forbidden
  - invalid state
  - validation error
  - conflict
- message rõ ràng, dễ debug

G. Kiểm tra frontend
- frontend chỉ giữ UI state và gọi API
- không tự giữ business logic quan trọng mà backend phải quyết định
- form/action chính phải map đúng API response

H. Tự test toàn bộ luồng chính
- tạo mới
- chỉnh sửa
- submit
- xem kết quả
- dashboard
- lỗi quyền truy cập
- lỗi trạng thái không hợp lệ

I. Kết quả đầu ra bắt buộc
1. danh sách nghiệp vụ chính của web
2. file đã refactor
3. logic mới của từng luồng
4. các bug logic đã sửa
5. các test case đã kiểm
6. cách chạy lại project

Bắt đầu bằng việc:
- phân tích nghiệp vụ cốt lõi của MiniQuiz
- vẽ lại luồng logic hiện tại
- tìm chỗ code đang trộn UI/router/service/repository
- refactor cho chuẩn production
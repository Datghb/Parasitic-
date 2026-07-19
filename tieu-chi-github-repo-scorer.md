# Tiêu chí AI GitHub Repo Scorer (MECE + Validation Chain)

Mỗi nhóm tiêu chí độc lập (Mutually Exclusive), gộp lại bao phủ toàn bộ (Collectively Exhaustive).
Mỗi nhóm áp dụng chuỗi kiểm chứng: **Tồn tại → Chất lượng → Nhất quán → Xác thực → Cờ đỏ trừ điểm**.

## 1. Mã nguồn

### 1.1. Tồn tại
- Repo chứa mã nguồn thực, không rỗng
- Ngôn ngữ chính được khai báo rõ ràng
- Có file cấu hình dependency (package.json, requirements.txt)
- Có .gitignore phù hợp với ngôn ngữ
- Entry point (main, index) xác định được

### 1.2. Chất lượng
- Tuân thủ coding convention của ngôn ngữ
- Đặt tên biến, hàm rõ nghĩa, nhất quán
- Hàm ngắn gọn, đơn trách nhiệm (SRP)
- Không lặp mã (DRY), không dead code
- Xử lý lỗi và exception đầy đủ
- Không hardcode secret, API key, mật khẩu
- Validate input, sanitize dữ liệu người dùng
- Không dùng dependency lỗi thời, có lỗ hổng
- Độ phức tạp cyclomatic ở mức chấp nhận
- Comment giải thích logic phức tạp, không thừa
- Type hint / typing đầy đủ (nếu hỗ trợ)

### 1.3. Nhất quán
- Cấu trúc thư mục logic, phân tầng rõ
- Style code đồng nhất toàn bộ repo
- Có linter, formatter được cấu hình
- Naming convention thống nhất giữa các module
- Import được tổ chức gọn, không vòng lặp

### 1.4. Xác thực
- Có unit test, coverage đo được
- Test chạy pass trên CI
- Có integration test cho luồng chính
- Commit history sạch, message có ý nghĩa
- Không commit file build, binary, node_modules

### 1.5. Cờ đỏ trừ điểm
- Code copy-paste nguyên từ tutorial, boilerplate
- File nghìn dòng, god class, god function
- Secret, token bị lộ trong commit history
- Test giả, test rỗng chỉ để pass
- Commit dồn cục "final", "fix", "update" vô nghĩa
- Nhiều file trùng lặp: copy1, backup, old
- Code comment tiếng lẫn lộn, debug print sót
- Dependency thừa không dùng đến

## 2. Deployment

### 2.1. Tồn tại
- Có script hoặc file cấu hình deploy
- Có Dockerfile hoặc container hóa tương đương
- Khai báo biến môi trường mẫu (.env.example)
- Có docker-compose cho local development

### 2.2. Chất lượng
- CI/CD pipeline tự động hóa build, test
- Build tái lập được (reproducible), version lock
- Tách biệt config theo môi trường (dev/prod)
- Dockerfile tối ưu: multi-stage, layer cache
- Image không chạy quyền root, gọn nhẹ
- Có migration script cho database schema

### 2.3. Nhất quán
- Pipeline đồng bộ với cấu trúc mã nguồn
- Tài liệu deploy khớp script thực tế
- Port, biến môi trường thống nhất mọi nơi

### 2.4. Xác thực
- Có link demo hoặc production đang chạy
- Badge CI/CD hiển thị trạng thái pass
- Có monitoring, logging, health check endpoint
- Có chiến lược rollback, backup dữ liệu
- HTTPS, security header được cấu hình

### 2.5. Cờ đỏ trừ điểm
- Link demo chết, trả lỗi 404/500
- CI đỏ liên tục, bị tắt bỏ
- .env thật bị commit lên repo
- Build local thất bại theo hướng dẫn
- Dockerfile lỗi, image không build được
- Hardcode localhost, đường dẫn máy cá nhân
- Không có cách chạy thử nào khả thi

## 3. Kiến trúc

### 3.1. Tồn tại
- Có sơ đồ hoặc mô tả kiến trúc
- Xác định rõ các thành phần hệ thống
- Nêu lý do chọn công nghệ (tech stack)

### 3.2. Chất lượng
- Phân tách module, layer hợp lý
- Áp dụng design pattern phù hợp bài toán
- Khả năng mở rộng (scalability) được cân nhắc
- Tách biệt business logic khỏi framework
- Database schema chuẩn hóa, index hợp lý
- API thiết kế RESTful hoặc chuẩn tương đương
- Không over-engineering so với quy mô bài toán

### 3.3. Nhất quán
- Mã nguồn phản ánh đúng kiến trúc mô tả
- Luồng dữ liệu nhất quán giữa các module
- Dependency giữa layer đúng chiều, không ngược

### 3.4. Xác thực (AI-native)
- Tích hợp LLM/AI làm lõi nghiệp vụ
- AI giải quyết vấn đề thực, không gắn trang trí
- Có prompt engineering, orchestration rõ ràng
- Prompt tách khỏi code, dễ chỉnh sửa
- Xử lý context, memory, tool-use bài bản
- Có RAG, embedding nếu bài toán cần
- Có cơ chế đánh giá (eval) đầu ra AI
- Xử lý lỗi khi model trả kết quả sai
- Kiểm soát chi phí, latency gọi model
- Có fallback khi API model bị lỗi
- Guardrail chống prompt injection, output độc hại
- Streaming response nếu trải nghiệm cần

### 3.5. Cờ đỏ trừ điểm
- AI chỉ là wrapper gọi API thô
- Prompt hardcode rải rác khắp codebase
- Không xử lý khi model trả rác
- Gọi model lặp vô hạn, không giới hạn
- Kiến trúc mô tả một đằng, code một nẻo
- Monolith rối, module phụ thuộc chằng chịt
- Chọn công nghệ theo trend, không lý do

## 4. Tài liệu kỹ thuật

### 4.1. Tồn tại
- README có mặt tại thư mục gốc
- Có LICENSE, CONTRIBUTING, CHANGELOG
- Có tài liệu kiến trúc riêng (docs/, wiki)

### 4.2. Chất lượng
- Mô tả vấn đề, giải pháp rõ ràng
- Hướng dẫn cài đặt từng bước cụ thể
- Liệt kê prerequisite: phiên bản, công cụ cần
- Có ví dụ sử dụng, screenshot, demo
- Tài liệu API endpoint đầy đủ (nếu có)
- Giải thích cấu trúc thư mục dự án
- Nêu giới hạn đã biết (known limitations)
- Chính tả, ngữ pháp, trình bày chỉn chu

### 4.3. Nhất quán
- Hướng dẫn khớp với mã nguồn hiện tại
- Version tài liệu đồng bộ version code
- Tên lệnh, đường dẫn trong docs chính xác

### 4.4. Xác thực
- Người mới clone chạy được theo README
- Link trong tài liệu không bị hỏng
- Ảnh, diagram hiển thị đúng, không vỡ

### 4.5. Cờ đỏ trừ điểm
- README mặc định từ template chưa sửa
- README một dòng hoặc trống rỗng
- Docs viết bởi AI chung chung, sáo rỗng
- Hướng dẫn cài đặt sai, thiếu bước
- Screenshot cũ không khớp giao diện hiện tại
- Badge giả, thông tin phóng đại sai thực tế
- Không có license, mập mờ bản quyền

## 5. Độ hoàn thiện

### 5.1. Tồn tại
- Tính năng cốt lõi đã được triển khai
- Có release hoặc tag phiên bản
- Luồng người dùng chính hoàn chỉnh end-to-end

### 5.2. Chất lượng
- Tính năng hoạt động đúng như mô tả
- UX/UI hoàn chỉnh, không placeholder
- Edge case được xử lý hợp lý
- Thông báo lỗi thân thiện, dễ hiểu
- Loading state, empty state được chăm chút
- Responsive hoặc tương thích thiết bị mục tiêu
- Hiệu năng chấp nhận được với dữ liệu thật

### 5.3. Nhất quán
- Roadmap, issue phản ánh tiến độ thực
- Không còn TODO, FIXME nghiêm trọng
- Tính năng quảng bá đều dùng được thật

### 5.4. Xác thực
- Repo được maintain, commit gần đây
- Issue, PR được phản hồi tích cực
- Có người dùng thực, star, fork tự nhiên
- Lịch sử phát triển liên tục, không dồn dập

### 5.5. Cờ đỏ trừ điểm
- Nút bấm chết, tính năng nửa vời
- Crash khi nhập dữ liệu bất thường
- Toàn bộ commit trong một ngày (nghi copy)
- Star, fork ảo, tăng bất thường
- Repo bỏ hoang, issue chất đống không đáp
- Demo dùng dữ liệu giả che chức năng thiếu
- Khác biệt lớn giữa quảng cáo và thực tế

---

## Nhóm xuyên suốt: Tính xác thực & liêm chính (cross-cutting)

Áp dụng chồng lên cả 5 nhóm trên khi nghi ngờ:

- Code do chính tác giả viết, hiểu được
- Lịch sử commit thể hiện quá trình phát triển
- Không fork rồi đổi tên nhận của mình
- Ghi công (attribution) đầy đủ cho mã mượn
- Tác giả trả lời được câu hỏi về code
- Đóng góp phân bổ hợp lý giữa thành viên

---

## Gợi ý trọng số chấm điểm

| Nhóm | Trọng số | Cờ đỏ tối đa trừ |
|---|---|---|
| Mã nguồn | 25% | -15% |
| Deployment | 15% | -10% |
| Kiến trúc (AI-native) | 25% | -15% |
| Tài liệu kỹ thuật | 15% | -10% |
| Độ hoàn thiện | 20% | -15% |

**Quy tắc chấm:** điểm dương theo tiêu chí đạt; cờ đỏ trừ trực tiếp; vi phạm liêm chính có thể loại thẳng.

# Kịch bản demo end-to-end

Thời lượng mục tiêu: 4–5 phút.

## Chuẩn bị

1. Kiểm tra `https://api.theoria-lab.io.vn/health` trả `{"status":"ok"}`.
2. Mở `https://diachung.dpdns.org`.
3. Xác nhận góc trên hiển thị `Dữ liệu API trực tiếp`.
4. Chuẩn bị nội dung:

   > Ngân hàng An Việt sắp phá sản, mọi người phải rút tiền ngay ngày mai.

## Cảnh 1 — Tổng quan thị trường (45 giây)

- Mở **Tổng quan thị trường**.
- Chỉ ra KPI, biểu đồ rủi ro, phân bổ nền tảng và heatmap.
- Đổi `24 giờ`, `7 ngày`, `30 ngày`.
- Nhấn mạnh toàn bộ biểu đồ tính từ cùng dữ liệu `/api/queue`.

Kỳ vọng: số liệu và hình dạng biểu đồ thay đổi theo bộ lọc.

## Cảnh 2 — Quét mạng xã hội (60 giây)

- Bấm **Quét MXH**.
- Quan sát trạng thái `Đang quét MXH…`.
- Chờ toast kết quả.
- Hệ thống tự gọi lại hàng đợi và cập nhật dashboard.

Kỳ vọng:

- Có API key/crawler: toast báo thu thập trực tiếp.
- Không có key hoặc nguồn chặn: toast nói rõ dùng dữ liệu dự phòng.
- Không được hiển thị thành công giả hoặc làm ứng dụng crash.

## Cảnh 3 — Nhập nội dung thủ công (60 giây)

- Mở **Hàng đợi giám sát** → **Nhập nội dung mới**.
- Chọn `Bài viết` hoặc `Bình luận`.
- Dán nội dung mẫu, chọn Facebook, lưu.
- Có thể đổi sang tab tải CSV/JSON/TXT để minh họa nhập hàng loạt.

Kỳ vọng: hồ sơ mới xuất hiện với trạng thái `Mới` và nhãn an toàn
`Cần kiểm chứng`.

## Cảnh 4 — Rà soát hồ sơ (60 giây)

- Bấm vào hồ sơ ưu tiên cao.
- Trình bày nội dung gốc, claim, kết quả AI và lý do.
- Chỉ ra điều/khoản/điểm, chủ thể, mức phạt và nguồn chính thức.
- Đổi trạng thái `Mới → Đang xử lý → Đã xử lý`.

Thông điệp nói: “AI đề xuất và giải thích; chuyên viên là người quyết định.”

## Cảnh 5 — Tầng kiểm chứng (45 giây)

- Mở **Tầng kiểm chứng**.
- Chọn một study case và so hành vi thực tế với kết quả mong đợi.
- Nêu guardrail: không có nguồn không đồng nghĩa nội dung sai.

## API dự phòng khi demo UI gặp sự cố

```bash
curl https://api.theoria-lab.io.vn/health

curl -X POST https://api.theoria-lab.io.vn/api/qa \
  -H "Content-Type: application/json" \
  -d '{"question":"Cá nhân đăng tin giả bị phạt bao nhiêu?"}'

curl -X POST https://api.theoria-lab.io.vn/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"keywords":["tin giả","nghị định 174"],"max_posts_per_platform":5}'
```

## Checklist kết thúc

- [ ] Dashboard lấy dữ liệu API.
- [ ] Nút crawl có loading, kết quả và refresh.
- [ ] Không khẳng định vi phạm tự động.
- [ ] Mở được nguồn chính thức.
- [ ] Trạng thái hồ sơ thay đổi được.
- [ ] Frontend và Backend production cùng hoạt động.

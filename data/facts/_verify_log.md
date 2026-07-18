# Verify log — data/facts/fact_references.json

Ghi lại ai verify, verify bằng nguồn nào, lúc nào — để trả lời được ngay nếu bị hỏi ngược lúc demo.

**Người verify:** P2 (qua trợ lý AI, WebSearch + WebFetch trực tiếp vào nguồn chính)
**Lúc verify:** 2026-07-18 (cùng thời điểm soạn `fact_references.json`)

---

## fr-001 — Nghị quyết 202/2025/QH15 (34 tỉnh thành)

- **Số hiệu + ngày ban hành:** Nghị quyết số 202/2025/QH15, Quốc hội thông qua 12/6/2025 (461/465 đại biểu tán thành).
- **Nội dung:** cả nước 34 đơn vị hành chính cấp tỉnh (28 tỉnh + 6 thành phố), hiệu lực từ 01/7/2025.
- **Cách verify:** WebSearch "Nghị quyết Quốc hội sáp nhập đơn vị hành chính cấp tỉnh 2025 34 tỉnh thành chính thức" → khớp nhiều nguồn độc lập (baochinhphu.vn, xaydungchinhsach.chinhphu.vn, thuvienphapluat.vn, vass.gov.vn) cùng nói 1 số hiệu, 1 ngày, 1 con số.
- **URL đã click thật:** https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-quyet-so-202-2025-qh15-ve-sap-xep-don-vi-hanh-chinh-cap-tinh-119250612174148722.htm

## fr-002 — Luật 72/2025/QH15 (mô hình 2 cấp)

- **Số hiệu + ngày ban hành:** Luật số 72/2025/QH15, Quốc hội thông qua 16/6/2025.
- **Nội dung:** bỏ cấp huyện, còn 2 cấp chính quyền địa phương (tỉnh + xã/phường/đặc khu).
- **Cách verify:** WebSearch "Luật Tổ chức chính quyền địa phương số 72/2025/QH15" → khớp nhiều nguồn (xaydungchinhsach.chinhphu.vn, thuvienphapluat.vn, tulieuvankien.dangcongsan.vn).
- **URL đã click thật:** https://xaydungchinhsach.chinhphu.vn/toan-van-luat-so-72-2025-qh15-to-chuc-chinh-quyen-dia-phuong-119250618161434371.htm

## fr-003 — Bộ Nội vụ bác bỏ tin "còn 16 tỉnh"

- **Sự kiện có 2 đợt** (quan trọng — dễ nhầm là 1 sự kiện):
  - Đợt 1: 17/11/2025, ông Phan Trung Tuấn (Cục trưởng Cục Chính quyền địa phương, Bộ Nội vụ) bác bỏ trên baochinhphu.vn.
  - Đợt 2 (tin đồn tái phát): 04/3/2026, Bộ Nội vụ bác bỏ lại, đưa tin qua Tuổi Trẻ (fact-014).
- **Cách verify:** WebFetch trực tiếp cả 2 bài (baochinhphu.vn cho đợt 1, tuoitre.vn cho đợt 2) — xác nhận ngày đăng chính xác qua nội dung bài, không suy đoán từ slug URL.
- **Lỗi đã tự sửa trong quá trình verify:** ban đầu gán nhầm ngày đợt 2 = ngày đợt 1 (17/11/2025) — phát hiện và sửa lại thành 04/3/2026 sau khi fetch trực tiếp.

## fr-004 — Thanh Hóa bác bỏ tin "còn 58 xã"

- **Ngày:** 04/6/2026, Ban Tuyên giáo và Dân vận Tỉnh ủy Thanh Hóa bác bỏ qua Dân Trí.
- **Nguồn phát tán tin giả:** Facebook cá nhân "Hoàng Dũng".
- **Cách verify:** WebFetch trực tiếp bài Dân Trí + WebFetch chéo bài VietnamNet cùng chủ đề, cùng ngày — 2 nguồn độc lập khớp nhau.
- **URL đã click thật:** https://dantri.com.vn/noi-vu/bac-bo-tin-don-thanh-hoa-chi-con-58-xa-phuong-20260604170436471.htm

---

## Case xử phạt thật (study_cases.json)

- **sc-003** (Tuổi Trẻ, 06/5/2025, 7.5tr) — case chung về "sáp nhập tỉnh", KHÔNG khớp trực tiếp variant tin đồn nào đang track. Giữ lại vì vẫn là case thật, dùng làm case phụ.
- **sc-004** (Báo Gia Lai, 05/3/2026, 7.5tr) — **case chính**, khớp trực tiếp tin đồn "còn 16 tỉnh" (fr-003). Xảy ra đúng 1 ngày sau đợt bác bỏ lần 2 của Bộ Nội vụ (04/3/2026) — timeline chặt, tốt cho demo.
- Đã tìm nhưng KHÔNG dùng: vụ Điền Lư (Thanh Hóa, 10/6/2026, N.V.H, 7.5tr) — nội dung thực tế là "xúc phạm lực lượng công an", không liên quan tin đồn sáp nhập, dù cùng địa bàn Thanh Hóa. Không ép vào case này để tránh gán sai chủ đề.
- Chưa tìm thấy case xử phạt thật nào khớp trực tiếp tin đồn "Thanh Hóa còn 58 xã" (fr-004) — đây là khoảng trống đã biết, không phải "chưa tìm thấy = không có" (theo nguyên tắc 1 của domain brief §5b).

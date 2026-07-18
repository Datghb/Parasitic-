# 16 — Handoff P2 → P1: data domain "Giám sát tin đồn sáp nhập ĐVHC" đã sẵn sàng

**Từ:** P2 (Data Specialist)
**Đến:** P1 (Engine Architect)
**Bối cảnh:** Team đổi hướng sang domain "Giám sát tin đồn liên quan sắp xếp đơn vị hành chính (sáp nhập tỉnh/xã)" — xem `.kilo/plans/1784345997023-scope-admin-merger-rumors.md`. P2 đã hoàn thành toàn bộ data phần mình phụ trách; các mục dưới đây cần P1 xác nhận/xử lý khi build `FactRef` + engine mới.

---

## 1. File đã tạo/cập nhật (P2.1 → P2.6)

| File | Trạng thái | Ghi chú |
|---|---|---|
| `data/facts/fact_references.json` | **Mới** — 4 FactRef ground truth | Schema tự thiết kế (xem mục 2), P1 cần xác nhận trước khi build dataclass |
| `data/facts/facts_corpus.json` | Cập nhật — +5 fact (fact-013 → fact-017), giữ nguyên 12 fact cũ | Đã verify `classify_tier()` cho toàn bộ 17 fact, 0 mismatch |
| `data/study_cases/study_cases.json` | Cập nhật — +1 case thật (sc-003) | Case Tuổi Trẻ 06/5/2025, 7.5tr, điểm a khoản 1 Điều 101 NĐ15 → khớp Điều 95 NĐ174 khi diff |
| `data/fixtures/comments_batch_1/2/3.json` | Viết lại toàn bộ 45 câu | Batch 1 = đúng, Batch 2 = hiểu lầm (khẳng định sai chắc nịch), Batch 3 = cần kiểm chứng (câu hỏi mơ hồ) |
| `backend/eval/cases_dvhc_draft.json` | **Mới, DRAFT** — 10 eval case domain ĐVHC | **CHƯA đổi tên thành `cases.json`** — xem mục 4 |

Tất cả JSON đã valid, 315 test hiện tại (`backend/tests/`) vẫn xanh (data mới không phá gì vì chưa có code nào consume các file này).

## 2. Schema `FactRef` (draft — P2 tự thiết kế, cần P1 xác nhận)

```json
{
  "id": "fr-003",
  "chu_de": "tin_don_tiep_tuc_sap_nhap_con_16_tinh",
  "tu_khoa": ["sap nhap tiep", "16 tinh", "giam con 16", ...],
  "tuyen_bo_dung": "Khong co chu truong tiep tuc sap nhap... (câu sự thật chuẩn)",
  "bien_the_tin_don_sai": ["sap nhap tiep tuc con 16 tinh thanh pho", "34 tinh sap giam xuong 16", ...],
  "nguon": "Bo Noi vu (qua Cong TTDT Chinh phu)",
  "ngay_hieu_luc": "2025-11-17",
  "url": "https://...",
  "ghi_chu": "..."
}
```

- `tu_khoa`: dùng cho `match_fact_ref()` (BM25, tương tự `match_hanh_vi()` hiện có).
- `bien_the_tin_don_sai`: các cách diễn đạt SAI thường gặp — dùng cho `_is_negation_of()`/`_contradicts()`. Đã cố ý viết khớp gần nguyên văn với câu trong `comments_batch_2.json` để dễ test.
- Nếu P1 muốn đổi tên field (vd `su_that` thay vì `tuyen_bo_dung`) — báo lại, P2 sửa JSON theo, không sao.

4 FactRef hiện có: `fr-001` (34 tỉnh chính thức), `fr-002` (mô hình 2 cấp, bỏ huyện), `fr-003` (bác bỏ tin "còn 16 tỉnh"), `fr-004` (bác bỏ tin "Thanh Hóa còn 58 xã"). Cả 4 đều có ít nhất 2 câu trong `comments_batch_2.json` mâu thuẫn trực tiếp để test negation.

## 3. Gap quan trọng — CẦN XỬ LÝ trước khi wire facts_corpus.json vào pipeline

`data/facts/facts_corpus.json` (cả 12 entry cũ lẫn 5 entry P2 vừa thêm) **không có field `la_bac_bo`/`la_xac_nhan`** mà `SearchDoc`/`apply_fusion_rules()` trong `source_classifier.py` bắt buộc cần (mặc định `False` nếu thiếu).

→ Nếu dùng thẳng `facts_corpus.json` làm `search_results` đầu vào cho `xac_thuc_nguon()`, **mọi fact sẽ luôn bị coi là không xác nhận cũng không bác bỏ**, bất kể tier đúng cỡ nào — kết quả luôn ra `chua_tim_thay_nguon` dù data có đúng tài liệu Tier 0 khớp claim. Cần thêm bước gắn `la_bac_bo`/`la_xac_nhan` (thủ công theo từng fact, hoặc suy luận từ `tieu_de`) khi viết loader cho file này.

## 4. Vì sao chưa đổi `cases_dvhc_draft.json` thành `cases.json`

`backend/eval/cases.json` hiện tại là eval gate **đang sống** cho engine cũ (`phan_loai_claim` dựa trên chủ thể + số tiền), được `eval/smoke.py` và `test_eval_cases.py` chạy thật và đang pass. 10 case ĐVHC mới **không chạy được với engine hiện tại** (chưa có `match_fact_ref`/`_contradicts`), nên P2 để riêng thành `cases_dvhc_draft.json` — không đụng tới file cũ, tránh phá eval gate đang xanh.

**Khi P1 xong P1.6 (refactor `phan_loai_claim`):** đổi tên `cases_dvhc_draft.json` → merge vào `cases.json` (hoặc thay thế hẳn nếu domain cũ bị bỏ), chạy `python eval/smoke.py`, target pass ≥ 9/10 theo Gate G1 trong plan.

## 5. Việc P2 sẽ làm tiếp khi P1 xong

- Chạy lại toàn bộ 45 comment qua engine thật, đối chiếu nhãn ra có đúng kỳ vọng (đúng/hiểu lầm/cần kiểm chứng) như thiết kế không — hiện tại mới verify được bằng mắt + `classify_tier()`, chưa chạy qua `match_fact_ref()` thật vì hàm chưa tồn tại.
- P2.8: verify lại `sc-004.expected_he_thong` sau khi engine thật chạy case này (hiện đối chiếu thủ công với Điều 4 khoản 3 NĐ174, số liệu khớp nhưng chưa qua code).
- Sau khi engine thật chạy được: tính confusion matrix + macro-F1 + Recall("hieu_lam") trên 45 comment, đề xuất thêm điều kiện `macro_f1 ≥ 0.7` và `Recall("hieu_lam") ≥ 0.8` vào Gate G2 (không chỉ "JSON valid, load được" như hiện tại).

## 6. Cập nhật sau lượt review lần 2 (đối chiếu lại theo checklist P2.1→P2.8 chi tiết)

- **`data/facts/_verify_log.md`** (mới) — ghi lại ai/khi nào/verify bằng nguồn nào cho từng FactRef, kể cả 1 lỗi đã tự phát hiện và sửa (fr-003 ban đầu gán nhầm ngày đợt tin đồn tái phát lần 2).
- **`sc-004`** (mới, `study_cases.json`) — case xử phạt thật **khớp trực tiếp** tin đồn "còn 16 tỉnh" (fr-003): cá nhân ở Phú Thọ bị phạt 7.5tr ngày 05/3/2026, chỉ 1 ngày sau khi Bộ Nội vụ bác bỏ lại (04/3/2026, fact-014). Đây mới là case chính cho demo — `sc-003` (Tuổi Trẻ, case sáp nhập tỉnh chung chung, không khớp variant tin đồn nào) giữ lại làm case phụ. `cases_dvhc_draft.json` (ev-dvhc-09) đã trỏ sang `sc-004`.
- **`comments_batch_2.json`** viết lại: chia 3 tầng khó (5 câu dùng đúng từ khóa / 5 câu diễn đạt vòng không dùng đúng cụm / 5 câu teencode+emoji), và thêm field `loai_loi: "fact" | "luat"` phân biệt lỗi sai sự kiện (mâu thuẫn FactRef) với lỗi sai luật (nhầm mức phạt tổ chức/cá nhân) — 12 câu `fact`, 3 câu `luat`. P1 lưu ý field này khi thiết kế eval để biết đang test tầng nào (`match_fact_ref` hay `match_hanh_vi`/`phan_loai_claim`).
- Chưa làm (do cần engine thật): confusion matrix, macro-F1, Recall("hieu_lam") — xem mục 5.

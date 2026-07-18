# 15 — Bug report: `dynamic_search_gemini()` không chạy được với `google-genai` 2.6.0

**Từ:** A1 (Engine Architect) — phát hiện khi chạy thử app end-to-end với API key thật
**Đến:** A2 (Verification Specialist)
**File bị ảnh hưởng:** `backend/legal_radar/source_search.py` (không sửa, chỉ báo)

---

## Bối cảnh phát hiện

Đang chạy thử toàn bộ app (`backend` + `frontend`) sau khi điền API key thật vào `backend/.env`. Gọi thử `dynamic_search_gemini()` trực tiếp để xác nhận Google Search grounding hoạt động — gặp lỗi ngay cả khi key hợp lệ.

## Bug #1 (đã tự sửa, không cần A2 làm gì): thiếu biến env `GOOGLE_API_KEY`

`source_search.py:21` đọc `GOOGLE_API_KEY_1` hoặc `GOOGLE_API_KEY`, nhưng `backend/.env.example` chỉ khai báo `GEMINI_API_KEY` (dùng cho `providers.py`, LLM extract). Cùng 1 key Google AI Studio dùng được cho cả hai, chỉ khác tên biến — nên `.env` điền `GEMINI_API_KEY` xong vẫn báo `ValueError: No Gemini API key provided`.

→ Đã tự thêm dòng `GOOGLE_API_KEY=<cùng giá trị>` vào `backend/.env` (không phải `.env.example`, chỉ máy A1). **A2 nên cập nhật `backend/.env.example` thêm dòng `GOOGLE_API_KEY=` để người sau không bị vướng lại.**

## Bug #2 (cần A2 sửa): `generate_content()` không nhận `tools=` trực tiếp

`source_search.py:28-39`:

```python
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"""...""",
    tools={"google_search": {}},   # ← lỗi ở đây
)
```

Với `google-genai==2.6.0` (bản đang cài trong `backend`, theo `pyproject.toml`/lockfile hiện tại), gọi thế này bắn:

```
TypeError: Models.generate_content() got an unexpected keyword argument 'tools'
```

SDK bản này yêu cầu truyền `tools` qua `config=types.GenerateContentConfig(...)`, không phải kwarg rời. Cách sửa (theo doc chính thức `google-genai` cho Google Search grounding):

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"""...""",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    ),
)
```

## Cách verify sau khi sửa

Không có test nào cover hàm này hiện tại (live API call, cần key thật nên không nằm trong `pytest` CI) — đây cũng là lỗ hổng nên vá: ít nhất 1 test `@pytest.mark.integration` có skip-if-no-key để bắt được lỗi kiểu này sớm hơn, thay vì phải chạy thử app mới phát hiện.

Test thủ công nhanh:

```bash
cd backend
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from legal_radar.source_search import dynamic_search_gemini
results = dynamic_search_gemini(['SBV', 'bác bỏ', 'tin đồn'], '2026-01-01')
print(len(results), results[:1])
"
```

Kỳ vọng: không raise `TypeError`, trả về list (có thể rỗng nếu Gemini không tìm thấy nguồn liên quan).

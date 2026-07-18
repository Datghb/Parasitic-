from __future__ import annotations

import json
import logging
import os

import requests as http_requests

logger = logging.getLogger(__name__)


def _get_tokenrouter_config() -> tuple[str, str, str]:
    api_key = os.environ.get("TOKENROUTER_API_KEY", "")
    base_url = os.environ.get("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1").rstrip("/")
    model = os.environ.get("TOKENROUTER_MODEL", "google/gemini-3-flash-preview")
    return api_key, base_url, model


def dynamic_search_gemini(
    claim_keywords: list[str],
    thoi_gian_claim: str,
    api_key: str | None = None,
) -> list[dict]:
    tr_key, base_url, model = _get_tokenrouter_config()
    key = api_key or tr_key
    if not key:
        logger.warning("No TOKENROUTER_API_KEY set — skipping source search")
        return []

    query = " ".join(claim_keywords)
    prompt = (
        f'Tìm kiếm thông tin chính thức liên quan đến: "{query}"\n\n'
        "Chỉ trả về các nguồn tin chính thức từ cơ quan nhà nước, báo chí chính thống Việt Nam.\n"
        "Với mỗi nguồn tìm thấy, trả về JSON array với format:\n"
        '[{"tieu_de": "...", "nguon": "...", "url": "...", "ngay_dang": "YYYY-MM-DD", '
        '"noi_dung_tom_tat": "1-2 câu", "la_bac_bo": true/false, "la_xac_nhan": true/false}]\n\n'
        "Nếu không tìm thấy nguồn chính thức, trả về [].\n"
        "KHÔNG tự tạo URL giả. Chỉ trả về URL thật."
    )

    try:
        response = http_requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
    except Exception as exc:
        logger.warning("TokenRouter source search request error: %s", exc)
        return []

    if response.status_code != 200:
        logger.warning("TokenRouter source search HTTP %s: %s", response.status_code, response.text[:200])
        return []

    try:
        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        logger.warning("TokenRouter source search parse error: %s", exc)
        return []

    if not text:
        return []

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            if part.startswith("["):
                text = part
                break

    bracket_start = text.find("[")
    bracket_end = text.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        text = text[bracket_start : bracket_end + 1]

    try:
        results = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("TokenRouter source search returned non-JSON: %s", text[:200])
        return []

    if not isinstance(results, list):
        return []

    return results

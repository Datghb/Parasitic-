"""Domain relevance filter — only keep posts related to ĐVHC (administrative unit) mergers."""
from __future__ import annotations

from typing import Any

_DVHC_KEYWORDS: list[str] = [
    "sáp nhập",
    "gộp tỉnh",
    "giảm tỉnh",
    "hợp nhất",
    "đơn vị hành chính",
    "dvhc",
    "cấp tỉnh",
    "cấp xã",
    "tỉnh mới",
    "thành phố mới",
    "nối tỉnh",
    "16 tỉnh",
    "20 tỉnh",
    "34 tỉnh",
    "166 xã",
    "58 xã",
    "bộ nội vụ",
    "nghị quyết quốc hội",
    "sắp xếp",
    "quy hoạch tỉnh",
    "giảm số lượng",
    "tách tỉnh",
]

_MIN_KEYWORD_MATCH = 2


def is_relevant(text: str) -> bool:
    """Check if text is related to the ĐVHC domain."""
    normalized = text.lower()
    matches = sum(1 for kw in _DVHC_KEYWORDS if kw in normalized)
    return matches >= _MIN_KEYWORD_MATCH


def filter_posts(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter list of posts, keeping only relevant ones."""
    result: list[dict[str, Any]] = []
    for post in posts:
        all_text = post.get("text", "")
        for c in post.get("comments", []):
            all_text += " " + c.get("text", "")
        if is_relevant(all_text):
            result.append(post)
    return result

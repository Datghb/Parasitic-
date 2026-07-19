"""Content cleaner — remove FB UI garbage from crawled data."""

from __future__ import annotations

import re
from typing import Any

_UI_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^Find friends$",
        r"^View Post$",
        r"^See more$",
        r"^No comments yet$",
        r"^Be the first to comment\.$",
        r"^Photos from .+",
        r"^See translation$",
        r"^Interested$",
        r"^Not interested$",
        r"^Newest\s*$",
        r"^Most relevant$",
        r"^.+?[''']s post$",
        r"^https?://\S+$",
        r"^[A-Za-z0-9+/=\s]{30,}$",
        r"^[a-z0-9]{30,}$",
        r"^[\w\d]{40,}$",
        r"^Ads Manager$",
        r"^Facebook$",
        r"^Meta AI$",
        r"^Friends$",
        r"^Memories$",
        r"^Saved$",
        r"^Groups$",
        r"^Reels$",
        r"^Marketplace$",
        r"^Feeds$",
        r"^Events$",
        r"^Privacy\b",
        r"^Are you interested",
    ]
]

_MIN_POST_LEN = 10
_MIN_COMMENT_LEN = 5


def _is_ui_garbage(text: str) -> bool:
    """Check if text is a FB UI element."""
    normalized = re.sub(r"\s+", " ", text.strip())
    for pat in _UI_PATTERNS:
        if pat.search(normalized):
            return True
    tokens = normalized.split(" ")
    if len(tokens) >= 5 and sum(1 for t in tokens if len(t) <= 1) / len(tokens) > 0.6:
        return True
    return False


def clean_comment(text: str) -> str | None:
    """Clean a single comment text. Return None if it is garbage."""
    stripped = text.strip()
    if len(stripped) < _MIN_COMMENT_LEN:
        return None
    if _is_ui_garbage(stripped):
        return None
    return stripped


def clean_post(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Clean a single raw post. Return None if the post should be rejected."""
    text = (raw.get("text") or "").strip()
    if len(text) < _MIN_POST_LEN:
        return None

    raw_comments = raw.get("comments") or []
    cleaned_comments: list[dict[str, Any]] = []
    for c in raw_comments:
        ctext = c.get("text", "")
        cleaned = clean_comment(ctext)
        if cleaned is not None:
            cleaned_comments.append({**c, "text": cleaned})

    return {
        "platform": raw.get("platform", ""),
        "content_type": raw.get("content_type", ""),
        "text": text,
        "author": raw.get("author", "Unknown"),
        "author_id": raw.get("author_id", ""),
        "author_url": raw.get("author_url", ""),
        "author_handle": raw.get("author_handle", ""),
        "page_followers": raw.get("page_followers"),
        "page_verified": raw.get("page_verified", False),
        "url": raw.get("url", ""),
        "timestamp": raw.get("timestamp", ""),
        "engagement": raw.get("engagement", {}),
        "comments": cleaned_comments,
    }

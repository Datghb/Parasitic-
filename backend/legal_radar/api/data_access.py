"""Read-only data access for dashboard API routes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..pipeline import analyze_comment
from .dependencies import data_dir, runs_dir


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _queue_from_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _fixture_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((data_dir() / "fixtures").glob("comments_batch_*.json")):
        rows.extend(_read_json(path))
    return rows


def _platform(source: str) -> str:
    source = source.lower()
    if "fanpage" in source or "group" in source:
        return "Facebook"
    if "video" in source:
        return "YouTube"
    return "Forum"

def _normalise_crawled(raw: dict[str, Any]) -> dict[str, Any]:
    analysed = analyze_comment(str(raw.get("text", "")))
    engagement = raw.get("engagement") or {}
    reach = sum(int(value or 0) for value in engagement.values() if isinstance(value, (int, float)))
    platform_name = str(raw.get("platform", "Forum")).title()
    if platform_name == "Youtube":
        platform_name = "YouTube"
    source_key = str(raw.get("id") or raw.get("url") or analysed["id"])
    author = str(raw.get("author", "Nguồn chưa xác định"))
    author_id = str(raw.get("author_id", ""))
    author_url = str(raw.get("author_url", ""))
    author_handle = str(raw.get("author_handle", ""))
    page_followers = raw.get("page_followers")
    page_verified = raw.get("page_verified", False)
    if page_followers is not None:
        author = f"{author} ({page_followers:,} followers)"
    if page_verified:
        author = f"{author} [verified]"

    label_val = getattr(analysed["label"], "value", analysed["label"])
    priority = int(analysed.get("priority", 0))
    citations = analysed.get("citations") or []

    penalty_str = "Cần xác định chủ thể trước khi tính mức phạt"
    provision_str = "Điều 95 — cần đối chiếu claim cụ thể"
    document_str = "Nghị định 174/2026/NĐ-CP"
    if citations:
        provision_str = "; ".join(citations[:2])

    source_label_val = getattr(analysed["source_label"], "value", analysed["source_label"])
    source_title = "Chưa tìm thấy nguồn phù hợp"
    source_url = ""
    source_agency = ""
    if source_label_val == "co_nguon_xac_nhan":
        source_title = "Có nguồn chính thức xác nhận"
    elif source_label_val == "co_bac_bo_chinh_thuc":
        source_title = "Có nguồn chính thức bác bỏ"

    score = min(95, 30 + priority * 20 + min(25, reach // 10))
    if label_val == "hieu_lam":
        score = max(score, 60)

    return {
        "id": str(raw.get("id") or f"CRAWL-{hashlib.sha1(source_key.encode()).hexdigest()[:12]}"),
        "comment_id": "",
        "text": str(raw.get("text", "")),
        "url": str(raw.get("url", "")),
        "claim": analysed["claim"],
        "keywords": analysed.get("keywords", []),
        "label": label_val,
        "source_label": source_label_val,
        "reason": analysed["reason"],
        "priority": priority,
        "platform": platform_name,
        "account": author,
        "author_id": author_id,
        "author_url": author_url,
        "author_handle": author_handle,
        "published_at": str(raw.get("timestamp", "")),
        "reach": reach,
        "status": "new",
        "document": document_str,
        "provision": provision_str,
        "penalty": penalty_str,
        "source_title": source_title,
        "source_url": source_url,
        "source_agency": source_agency,
        "score": score,
    }


def _normalise(raw: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    fixture = fixture or {}
    label = raw.get("nhan") or raw.get("label") or "can_kiem_chung"
    source_label = raw.get("nhan_nguon") or raw.get("source_label") or "chua_tim_thay_nguon"
    label_val = getattr(label, "value", label)
    source_val = getattr(source_label, "value", source_label)
    priority = int(raw.get("priority", 0))
    reach = int(fixture.get("do_lan_truyen", raw.get("reach", 0)) or 0)

    source_title = "Chưa tìm thấy nguồn phù hợp"
    source_url = str(fixture.get("url", ""))
    source_agency = ""
    if source_val == "co_nguon_xac_nhan":
        source_title = "Có nguồn chính thức xác nhận"
    elif source_val == "co_bac_bo_chinh_thuc":
        source_title = "Có nguồn chính thức bác bỏ"

    score = min(95, 30 + priority * 20 + min(25, reach // 10))
    if label_val == "hieu_lam":
        score = max(score, 60)

    return {
        "id": str(raw.get("id") or fixture.get("id")),
        "comment_id": str(raw.get("comment_id") or fixture.get("id", "")),
        "text": str(raw.get("text") or fixture.get("text", "")),
        "url": str(raw.get("url") or fixture.get("url", "")),
        "claim": str(raw.get("claim") or raw.get("text") or fixture.get("text", "")),
        "keywords": list(raw.get("keywords") or []),
        "label": label_val,
        "source_label": source_val,
        "reason": str(raw.get("ly_do") or raw.get("reason") or "Cần cán bộ đối chiếu."),
        "priority": priority,
        "platform": _platform(str(fixture.get("nguon_mo_ta", "forum"))),
        "account": str(fixture.get("nguon_mo_ta", "Nguồn chưa xác định")),
        "published_at": str(fixture.get("thoi_gian", "")),
        "reach": reach,
        "status": "new",
        "document": str(raw.get("document", "Nghị định 174/2026/NĐ-CP")),
        "provision": str(raw.get("provision", "Điều 95 — cần đối chiếu")),
        "penalty": str(raw.get("penalty", "Cần xác định chủ thể")),
        "source_title": source_title,
        "source_url": source_url,
        "source_agency": source_agency,
        "score": score,
    }


def list_queue_items() -> list[dict[str, Any]]:
    fixtures = _fixture_rows()
    fixture_by_id = {str(item["id"]): item for item in fixtures}
    raw_rows = _queue_from_jsonl(runs_dir() / "queue.jsonl")
    if raw_rows:
        items = [_normalise(row, fixture_by_id.get(str(row.get("id")))) for row in raw_rows]
    else:
        items = []
        for fixture in fixtures:
            analysed = analyze_comment(str(fixture["text"]))
            analysed["id"] = fixture["id"]
            items.append(_normalise(analysed, fixture))
        crawled_rows = _queue_from_jsonl(runs_dir() / "crawled_raw.jsonl")
        if crawled_rows:
            known_ids = {item["id"] for item in items}
            items.extend(
                row for row in (_normalise_crawled(raw) for raw in crawled_rows)
                if row["id"] not in known_ids
            )
    return sorted(items, key=lambda row: (row["priority"], row["reach"]), reverse=True)


def get_queue_item(case_id: str) -> dict[str, Any] | None:
    return next((item for item in list_queue_items() if item["id"] == case_id), None)


def list_study_cases() -> list[dict[str, Any]]:
    path = data_dir() / "study_cases" / "study_cases.json"
    return _read_json(path) if path.exists() else []

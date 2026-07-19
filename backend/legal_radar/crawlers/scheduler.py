"""Crawler scheduler — on-demand + periodic background crawling.

Appends results to runs/crawled_raw.jsonl with URL-based dedup.
Thread-safe for background execution.
"""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

from backend.legal_radar.crawlers.facebook import crawl_facebook
from backend.legal_radar.paths import runs_dir

logger = logging.getLogger(__name__)

CRAWL_KEYWORDS: list[str] = [
    "sáp nhập tỉnh",
    "giảm đơn vị hành chính",
    "34 tỉnh còn 16",
    "gộp tỉnh",
    "sắp xếp ĐVHC",
    "Bộ Nội vụ bác bỏ",
]

_DEFAULT_OUTPUT_DIR = runs_dir()
_DEFAULT_OUTPUT_FILE = "crawled_raw.jsonl"


def _load_seen_urls(path: Path) -> set[str]:
    """Load already-crawled URLs from the JSONL output file."""
    seen: set[str] = set()
    if not path.exists():
        return seen
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    url = data.get("url", "")
                    if url:
                        seen.add(url)
                except (json.JSONDecodeError, KeyError):
                    continue
    except OSError:
        pass
    return seen


def _append_results(path: Path, items: list[dict[str, Any]], seen_urls: set[str]) -> int:
    """Append new items to JSONL file, skipping already-seen URLs. Returns count appended."""
    os.makedirs(path.parent, exist_ok=True)
    appended = 0
    with open(path, "a", encoding="utf-8") as f:
        for item in items:
            url = item.get("url", "")
            if url and url in seen_urls:
                continue
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            f.flush()
            if url:
                seen_urls.add(url)
            appended += 1
    return appended


def crawl_now(
    keywords: list[str] | None = None,
    max_posts_per_platform: int = 20,
    output_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Run crawl immediately (on-demand). Returns all crawled items."""
    kw = keywords or CRAWL_KEYWORDS
    out = Path(output_path) if output_path else _DEFAULT_OUTPUT_DIR / _DEFAULT_OUTPUT_FILE

    seen_urls = _load_seen_urls(out)
    all_items: list[dict[str, Any]] = []

    crawlers: dict[str, tuple[Any, int]] = {}
    if os.environ.get("CRAWL_FACEBOOK_ENABLED", "true").lower() in {"1", "true", "yes", "on"}:
        crawlers["facebook"] = (crawl_facebook, max_posts_per_platform)

    if crawlers:
        pool = ThreadPoolExecutor(max_workers=len(crawlers))
        futures = {
            pool.submit(crawler, keywords=kw, max_posts=raw_limit): platform
            for platform, (crawler, raw_limit) in crawlers.items()
        }
        done, pending = wait(futures, timeout=300)
        for future in done:
            platform = futures[future]
            try:
                all_items.extend(future.result())
            except Exception as exc:
                logger.warning("%s crawler failed: %s", platform, exc)
        for future in pending:
            logger.warning("%s crawler exceeded the 300-second platform window", futures[future])
            future.cancel()
        pool.shutdown(wait=False, cancel_futures=True)

    appended = _append_results(out, all_items, seen_urls)
    logger.info(
        "crawl_now: %d items collected, %d new appended to %s",
        len(all_items),
        appended,
        out,
    )
    return all_items


def crawl_and_process(
    keywords: list[str] | None = None,
    max_posts: int = 20,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Crawl → clean → filter. Return {crawled, relevant, items}."""
    from backend.legal_radar.crawlers.cleaner import clean_post
    from backend.legal_radar.crawlers.filter import is_relevant

    raw_items = crawl_now(keywords=keywords, max_posts_per_platform=max_posts, output_path=output_path)
    logger.info("crawl_and_process: %d raw items from crawler", len(raw_items))

    relevant_items: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for raw in raw_items:
        cleaned = clean_post(raw)
        if not cleaned:
            logger.debug("clean_post returned None for: %s", str(raw.get("url", ""))[:80])
            continue

        url = cleaned.get("url", "")
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)

        all_text = cleaned["text"]
        for c in cleaned.get("comments", []):
            all_text += " " + c.get("text", "")

        if is_relevant(all_text):
            relevant_items.append(cleaned)
        else:
            logger.debug("is_relevant=False for: %s", cleaned["text"][:80])

    relevant_items = relevant_items[:max_posts]
    logger.info("crawl_and_process: %d raw → %d relevant", len(raw_items), len(relevant_items))
    return {
        "crawled": len(raw_items),
        "relevant": len(relevant_items),
        "items": relevant_items,
    }

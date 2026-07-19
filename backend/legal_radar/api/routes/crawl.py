"""On-demand social crawl endpoint with SSE streaming."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from hashlib import sha1

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from backend.legal_radar.api.dependencies import require_admin, runs_dir
from backend.legal_radar.api.schemas import CrawlRequest
from backend.legal_radar.pipeline import _build_crawled_ingestor, _queue_path

logger = logging.getLogger(__name__)

router = APIRouter(tags=["crawl"])


@router.get("/crawl/debug", dependencies=[Depends(require_admin)])
def debug_crawl():
    """Debug endpoint — test Bright Data APIs and return raw results."""
    import time

    import requests as http_requests

    from backend.legal_radar.crawlers.facebook import BD_BASE_URL, BD_COMMENTS_DATASET, BD_POSTS_DATASET
    from backend.legal_radar.settings import get_settings

    settings = get_settings()
    key = settings.brightdata_api_key or ""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    result = {
        "api_key_set": bool(key),
    }

    if not key:
        result["error"] = "BRIGHTDATA_API_KEY is empty"
        return result

    # Test 1: Discover API
    query = "sáp nhập tỉnh site:facebook.com"
    try:
        resp = http_requests.post(
            "https://api.brightdata.com/discover",
            headers=headers,
            json={"query": query, "num_results": 3, "format": "json", "language": "vi", "country": "VN"},
            timeout=15,
        )
        result["discover_post_status"] = resp.status_code
        result["discover_post_response"] = resp.text[:500]
    except Exception as exc:
        result["discover_post_error"] = str(exc)
        return result

    if resp.status_code != 200:
        return result

    task_id = resp.json().get("task_id")
    if not task_id:
        result["error"] = "No task_id"
        return result
    result["discover_task_id"] = task_id

    discover_results = []
    for i in range(10):
        time.sleep(3)
        try:
            r = http_requests.get(f"https://api.brightdata.com/discover?task_id={task_id}", headers=headers, timeout=15)
            data = r.json()
            result[f"discover_poll_{i}"] = data.get("status")
            if data.get("status") == "done":
                discover_results = data.get("results", [])
                result["discover_results_count"] = len(discover_results)
                result["discover_results"] = discover_results[:2]
                break
        except Exception as exc:
            result[f"discover_poll_{i}_error"] = str(exc)

    if not discover_results:
        result["error"] = "Discover returned no results"
        return result

    # Test 2: Scraper API on first discovered URL
    test_url = discover_results[0].get("link", "")
    result["scraper_test_url"] = test_url

    for dataset_id, label in [(BD_POSTS_DATASET, "posts"), (BD_COMMENTS_DATASET, "comments")]:
        try:
            scrape_resp = http_requests.post(
                f"{BD_BASE_URL}/scrape",
                params={"dataset_id": dataset_id, "include_errors": "true", "format": "json"},
                headers=headers,
                json={"input": [{"url": test_url}]},
                timeout=30,
            )
            result[f"scraper_{label}_status"] = scrape_resp.status_code
            result[f"scraper_{label}_response"] = scrape_resp.text[:500]

            if scrape_resp.status_code == 202:
                sid = scrape_resp.json().get("snapshot_id")
                result[f"scraper_{label}_snapshot_id"] = sid
                if sid:
                    for j in range(10):
                        time.sleep(3)
                        sr = http_requests.get(f"{BD_BASE_URL}/snapshot/{sid}", headers=headers, timeout=15)
                        result[f"scraper_{label}_poll_{j}"] = sr.status_code
                        if sr.status_code == 200:
                            snap_data = sr.json()
                            result[f"scraper_{label}_result_count"] = (
                                len(snap_data) if isinstance(snap_data, list) else "not_list"
                            )
                            result[f"scraper_{label}_result"] = (
                                snap_data[:2] if isinstance(snap_data, list) else str(snap_data)[:500]
                            )
                            break
        except Exception as exc:
            result[f"scraper_{label}_error"] = str(exc)

    return result


def _emit(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False) + "\n"


@router.post("/crawl")
def trigger_crawl(request: CrawlRequest):
    """Start a crawl job and stream progress events back to the caller."""
    from backend.legal_radar.settings import get_settings
    from backend.legal_radar.crawlers.facebook import crawl_facebook, _discover_urls, _crawl_one_post, FALLBACK_QUERIES, _DISCOVER_META_KEYWORDS
    from backend.legal_radar.crawlers.cleaner import clean_post
    from backend.legal_radar.crawlers.filter import is_relevant
    from backend.legal_radar.settings import get_settings as _gs

    settings = get_settings()
    if not settings.brightdata_api_key:
        def stream_no_key():
            yield _emit({"type": "error", "message": "BRIGHTDATA_API_KEY chưa được cấu hình. Không thể quét MXH.", "crawled": 0, "relevant": 0})
        return StreamingResponse(stream_no_key(), media_type="text/event-stream")

    max_posts = request.max_posts_per_platform
    output_path = runs_dir() / "crawled_raw.jsonl"

    def stream():
        from pathlib import Path
        import time as _time

        queries = request.keywords or FALLBACK_QUERIES

        # Step 1: Discover URLs
        yield _emit({"type": "progress", "step": "discover", "message": f"Đang tìm URL trên Facebook ({len(queries)} queries)..."})
        try:
            discover_items = _discover_urls(queries, max_posts)
        except Exception as exc:
            yield _emit({"type": "error", "message": f"Discover API lỗi: {exc}", "crawled": 0, "relevant": 0})
            return

        if not discover_items:
            yield _emit({"type": "error", "message": "Discover API không tìm thấy URL nào.", "crawled": 0, "relevant": 0})
            return

        yield _emit({"type": "progress", "step": "discover_done", "message": f"Discover trả về {len(discover_items)} URL", "urls_found": len(discover_items)})

        # Step 2: Scrape each URL
        raw_items = []
        failed = 0
        skipped_meta = 0
        for idx, item in enumerate(discover_items):
            url = item.get("link", "")
            title = item.get("title", "")
            description = item.get("description", "")

            if "facebook.com" not in url.lower():
                skipped_meta += 1
                continue

            meta_text = f"{title} {description}".lower()
            if not any(kw in meta_text for kw in _DISCOVER_META_KEYWORDS):
                skipped_meta += 1
                yield _emit({"type": "progress", "step": "scrape_skip", "message": f"Bỏ qua URL không liên quan: {title[:60]}", "index": idx + 1, "total": len(discover_items)})
                continue

            yield _emit({"type": "progress", "step": "scrape", "message": f"Đang scrape ({idx + 1}/{len(discover_items)}): {title[:60]}...", "index": idx + 1, "total": len(discover_items)})
            try:
                scraped = _crawl_one_post(url)
                if scraped:
                    raw_items.append(scraped)
                    yield _emit({"type": "progress", "step": "scrape_ok", "message": f"Scrape thành công: {scraped.get('author', 'Unknown')} - {len(scraped.get('comments', []))} comments", "index": idx + 1, "total": len(discover_items)})
                else:
                    fallback = {
                        "platform": "facebook", "content_type": "post",
                        "text": description or title,
                        "author": title[:50] if title else "Unknown",
                        "url": url, "timestamp": "", "engagement": {"likes": 0, "shares": 0, "comments": 0}, "comments": [],
                    }
                    if fallback["text"] and len(fallback["text"]) >= 20:
                        raw_items.append(fallback)
                        yield _emit({"type": "progress", "step": "fallback", "message": f"Scraper fail, dùng metadata: {title[:60]}", "index": idx + 1, "total": len(discover_items)})
                    else:
                        failed += 1
                        yield _emit({"type": "progress", "step": "scrape_fail", "message": f"Scraper fail, không có metadata: {url[:60]}", "index": idx + 1, "total": len(discover_items)})
            except Exception as exc:
                failed += 1
                yield _emit({"type": "progress", "step": "scrape_error", "message": f"Lỗi scrape: {exc}", "index": idx + 1, "total": len(discover_items)})

        if not raw_items:
            yield _emit({"type": "error", "message": f"Scrape xong {len(discover_items)} URL nhưng không lấy được nội dung. {failed} lỗi, {skipped_meta} bỏ qua.", "crawled": 0, "relevant": 0})
            return

        yield _emit({"type": "progress", "step": "scrape_done", "message": f"Scrape xong: {len(raw_items)} bài, {failed} lỗi, {skipped_meta} bỏ qua", "crawled": len(raw_items)})

        # Step 3: Clean + Filter
        yield _emit({"type": "progress", "step": "filter", "message": "Đang lọc nội dung liên quan sáp nhập ĐVHC..."})
        relevant_items = []
        seen_urls = set()
        for raw in raw_items:
            cleaned = clean_post(raw)
            if not cleaned:
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
                yield _emit({"type": "progress", "step": "filter_skip", "message": f"Không liên quan: {cleaned['text'][:80]}"})

        relevant_items = relevant_items[:max_posts]

        if not relevant_items:
            yield _emit({"type": "error", "message": f"Tìm thấy {len(raw_items)} bài nhưng không có nội dung liên quan sáp nhập ĐVHC.", "crawled": len(raw_items), "relevant": 0})
            return

        yield _emit({"type": "progress", "step": "filter_done", "message": f"Đã lọc: {len(relevant_items)}/{len(raw_items)} bài liên quan", "relevant": len(relevant_items)})

        # Step 4: Process through pipeline
        yield _emit({"type": "start", "message": f"Đang phân tích {len(relevant_items)} bài viết...", "mode": "live", "total": len(relevant_items)})

        queue_path = _queue_path()
        ingestor = _build_crawled_ingestor(queue_path)
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0

        with queue_path.open("a", encoding="utf-8") as queue_file:
            for post in relevant_items:
                url = str(post.get("url", ""))
                timestamp = str(post.get("timestamp", ""))
                post_platform = str(post.get("platform", "Facebook")).title()
                if post_platform == "Youtube":
                    post_platform = "YouTube"
                post_author = str(post.get("author", ""))
                engagement = post.get("engagement") or {}
                post_reach = sum(int(v or 0) for v in engagement.values() if isinstance(v, (int, float)))
                raw_comments = post.get("comments") or []
                bundled_comments = [
                    {"text": str(c.get("text", "")), "author": str(c.get("author", "")), "timestamp": str(c.get("timestamp", ""))}
                    for c in raw_comments[:20]
                    if str(c.get("text", "")).strip()
                ]
                candidate = {
                    "id": sha1(url.encode("utf-8")).hexdigest(),
                    "text": str(post.get("text", "")),
                    "url": url,
                    "thoi_gian": timestamp,
                    "platform": post_platform,
                    "account": post_author,
                    "published_at": str(post.get("timestamp", "")),
                    "reach": post_reach,
                    "comments": bundled_comments,
                }
                if not candidate.get("text", "").strip():
                    continue
                try:
                    queue_item = ingestor.process_one(candidate, skip_source_search=True)
                    queue_file.write(json.dumps(asdict(queue_item), ensure_ascii=False) + "\n")
                    queue_file.flush()
                    count += 1
                    yield _emit({
                        "type": "item",
                        "count": count,
                        "id": queue_item.id,
                        "claim": queue_item.claim[:100],
                        "label": queue_item.nhan.value,
                        "subject": queue_item.subject,
                        "source_title": queue_item.source_title,
                        "source_url": queue_item.source_url,
                        "source_agency": queue_item.source_agency,
                        "comments_count": len(bundled_comments),
                    })
                except Exception as exc:
                    logger.warning("Crawl item error: %s", exc)
                    yield _emit({"type": "progress", "step": "process_error", "message": f"Lỗi phân tích: {exc}"})

        yield _emit({"type": "done", "analyzed": count, "crawled": len(raw_items), "relevant": len(relevant_items)})

    return StreamingResponse(stream(), media_type="text/event-stream")

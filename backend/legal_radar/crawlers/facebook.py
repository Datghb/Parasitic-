"""Facebook public search crawler using Playwright + stealth.

No login required — only crawls publicly visible posts via
facebook.com/search/posts/?q=<keyword>.

Falls back gracefully (empty list + warning) if anti-detect kicks in.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_KEYWORDS: list[str] = [
    "tin giả",
    "phạt MXH",
    "xử phạt mạng xã hội",
    "nghị định 174",
    "fake news",
    "tin sai sự thật",
    "bóc phốt",
    "tin đồn",
]


def _random_delay(min_s: float = 3.0, max_s: float = 5.0) -> None:
    import time
    time.sleep(random.uniform(min_s, max_s))


def _parse_count(text: str) -> int:
    """Parse abbreviated counts like '1.2K', '5M', '1,234'."""
    text = text.strip().replace(",", "")
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.lower().endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(text)
    except ValueError:
        return 0


def _extract_post_data(card: Any) -> dict[str, Any] | None:
    """Extract structured data from a single Facebook search result card."""
    try:
        text_el = card.query_selector('[data-ad-rendering-role="story_message"]')
        if text_el is None:
            text_el = card.query_selector('[data-testid="post_message"]')
        post_text = text_el.inner_text().strip() if text_el else ""

        author_el = card.query_selector('strong > a, h2 a, h3 a, [role="link"]')
        author = author_el.inner_text().strip() if author_el else "Unknown"

        url = ""
        link_el = card.query_selector('a[href*="/posts/"], a[href*="/photo"], a[href*="/story"]')
        if link_el:
            href = link_el.get_attribute("href") or ""
            if href.startswith("/"):
                url = f"https://www.facebook.com{href}"
            else:
                url = href

        timestamp = datetime.now(timezone.utc).isoformat()
        time_el = card.query_selector("abbr[data-utime], span[id*='jsc']")
        if time_el:
            utime = time_el.get_attribute("data-utime")
            if utime:
                try:
                    timestamp = datetime.fromtimestamp(int(utime), tz=timezone.utc).isoformat()
                except (ValueError, OSError):
                    pass

        engagement: dict[str, int] = {"likes": 0, "shares": 0, "comments": 0}
        stat_els = card.query_selector_all('[aria-label*="reaction"], [aria-label*="comment"], [aria-label*="share"]')
        for sel in stat_els:
            label = (sel.get_attribute("aria-label") or "").lower()
            num_text = sel.inner_text().strip()
            count = _parse_count(num_text)
            if "reaction" in label or "like" in label:
                engagement["likes"] = count
            elif "comment" in label:
                engagement["comments"] = count
            elif "share" in label:
                engagement["shares"] = count

        comments: list[dict[str, str]] = []
        comment_els = card.query_selector_all('[data-testid="UFI2Comment/body"]')
        for c in comment_els[:5]:
            c_text_el = c.query_selector("span")
            c_author_el = c.query_selector("a[role='link'] span")
            comments.append({
                "text": c_text_el.inner_text().strip() if c_text_el else "",
                "author": c_author_el.inner_text().strip() if c_author_el else "Unknown",
                "timestamp": timestamp,
            })

        if not post_text and not url:
            return None

        return {
            "platform": "facebook",
            "content_type": "post",
            "text": post_text,
            "author": author,
            "url": url,
            "timestamp": timestamp,
            "engagement": engagement,
            "comments": comments,
        }
    except Exception as exc:
        logger.debug("Failed to extract post card: %s", exc)
        return None


def crawl_facebook(
    keywords: list[str] | None = None,
    max_posts: int = 20,
) -> list[dict[str, Any]]:
    """Crawl Facebook public search for posts matching *keywords*.

    Returns a list of crawled-item dicts, or an empty list if Playwright
    is unavailable or anti-detect blocks the request.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("playwright not installed — returning empty results")
        return []

    keywords = keywords or DEFAULT_KEYWORDS
    results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    try:
        with sync_playwright() as pw:
            try:
                from playwright_stealth import stealth_sync
            except ImportError:
                logger.warning("playwright-stealth not installed — using plain Chromium")
                stealth_sync = None  # type: ignore[assignment]

            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="vi-VN",
            )
            page = context.new_page()

            if stealth_sync is not None:
                try:
                    stealth_sync(page)
                except Exception:
                    logger.debug("stealth_sync failed — continuing without")

            for kw in keywords:
                if len(results) >= max_posts:
                    break

                url = f"https://www.facebook.com/search/posts/?q={kw}"
                try:
                    page.goto(url, wait_until="networkidle", timeout=30_000)
                    _random_delay()

                    # Check for login wall / anti-detect
                    if "login" in page.url.lower():
                        logger.warning("Facebook redirected to login — anti-detect triggered for '%s'", kw)
                        continue

                    cards = page.query_selector_all('[data-testid="post_message"], [role="article"]')
                    if not cards:
                        cards = page.query_selector_all('div[role="feed"] > div')

                    for card in cards:
                        if len(results) >= max_posts:
                            break
                        post = _extract_post_data(card)
                        if post and post["url"] and post["url"] not in seen_urls:
                            results.append(post)
                            seen_urls.add(post["url"])

                except Exception as exc:
                    logger.warning("Failed to crawl keyword '%s': %s", kw, exc)
                    continue
                finally:
                    _random_delay()

            browser.close()

    except Exception as exc:
        logger.warning("Facebook crawler failed entirely: %s — returning empty list", exc)
        return []

    logger.info("Facebook crawler collected %d posts", len(results))
    return results

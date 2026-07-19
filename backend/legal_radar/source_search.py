from __future__ import annotations

import logging
import os
import time
from urllib.parse import urlparse

import requests as http_requests

from backend.legal_radar.resilience import CircuitBreaker, CircuitOpenError, call_with_retry
from backend.legal_radar.source_classifier import TIER_0_DOMAINS, TIER_1_DOMAINS, TIER_2_DOMAINS

logger = logging.getLogger(__name__)

TRUSTED_DOMAINS = TIER_0_DOMAINS + TIER_1_DOMAINS + TIER_2_DOMAINS

BD_DISCOVER_URL = "https://api.brightdata.com/discover"
_brightdata_breaker = CircuitBreaker(failure_threshold=3, recovery_seconds=30)

_DOMAIN_TO_NGUON: dict[str, str] = {
    "chinhphu.vn": "Cổng TTĐT Chính phủ",
    "bocongan.gov.vn": "Cổng TTĐT Bộ Công an",
    "moh.gov.vn": "Cổng TTĐT Bộ Y tế",
    "mic.gov.vn": "Cổng TTĐT Bộ TT&TT",
    "moj.gov.vn": "Cổng TTĐT Bộ Tư pháp",
    "sbv.gov.vn": "Ngân hàng Nhà nước",
    "vietnamgovernment.vn": "Cổng TTĐT Chính phủ",
    "ttxvn.vn": "Thông tấn xã Việt Nam",
    "baotintuc.vn": "Báo Tin tức",
    "vtv.vn": "Đài Truyền hình Việt Nam",
    "vnews.vn": "VNews",
    "nhandan.vn": "Báo Nhân Dân",
    "quochoi.vn": "Cổng TTĐT Quốc hội",
    "suckhoedoisong.vn": "Báo Sức khỏe & Đời sống",
    "vnexpress.net": "VnExpress",
    "tuoitre.vn": "Báo Tuổi Trẻ",
    "thanhnien.vn": "Báo Thanh Niên",
    "dantri.com.vn": "Báo Dân Trí",
    "vietnamnet.vn": "VietNamNet",
    "plo.vn": "Báo Pháp Luật TP.HCM",
    "nld.com.vn": "Báo Người Lao Động",
}


def _bd_headers() -> dict[str, str]:
    key = os.environ.get("BRIGHTDATA_API_KEY", "")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _infer_nguon(url: str) -> str:
    """Infer source agency name from URL domain."""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return ""
    host_lower = host.lower()
    for domain, name in _DOMAIN_TO_NGUON.items():
        if domain in host_lower:
            return name
    return host


def _build_source_query(keywords: list[str]) -> list[str]:
    """Build 2 site-restricted sub-queries from keywords.

    Always includes ĐVHC (administrative unit merger) context terms
    to keep search results on-topic. Sub-query 1 targets TIER_0,
    sub-query 2 targets TIER_1 + TIER_2.
    """
    kw = " ".join(keywords[:6])
    if not kw.strip():
        kw = "sáp nhập đơn vị hành chính"

    merger_context = "sáp nhập đơn vị hành chính tỉnh"
    combined = f"{merger_context} {kw}"

    tier0_sites = " OR ".join(f"site:{d}" for d in [".gov.vn", "chinhphu.vn", "bocongan.gov.vn", "sbv.gov.vn"])
    tier12_sites = " OR ".join(
        f"site:{d}"
        for d in [
            "baotintuc.vn",
            "vtv.vn",
            "nhandan.vn",
            "vnexpress.net",
            "tuoitre.vn",
            "thanhnien.vn",
            "vietnamnet.vn",
        ]
    )

    return [
        f"{combined} {tier0_sites}",
        f"{combined} {tier12_sites}",
    ]


def _poll_discover(task_id: str) -> list[dict]:
    """Poll Bright Data Discover API until done. Returns list of result items."""
    for i in range(15):
        time.sleep(3)
        try:
            r = http_requests.get(
                f"{BD_DISCOVER_URL}?task_id={task_id}",
                headers=_bd_headers(),
                timeout=15,
            )
        except http_requests.RequestException:
            logger.warning("Source search poll %d failed for task %s", i, task_id)
            continue
        if r.status_code != 200:
            continue
        data = r.json()
        if data.get("status") == "done":
            return data.get("results", [])
    return []


def _map_bd_result(item: dict) -> dict:
    """Map a Bright Data Discover result to the xac_thuc_nguon input format.

    Results that pass _is_trusted_domain() are real search results from
    government/news sites — mark as confirmed so apply_fusion_rules()
    can classify them properly.
    """
    url = item.get("link", "")
    return {
        "tieu_de": item.get("title", ""),
        "nguon": _infer_nguon(url),
        "url": url,
        "ngay_dang": "",
        "noi_dung_tom_tat": item.get("description", ""),
        "la_bac_bo": False,
        "la_xac_nhan": True,
    }


def _is_trusted_domain(url: str) -> bool:
    """Check if URL belongs to a trusted domain whitelist."""
    url_lower = url.lower()
    return any(domain in url_lower for domain in TRUSTED_DOMAINS)


def search_brightdata(
    claim_keywords: list[str],
    thoi_gian: str = "",
) -> list[dict]:
    """Search for official Vietnamese sources via Bright Data Discover API.

    Builds site-restricted queries targeting TIER_0/1/2 domains,
    sends to Bright Data Discover API (same pattern as crawlers/facebook.py),
    returns real search results with verified URLs.
    """
    api_key = os.environ.get("BRIGHTDATA_API_KEY", "")
    if not api_key:
        logger.warning("No BRIGHTDATA_API_KEY — skipping source search")
        return []

    sub_queries = _build_source_query(claim_keywords)
    if not sub_queries:
        return []

    seen_urls: set[str] = set()
    results: list[dict] = []

    for query in sub_queries:
        logger.info("BrightData Discover: %s", query)
        try:
            resp = call_with_retry(
                lambda: http_requests.post(
                    BD_DISCOVER_URL,
                    headers=_bd_headers(),
                    json={
                        "query": query,
                        "num_results": 5,
                        "format": "json",
                        "language": "vi",
                        "country": "VN",
                    },
                    timeout=15,
                ),
                breaker=_brightdata_breaker,
                attempts=2,
                retry_on=(http_requests.RequestException,),
            )
        except (http_requests.RequestException, CircuitOpenError) as exc:
            logger.warning("BrightData Discover request error: %s", exc)
            continue

        if resp.status_code != 200:
            logger.warning("BrightData Discover HTTP %s: %s", resp.status_code, resp.text[:200])
            continue

        task_id = resp.json().get("task_id")
        if not task_id:
            logger.warning("BrightData Discover returned no task_id")
            continue

        raw_results = _poll_discover(task_id)
        for item in raw_results:
            url = item.get("link", "")
            if not url or url in seen_urls:
                continue
            if not _is_trusted_domain(url):
                logger.debug("Bỏ qua URL không thuộc whitelist: %s", url)
                continue
            seen_urls.add(url)
            results.append(_map_bd_result(item))

    logger.info("BrightData source search returned %d results", len(results))
    return results

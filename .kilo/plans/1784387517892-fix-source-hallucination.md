# Fix Source Hallucination: Bright Data Discover API

## Problem

`dynamic_search_gemini()` asks LLM to generate URLs → LLM hallucinates URLs (404/timeout).
`_url_exists()` band-aid adds 8-16s latency. Neither approach returns real search results.

## Solution

Replace LLM URL generation with **Bright Data Discover API** — the same real search engine
already used in `crawlers/facebook.py` for Facebook post discovery. Uses `site:` operator
to restrict results to trusted Vietnamese government/news domains.

**No new API keys needed** — reuses existing `BRIGHTDATA_API_KEY`.

## Data Flow

```
Claim → LLM extract keywords (unchanged)
     → Bright Data Discover API
       query: "xử phạt tin giả site:gov.vn OR site:baotintuc.vn OR site:tuoitre.vn"
       → real search results with real URLs
     → Filter by domain whitelist (TIER_0 + TIER_1 + TIER_2)
     → xac_thuc_nguon() fusion rules (unchanged)
     → Return verified source with real URL
```

## Files to Change

### 1. `backend/legal_radar/source_search.py`

**Replace** `dynamic_search_gemini()` with `search_brightdata()`:

```python
BD_DISCOVER_URL = "https://api.brightdata.com/discover"

def search_brightdata(keywords: list[str], thoi_gian: str = "") -> list[dict]:
    """Search for official Vietnamese sources via Bright Data Discover API.
    
    Builds site-restricted queries targeting TIER_0/1/2 domains,
    sends to Bright Data Discover API (same as facebook.py crawler),
    returns real search results with verified URLs.
    """
    api_key = os.environ.get("BRIGHTDATA_API_KEY", "")
    if not api_key:
        logger.warning("No BRIGHTDATA_API_KEY — skipping source search")
        return []
    
    query = _build_source_query(keywords)
    # POST to Discover API (same pattern as crawlers/facebook.py:_discover_urls)
    # Poll for results
    # Filter by TRUSTED_DOMAINS
    # Return list[dict] with {tieu_de, nguon, url, ngay_dang, noi_dung_tom_tat}
```

Key design decisions:
- **Query construction** (`_build_source_query`):
  - Join keywords with Vietnamese legal terms
  - Append `site:` restrictions for TIER_0 domains (`.gov.vn`, `chinhphu.vn`, etc.)
  - Example: `"xử phạt tin giả NĐ174 site:gov.vn OR site:baotintuc.vn"`
- **Reuse `_poll_discover()`** pattern from `crawlers/facebook.py`
- **Result mapping**: Bright Data returns `{link, title, description, position}` —
  map to `{tieu_de, nguon, url, ngay_dang, noi_dung_tom_tat}`
- **Domain filter**: Only keep URLs matching `TRUSTED_DOMAINS`
- **No `_url_exists()` needed**: URLs come from real search results

**Keep** `dynamic_search_gemini()` as fallback (rename to `_fallback_llm_search()`),
**Keep** `_is_trusted_domain()` for domain filtering,
**Remove** `_url_exists()` from main flow (not needed for real search results).

### 2. `backend/legal_radar/pipeline.py`

**Update** `analyze_comment()` and `process_one()`:
- Replace `from .source_search import dynamic_search_gemini` with `from .source_search import search_brightdata`
- Replace `dynamic_search_gemini(...)` call with `search_brightdata(...)`
- Keep `_fallback_fact_source()` as last resort when Discover API returns nothing

### 3. `backend/legal_radar/verification.py`

**Update** `verify_source()`:
- Replace `from .source_search import dynamic_search_gemini` with `from .source_search import search_brightdata`
- Replace call accordingly

### 4. No frontend changes

Source fields (`source_title`, `source_url`, `source_agency`) are already in the API
response and rendered in the UI. No frontend changes needed.

## Bright Data Discover API Pattern (from facebook.py)

```python
# POST search query → get task_id
resp = requests.post(
    "https://api.brightdata.com/discover",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"query": query, "num_results": 10, "format": "json", "language": "vi", "country": "VN"},
    timeout=30,
)
task_id = resp.json()["task_id"]

# Poll until done (same pattern as facebook.py:_poll_discover)
for _ in range(20):
    time.sleep(3)
    r = requests.get(f"https://api.brightdata.com/discover?task_id={task_id}", ...)
    if r.json()["status"] == "done":
        results = r.json()["results"]  # [{link, title, description, position}, ...]
```

## Query Construction Strategy

For each claim, build a query like:
```
"xử phạt tin giả NĐ174 site:chinhphu.vn OR site:bocongan.gov.vn OR site:baotintuc.vn"
```

Split into 2-3 sub-queries to avoid overly long query strings:
1. TIER_0: `keywords + " site:gov.vn OR site:chinhphu.vn"`
2. TIER_1: `keywords + " site:baotintuc.vn OR site:vtv.vn OR site:nhandan.vn"`

Each sub-query returns up to 10 results. Merge, dedup by URL, filter by whitelist.

## Failure Modes

| Scenario | Behavior |
|----------|----------|
| No `BRIGHTDATA_API_KEY` | Log warning, return empty, fallback to fact_references.json |
| Discover API timeout | Log warning, return empty, fallback to fact_references.json |
| No results for keywords | Return empty, fallback to fact_references.json |
| Results exist but none pass domain filter | Return empty, fallback to fact_references.json |

## Validation

1. `ruff check backend/legal_radar/source_search.py backend/legal_radar/pipeline.py backend/legal_radar/verification.py`
2. `python -c "from legal_radar.source_search import search_brightdata"`
3. Test with real claim: `search_brightdata(["xử phạt", "tin giả", "NĐ174"])` → expect real `.gov.vn` URLs
4. Test `POST /api/qa` with claim → verify `source_url` is real (not hallucinated)
5. Test `POST /api/crawl` → verify queue items have real source URLs

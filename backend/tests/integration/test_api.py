import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from legal_radar.model import NhanNguon
from legal_radar.api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_preflight_allows_production_frontend() -> None:
    response = client.options(
        "/api/crawl",
        headers={
            "Origin": "https://diachung.dpdns.org",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "https://diachung.dpdns.org"
    )


def test_queue_returns_list_with_supported_schema() -> None:
    response = client.get("/api/queue")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    if items:
        assert {"id", "claim", "label", "source_label", "platform", "reach"} <= items[0].keys()


def test_case_returns_matching_queue_item() -> None:
    queue_items = client.get("/api/queue").json()
    if not queue_items:
        return
    queue_item = queue_items[0]
    response = client.get(f"/api/cases/{queue_item['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == queue_item["id"]


def test_case_missing_returns_404() -> None:
    response = client.get("/api/cases/not-found")
    assert response.status_code == 404


def test_verify_returns_study_cases() -> None:
    response = client.get("/api/verify")
    assert response.status_code == 200
    cases = response.json()["cases"]
    assert len(cases) >= 2
    assert {"id", "ten_vu", "expected_he_thong", "nguon_url"} <= cases[0].keys()


def test_qa_returns_supported_schema() -> None:
    response = client.post("/api/qa", json={"question": "Cá nhân đăng tin giả bị phạt bao nhiêu?"})
    assert response.status_code == 200
    assert response.json()["label"] in {"dung", "hieu_lam", "can_kiem_chung"}

def test_crawl_returns_supported_schema(monkeypatch, tmp_path) -> None:
    from legal_radar.api.routes import crawl

    monkeypatch.setattr(crawl, "runs_dir", lambda: tmp_path)
    monkeypatch.setattr(crawl, "_try_live_crawl", lambda *a, **kw: {"items": [], "crawled": 0, "relevant": 0})
    response = client.post("/api/crawl", json={"keywords": ["tin giả"], "max_posts_per_platform": 2})
    assert response.status_code == 200
    lines = [ln for ln in response.text.strip().split("\n") if ln.strip()]
    assert len(lines) >= 1
    start_msg = json.loads(lines[0])
    assert start_msg["type"] == "start"


def test_crawl_analyzes_fixture_posts_and_writes_queue(monkeypatch, tmp_path) -> None:
    from legal_radar.api.routes import crawl

    fixture_path = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "fixtures"
        / "crawled_sample.json"
    )
    fixture_post = json.loads(fixture_path.read_text(encoding="utf-8"))[0]
    expected_count = 1 + len(fixture_post.get("comments", []))
    queue_path = tmp_path / "queue.jsonl"
    provider = MagicMock()
    provider.generate.return_value = json.dumps(
        {
            "claim": "Thong tin sap nhap can kiem chung",
            "keywords": ["sap nhap", "don vi hanh chinh"],
            "subject": None,
        },
        ensure_ascii=False,
    )

    monkeypatch.setattr(
        crawl,
        "_try_live_crawl",
        lambda *a, **kw: {"crawled": 1, "relevant": 1, "items": [fixture_post]},
    )
    monkeypatch.setattr(crawl, "runs_dir", lambda: tmp_path)
    monkeypatch.setattr(crawl, "_load_sample_items", lambda: [fixture_post])

    import legal_radar.pipeline as pipeline_mod
    monkeypatch.setattr(pipeline_mod, "_queue_path", lambda: queue_path)
    monkeypatch.setattr(crawl, "_queue_path", lambda: queue_path)
    monkeypatch.setattr(crawl, "_build_crawled_ingestor", lambda qp: pipeline_mod.CommentIngestor(provider, MagicMock(), str(qp)))
    monkeypatch.setattr(pipeline_mod, "_default_provider", lambda: provider)

    with patch(
        "legal_radar.source_search.dynamic_search_gemini",
        return_value=[],
    ), patch(
        "legal_radar.pipeline.xac_thuc_nguon",
        return_value=(NhanNguon.CHUA_TIM_THAY_NGUON, [], "Khong tim thay nguon"),
    ):
        response = client.post(
            "/api/crawl",
            json={"keywords": ["sap nhap"], "max_posts_per_platform": 1},
        )

    assert response.status_code == 200
    lines = [ln for ln in response.text.strip().split("\n") if ln.strip()]
    types = [json.loads(ln)["type"] for ln in lines]
    assert "start" in types
    assert "done" in types
    done_msg = json.loads(lines[-1])
    assert done_msg["analyzed"] == expected_count

    rows = [
        json.loads(line)
        for line in queue_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == expected_count

"""Backfill old queue.jsonl items with computed spread_risk, ai_accuracy, source_reliability."""
import json
import math

QUEUE = "runs/queue.jsonl"


def compute_spread_risk(item):
    label = item.get("nhan", "can_kiem_chung")
    reach = int(item.get("reach", 0) or 0)
    source = item.get("nhan_nguon", "chua_tim_thay_nguon")
    reason = item.get("ly_do", "")
    severity = 40 if label == "hieu_lam" else 20 if label == "can_kiem_chung" else 5
    reach_sc = min(30, round(math.log2(reach + 1) * 5)) if reach > 0 else 0
    cta_words = ["tẩy chay", "cảnh giác", "cảnh báo", "đừng tin", "báo cáo", "chia sẻ ngay"]
    has_cta = any(w in reason.lower() for w in cta_words)
    cta = 15 if has_cta and source == "chua_tim_thay_nguon" else 5 if has_cta else 0
    source_gap = 10 if source == "chua_tim_thay_nguon" else 5 if source == "co_bac_bo_chinh_thuc" else 0
    return min(100, severity + reach_sc + cta + source_gap)


def compute_ai_accuracy(item):
    label = item.get("nhan", "can_kiem_chung")
    citations = item.get("citations", [])
    cite_sc = min(15, len(citations) * 5)
    if label == "dung":
        return min(100, 60 + cite_sc)
    elif label == "hieu_lam":
        return min(100, 55 + cite_sc)
    return min(100, 30 + cite_sc)


def compute_source_reliability(item):
    source = item.get("nhan_nguon", "chua_tim_thay_nguon")
    citations = item.get("citations", [])
    denial_sc = 20 if source == "co_bac_bo_chinh_thuc" else 10 if source == "co_nguon_xac_nhan" else 0
    cite_sc = 5 if citations else 0
    return min(100, denial_sc + cite_sc)


def main():
    items = []
    with open(QUEUE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))

    backfilled = 0
    for item in items:
        needs_backfill = (
            "spread_risk" not in item
            or "ai_accuracy" not in item
            or "source_reliability" not in item
        )
        if needs_backfill:
            item["spread_risk"] = compute_spread_risk(item)
            item["ai_accuracy"] = compute_ai_accuracy(item)
            item["source_reliability"] = compute_source_reliability(item)
            backfilled += 1

    with open(QUEUE, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Backfilled {backfilled}/{len(items)} items")
    for item in items:
        rid = item["id"][:12]
        print(f"  {rid} | risk={item['spread_risk']:3d}  acc={item['ai_accuracy']:3d}  rel={item['source_reliability']:3d} | {item['nhan']:20s} reach={item.get('reach', 0)}")


if __name__ == "__main__":
    main()

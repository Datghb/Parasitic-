"""Pipeline orchestration."""

from uuid import uuid4

from .engine import classify_claim
from .model import QueueItem
from .verification import verify_source


def analyze_comment(comment: str) -> QueueItem:
    return QueueItem(
        id=str(uuid4()),
        claim=comment.strip(),
        label=classify_claim(comment),
        source_label=verify_source(comment),
        reason="Chưa đủ dữ kiện để kết luận.",
    )


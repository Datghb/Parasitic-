"""Report generation helpers."""

import json
from dataclasses import asdict

from backend.legal_radar.model import QueueItem


def render_json(item: QueueItem) -> str:
    """Serialize a QueueItem to a JSON string."""
    return json.dumps(asdict(item), ensure_ascii=False)

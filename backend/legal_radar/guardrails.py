"""Domain safety checks applied after classification."""

from .model import ClaimLabel


def ensure_valid_label(label: ClaimLabel) -> ClaimLabel:
    return ClaimLabel(label)


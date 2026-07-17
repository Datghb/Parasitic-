"""Pure legal classification functions."""

from .model import ClaimLabel


def classify_claim(claim: str) -> ClaimLabel:
    if not claim.strip():
        return ClaimLabel.CAN_KIEM_CHUNG
    return ClaimLabel.CAN_KIEM_CHUNG


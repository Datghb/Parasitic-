"""Domain models shared by the legal engine and API."""

from dataclasses import dataclass
from enum import StrEnum


class ClaimLabel(StrEnum):
    DUNG = "dung"
    HIEU_LAM = "hieu_lam"
    CAN_KIEM_CHUNG = "can_kiem_chung"


class SourceLabel(StrEnum):
    CO_NGUON_XAC_NHAN = "co_nguon_xac_nhan"
    CO_BAC_BO_CHINH_THUC = "co_bac_bo_chinh_thuc"
    CHUA_TIM_THAY_NGUON = "chua_tim_thay_nguon"


@dataclass(frozen=True)
class QueueItem:
    id: str
    claim: str
    label: ClaimLabel
    source_label: SourceLabel
    reason: str


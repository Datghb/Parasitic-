from __future__ import annotations

import re
from enum import StrEnum


class LabelEnum(StrEnum):
    DUNG = "dung"
    HIEU_LAM = "hieu_lam"
    CAN_KIEM_CHUNG = "can_kiem_chung"


class NhanNguonEnum(StrEnum):
    CO_NGUON_XAC_NHAN = "co_nguon_xac_nhan"
    CO_BAC_BO_CHINH_THUC = "co_bac_bo_chinh_thuc"
    CHUA_TIM_THAY_NGUON = "chua_tim_thay_nguon"


FORBIDDEN_LABELS = {"vi_pham", "sai", "dung_100", "violation"}

PII_PATTERNS = [
    (
        r"(?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-ZÀ-ỸĐ][a-zà-ỹđ]*\s+[A-ZÀ-ỸĐ][a-zà-ỹđ]*",
        "N.V.A",
    ),
    (r"https?://(?:www\.)?facebook\.com/[^\s]+", "[đã ẩn danh]"),
    (r"https?://(?:www\.)?tiktok\.com/@[^\s]+", "[đã ẩn danh]"),
]

INJECTION_PATTERNS = [
    r"ignore\s+previous",
    r"you\s+are\s+now",
    r"system\s*:",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"\[INST\]",
    r"\[/INST\]",
    r"ignore\s+above",
    r"disregard\s+prior",
    r"new\s+instructions",
]

FORBIDDEN_SOURCE_RENDER = [
    "nghi vấn sai",
    "độ tin cậy",
    "xác suất sai",
    "% sai",
    "% đúng",
]


def validate_label(label: str) -> str:
    """Validate that label is an accepted classification label and is not forbidden."""
    try:
        LabelEnum(label)
    except ValueError:
        raise ValueError(f"Nhãn '{label}' không hợp lệ. Chỉ chấp nhận: {[e.value for e in LabelEnum]}")
    if label in FORBIDDEN_LABELS:
        raise ValueError(f"Nhãn '{label}' bị cấm — hệ thống không kết luận vi phạm")
    return label


def assert_rule_half(
    to_chuc_min: int,
    to_chuc_max: int,
    ca_nhan_min: int,
    ca_nhan_max: int,
) -> None:
    """Assert that the individual penalty is exactly half of the organisation penalty."""
    expected_min = to_chuc_min // 2
    expected_max = to_chuc_max // 2
    if ca_nhan_min != expected_min or ca_nhan_max != expected_max:
        raise AssertionError(
            f"Rule 1/2 violated: tổ chức {to_chuc_min}-{to_chuc_max} "
            f"→ cá nhân phải là {expected_min}-{expected_max}, "
            f"nhưng nhận được {ca_nhan_min}-{ca_nhan_max}"
        )


def anonymize_pii(text: str) -> str:
    """Replace personally identifiable information in text with anonymised placeholders."""
    result = text
    for pattern, replacement in PII_PATTERNS:
        result = re.sub(pattern, replacement, result)
    return result


def sanitize_injection(text: str) -> str:
    """Wrap text in a quoted-data marker if prompt-injection patterns are detected."""
    result = text
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, result, re.IGNORECASE):
            result = f"[quoted data: {result}]"
            break
    return result


def validate_reviewer_label(label: str) -> str:
    """Validate the reviewer decision label; return empty string if label is empty."""
    if not label:
        return ""
    try:
        LabelEnum(label)
    except ValueError:
        raise ValueError(f"Nhãn reviewer '{label}' không hợp lệ. Chỉ chấp nhận: {[e.value for e in LabelEnum]}")
    return label


def validate_source_label(nhan_nguon: str, rendered_text: str) -> None:
    """Validate the source label and assert no forbidden phrases appear in the rendered output."""
    try:
        NhanNguonEnum(nhan_nguon)
    except ValueError:
        raise ValueError(f"Nhãn nguồn '{nhan_nguon}' không hợp lệ. Chỉ chấp nhận: {[e.value for e in NhanNguonEnum]}")
    if nhan_nguon == NhanNguonEnum.CHUA_TIM_THAY_NGUON.value:
        for phrase in FORBIDDEN_SOURCE_RENDER:
            if phrase in rendered_text.lower():
                raise AssertionError(
                    f"Vi phạm nguồn-tin rail: '{phrase}' không được phép xuất hiện "
                    f"khi nhãn nguồn là chua_tim_thay_nguon"
                )

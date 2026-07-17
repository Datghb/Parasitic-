"""LLM provider adapters."""

from typing import Protocol


class ClaimExtractor(Protocol):
    def extract(self, text: str) -> dict[str, object]: ...


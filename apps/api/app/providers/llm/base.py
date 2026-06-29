from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True)
class TranscriptEvidence:
    segment_id: UUID
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True)
class LLMExtractionRequest:
    meeting_id: UUID
    transcript: list[TranscriptEvidence]
    json_schema: dict[str, Any]
    prompt_version: str
    retry_instruction: str | None = None


@dataclass(frozen=True)
class LLMExtractionResponse:
    content: str
    model_name: str
    model_version: str | None = None


class LLMExtractor(Protocol):
    provider_name: str

    def extract(self, request: LLMExtractionRequest) -> LLMExtractionResponse:
        """Return provider text that will be validated against the JSON schema."""

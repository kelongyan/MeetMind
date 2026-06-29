from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class AnswerEvidence:
    id: str
    meeting_id: UUID
    source_text: str
    quote: str
    source_type: str
    source_id: UUID
    segment_id: UUID
    start_ms: int
    end_ms: int
    score: float
    metadata: dict[str, object]


@dataclass(frozen=True)
class AnswerSynthesisRequest:
    meeting_id: UUID
    question: str
    evidence: list[AnswerEvidence]


@dataclass(frozen=True)
class AnswerSynthesisResponse:
    content: str
    selected_evidence_ids: list[str]
    model_name: str


class AnswerSynthesizer(Protocol):
    provider_name: str
    model_name: str

    def synthesize(
        self, request: AnswerSynthesisRequest
    ) -> AnswerSynthesisResponse:
        """Create an answer from citable meeting evidence only."""

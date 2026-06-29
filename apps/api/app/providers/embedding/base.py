from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmbeddingResponse:
    vectors: list[list[float]]
    model_name: str


class Embedder(Protocol):
    provider_name: str
    model_name: str

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        """Return one vector for each input text in the same order."""

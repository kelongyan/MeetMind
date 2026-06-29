from __future__ import annotations

import hashlib
import math
import re

from app.providers.embedding.base import EmbeddingResponse

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


class LocalHashEmbedder:
    provider_name = "local"

    def __init__(self, *, dimensions: int = 1536, model_name: str = "local-hash-1536"):
        self.dimensions = dimensions
        self.model_name = model_name

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        return EmbeddingResponse(
            vectors=[self._embed_text(text) for text in texts],
            model_name=self.model_name,
        )

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            vector[index] += 1.0

        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0:
            return vector
        return [value / magnitude for value in vector]


def _tokens(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(text)]

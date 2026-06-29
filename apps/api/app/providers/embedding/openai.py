from __future__ import annotations

from typing import Any

from app.providers.embedding.base import EmbeddingResponse


class OpenAIEmbedder:
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model_name = model

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model_name, input=texts)
        ordered = sorted(response.data, key=lambda item: item.index)
        return EmbeddingResponse(
            vectors=[list(_get_value(item, "embedding") or []) for item in ordered],
            model_name=self.model_name,
        )


def _get_value(source: Any, key: str) -> Any:
    if isinstance(source, dict):
        return source.get(key)
    return getattr(source, key, None)

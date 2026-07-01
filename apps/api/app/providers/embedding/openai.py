from __future__ import annotations

from typing import Any

from app.providers.embedding.base import EmbeddingResponse


class OpenAIEmbedder:
    provider_name = "openai"

    def __init__(
        self, *, api_key: str, model: str, base_url: str | None = None
    ) -> None:
        self.api_key = api_key
        self.model_name = model
        self.base_url = base_url

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        from openai import OpenAI

        kwargs: dict[str, object] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)  # type: ignore[arg-type]
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

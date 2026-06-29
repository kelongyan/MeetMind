from app.config import settings
from app.exceptions import ConflictError
from app.providers.embedding.base import Embedder
from app.providers.embedding.local import LocalHashEmbedder
from app.providers.embedding.openai import OpenAIEmbedder


def get_embedder() -> Embedder:
    if settings.embedding_provider == "local":
        return LocalHashEmbedder(
            dimensions=settings.embedding_dimensions,
            model_name=settings.local_embedding_model,
        )
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ConflictError("OpenAI embedding provider requires OPENAI_API_KEY")
        return OpenAIEmbedder(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
    raise ConflictError("Embedding provider is disabled")

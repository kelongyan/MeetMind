from app.config import settings
from app.exceptions import ConflictError
from app.providers.llm.base import LLMExtractor
from app.providers.llm.openai import OpenAILLMExtractor


def get_llm_extractor() -> LLMExtractor:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ConflictError("OpenAI LLM provider requires OPENAI_API_KEY")
        return OpenAILLMExtractor(
            api_key=settings.openai_api_key,
            model=settings.openai_llm_model,
            base_url=settings.openai_base_url,
        )
    raise ConflictError("LLM provider is disabled")

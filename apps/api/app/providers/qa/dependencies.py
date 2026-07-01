from app.config import settings
from app.exceptions import ConflictError
from app.providers.qa.base import AnswerSynthesizer
from app.providers.qa.extractive import ExtractiveAnswerSynthesizer


def get_answer_synthesizer() -> AnswerSynthesizer:
    if settings.qa_answer_provider == "extractive":
        return ExtractiveAnswerSynthesizer()
    if settings.qa_answer_provider == "llm":
        if not settings.openai_api_key:
            raise ConflictError("LLM QA provider requires OPENAI_API_KEY")
        from app.providers.qa.generative import LLMAnswerSynthesizer

        return LLMAnswerSynthesizer(
            api_key=settings.openai_api_key,
            model=settings.openai_llm_model,
            base_url=settings.openai_base_url,
        )
    raise ConflictError("Q&A answer provider is disabled")

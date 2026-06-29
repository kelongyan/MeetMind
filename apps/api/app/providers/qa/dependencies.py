from app.config import settings
from app.exceptions import ConflictError
from app.providers.qa.base import AnswerSynthesizer
from app.providers.qa.extractive import ExtractiveAnswerSynthesizer


def get_answer_synthesizer() -> AnswerSynthesizer:
    if settings.qa_answer_provider == "extractive":
        return ExtractiveAnswerSynthesizer()
    raise ConflictError("Q&A answer provider is disabled")

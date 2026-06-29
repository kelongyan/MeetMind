from app.config import settings
from app.exceptions import ConflictError
from app.providers.asr.base import Transcriber
from app.providers.asr.openai import OpenAITranscriber


def get_transcriber() -> Transcriber:
    if settings.asr_provider == "openai":
        if not settings.openai_api_key:
            raise ConflictError("OpenAI ASR provider requires OPENAI_API_KEY")
        return OpenAITranscriber(
            api_key=settings.openai_api_key,
            model=settings.openai_transcription_model,
        )

    raise ConflictError("ASR provider is not configured")

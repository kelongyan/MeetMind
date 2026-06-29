from pathlib import Path
from typing import Any

from app.providers.asr.base import TranscribedSegment


class OpenAITranscriber:
    def __init__(self, *, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> list[TranscribedSegment]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        with audio_path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = _get_value(response, "segments") or []
        if not segments:
            text = _get_value(response, "text") or ""
            if not text:
                return []
            return [TranscribedSegment(start_ms=0, end_ms=0, text=text)]

        return [
            TranscribedSegment(
                start_ms=round(float(_get_value(segment, "start") or 0) * 1000),
                end_ms=round(float(_get_value(segment, "end") or 0) * 1000),
                text=str(_get_value(segment, "text") or "").strip(),
                confidence=None,
            )
            for segment in segments
            if str(_get_value(segment, "text") or "").strip()
        ]


def _get_value(source: Any, key: str) -> Any:
    if isinstance(source, dict):
        return source.get(key)
    return getattr(source, key, None)

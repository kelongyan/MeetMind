from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TranscribedSegment:
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None = None


class Transcriber(Protocol):
    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> list[TranscribedSegment]:
        pass

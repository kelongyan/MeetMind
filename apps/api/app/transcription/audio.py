import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from app.config import settings


@dataclass(frozen=True)
class NormalizedAudio:
    path: Path
    duration_ms: int


@dataclass(frozen=True)
class AudioChunk:
    index: int
    path: Path
    offset_start_ms: int
    duration_ms: int


class AudioProcessor:
    def __init__(
        self,
        *,
        chunk_ms: int | None = None,
        ffmpeg_binary: str | None = None,
    ) -> None:
        self.chunk_ms = chunk_ms or settings.transcription_chunk_ms
        self.ffmpeg_binary = ffmpeg_binary or _resolve_ffmpeg_binary()

    def normalize_to_wav(self, source_path: Path, output_dir: Path) -> NormalizedAudio:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{source_path.stem}.normalized.wav"
        command = [
            self.ffmpeg_binary,
            "-y",
            "-i",
            str(source_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-vn",
            str(output_path),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        return NormalizedAudio(
            path=output_path, duration_ms=_wav_duration_ms(output_path)
        )

    def slice_audio(self, normalized_path: Path, output_dir: Path) -> list[AudioChunk]:
        output_dir.mkdir(parents=True, exist_ok=True)
        chunks: list[AudioChunk] = []

        with wave.open(str(normalized_path), "rb") as source:
            params = source.getparams()
            frame_rate = source.getframerate()
            frames_per_chunk = round(frame_rate * self.chunk_ms / 1000)
            chunk_index = 0
            while True:
                frames = source.readframes(frames_per_chunk)
                if not frames:
                    break

                output_path = output_dir / f"chunk_{chunk_index:04d}.wav"
                with wave.open(str(output_path), "wb") as target:
                    target.setparams(params)
                    target.writeframes(frames)

                frame_count = len(frames) // (params.sampwidth * params.nchannels)
                chunks.append(
                    AudioChunk(
                        index=chunk_index,
                        path=output_path,
                        offset_start_ms=chunk_index * self.chunk_ms,
                        duration_ms=round(frame_count / frame_rate * 1000),
                    )
                )
                chunk_index += 1

        return chunks


def _resolve_ffmpeg_binary() -> str:
    if settings.ffmpeg_binary:
        return settings.ffmpeg_binary

    system_binary = shutil.which("ffmpeg")
    if system_binary:
        return system_binary

    return imageio_ffmpeg.get_ffmpeg_exe()


def _wav_duration_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as handle:
        return round(handle.getnframes() / handle.getframerate() * 1000)

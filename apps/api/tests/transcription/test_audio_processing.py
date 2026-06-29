import math
import wave
from pathlib import Path

from app.transcription.audio import AudioProcessor


def test_normalize_wav_to_mono_16khz_and_slice_with_offsets(tmp_path: Path) -> None:
    source_path = tmp_path / "source.wav"
    _write_wave(source_path, sample_rate=8000, duration_ms=2300, channels=2)
    output_dir = tmp_path / "processed"
    processor = AudioProcessor(chunk_ms=1000)

    normalized = processor.normalize_to_wav(source_path, output_dir)
    chunks = processor.slice_audio(normalized.path, output_dir / "chunks")

    assert normalized.duration_ms == 2300
    with wave.open(str(normalized.path), "rb") as normalized_file:
        assert normalized_file.getnchannels() == 1
        assert normalized_file.getframerate() == 16000

    assert [chunk.index for chunk in chunks] == [0, 1, 2]
    assert [chunk.offset_start_ms for chunk in chunks] == [0, 1000, 2000]
    assert [chunk.duration_ms for chunk in chunks] == [1000, 1000, 300]
    assert all(chunk.path.exists() for chunk in chunks)


def _write_wave(
    path: Path, *, sample_rate: int, duration_ms: int, channels: int
) -> None:
    frame_count = math.ceil(sample_rate * duration_ms / 1000)
    amplitude = 8000
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = int(amplitude * math.sin(index / 12))
            sample_bytes = sample.to_bytes(2, "little", signed=True)
            frames.extend(sample_bytes * channels)
        handle.writeframes(bytes(frames))

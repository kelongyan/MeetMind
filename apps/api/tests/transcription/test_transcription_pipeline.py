import math
import wave
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db.models import JobStatus, JobType, ProcessingJob
from app.db.session import SessionLocal
from app.exceptions import ConflictError
from app.main import app
from app.providers.asr.base import TranscribedSegment
from app.providers.asr.dependencies import get_transcriber
from app.transcription import service


class FakeTranscriber:
    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> list[TranscribedSegment]:
        duration_ms = _duration_ms(audio_path)
        return [
            TranscribedSegment(
                start_ms=0,
                end_ms=duration_ms,
                text=f"chunk-{audio_path.stem}",
                confidence=0.92,
            )
        ]


class FailingTranscriber:
    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> list[TranscribedSegment]:
        raise RuntimeError("provider timeout")


@pytest.fixture
def upload_storage_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    storage_dir = tmp_path / "storage"
    monkeypatch.setattr(settings, "upload_storage_dir", str(storage_dir))
    monkeypatch.setattr(settings, "transcription_chunk_ms", 1000)
    return storage_dir


def test_run_transcription_job_writes_segments_with_global_offsets(
    upload_storage_dir: Path, auth_headers: dict[str, str]
) -> None:
    client = TestClient(app)
    meeting_response = client.post(
        "/api/meetings", json={"title": "Transcribe"}, headers=auth_headers
    )
    meeting_id = meeting_response.json()["id"]
    audio_bytes = _wave_bytes(duration_ms=2200)
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("sample.wav", audio_bytes, "audio/wav")},
        headers=auth_headers,
    )
    asset_id = upload_response.json()["asset"]["id"]
    job_id = UUID(upload_response.json()["job"]["id"])

    with SessionLocal() as session:
        result = service.run_transcription_job(
            session, job_id, transcriber=FakeTranscriber()
        )

    assert result.job.status == "succeeded"
    assert result.job.progress == 100
    assert result.asset.duration_ms == 2200
    assert [segment.chunk_index for segment in result.segments] == [0, 1, 2]
    assert [segment.start_ms for segment in result.segments] == [0, 1000, 2000]
    assert [segment.end_ms for segment in result.segments] == [1000, 2000, 2200]
    assert {str(segment.source_asset_id) for segment in result.segments} == {asset_id}

    transcript_response = client.get(
        f"/api/meetings/{meeting_id}/transcript", headers=auth_headers
    )
    assert transcript_response.status_code == 200
    assert [item["start_ms"] for item in transcript_response.json()["items"]] == [
        0,
        1000,
        2000,
    ]


def test_run_transcription_job_endpoint_uses_provider_dependency(
    upload_storage_dir: Path, auth_headers: dict[str, str]
) -> None:
    client = TestClient(app)
    app.dependency_overrides[get_transcriber] = lambda: FakeTranscriber()
    meeting_response = client.post(
        "/api/meetings", json={"title": "Run endpoint"}, headers=auth_headers
    )
    meeting_id = meeting_response.json()["id"]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("endpoint.wav", _wave_bytes(duration_ms=1200), "audio/wav")},
        headers=auth_headers,
    )
    job_id = upload_response.json()["job"]["id"]

    try:
        run_response = client.post(f"/api/jobs/{job_id}/run", headers=auth_headers)
    finally:
        app.dependency_overrides.clear()

    assert run_response.status_code == 200
    body = run_response.json()
    assert body["job"]["status"] == "succeeded"
    assert [segment["start_ms"] for segment in body["segments"]] == [0, 1000]


def test_run_transcription_job_without_auto_process_allows_disabled_pipeline_providers(
    upload_storage_dir: Path,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    client = TestClient(app)
    app.dependency_overrides[get_transcriber] = lambda: FakeTranscriber()
    meeting_id = client.post(
        "/api/meetings",
        json={"title": "Run without pipeline providers"},
        headers=auth_headers,
    ).json()["id"]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("endpoint.wav", _wave_bytes(duration_ms=1200), "audio/wav")},
        headers=auth_headers,
    )
    job_id = upload_response.json()["job"]["id"]
    monkeypatch.setattr(settings, "llm_provider", "disabled")
    monkeypatch.setattr(settings, "embedding_provider", "disabled")

    try:
        run_response = client.post(f"/api/jobs/{job_id}/run", headers=auth_headers)
    finally:
        app.dependency_overrides.clear()

    assert run_response.status_code == 200
    assert run_response.json()["job"]["status"] == "succeeded"


def test_failed_transcription_preserves_existing_transcript(
    upload_storage_dir: Path, auth_headers: dict[str, str]
) -> None:
    client = TestClient(app)
    meeting_response = client.post(
        "/api/meetings", json={"title": "Failure"}, headers=auth_headers
    )
    meeting_id = meeting_response.json()["id"]
    upload_response = client.post(
        f"/api/meetings/{meeting_id}/assets",
        files={"file": ("failure.wav", _wave_bytes(duration_ms=1200), "audio/wav")},
        headers=auth_headers,
    )
    asset_id = upload_response.json()["asset"]["id"]
    job_id = UUID(upload_response.json()["job"]["id"])
    existing_response = client.post(
        f"/api/meetings/{meeting_id}/transcript",
        json={
            "start_ms": 0,
            "end_ms": 500,
            "text": "existing transcript",
            "source_asset_id": asset_id,
        },
        headers=auth_headers,
    )
    assert existing_response.status_code == 201

    with SessionLocal() as session:
        with pytest.raises(RuntimeError):
            service.run_transcription_job(
                session, job_id, transcriber=FailingTranscriber()
            )

    transcript_response = client.get(
        f"/api/meetings/{meeting_id}/transcript", headers=auth_headers
    )
    assert [item["text"] for item in transcript_response.json()["items"]] == [
        "existing transcript"
    ]


def test_run_transcription_job_rejects_asset_from_another_meeting(
    upload_storage_dir: Path, auth_headers: dict[str, str]
) -> None:
    client = TestClient(app)
    source_meeting_id = client.post(
        "/api/meetings", json={"title": "Source audio"}, headers=auth_headers
    ).json()["id"]
    target_meeting_id = client.post(
        "/api/meetings", json={"title": "Target audio"}, headers=auth_headers
    ).json()["id"]
    upload_response = client.post(
        f"/api/meetings/{source_meeting_id}/assets",
        files={"file": ("source.wav", _wave_bytes(duration_ms=1000), "audio/wav")},
        headers=auth_headers,
    )
    asset_id = UUID(upload_response.json()["asset"]["id"])

    with SessionLocal() as session:
        job = ProcessingJob(
            meeting_id=UUID(target_meeting_id),
            job_type=JobType.TRANSCRIBE,
            status=JobStatus.QUEUED,
            input_asset_id=asset_id,
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        with pytest.raises(ConflictError):
            service.run_transcription_job(
                session, job.id, transcriber=FakeTranscriber()
            )


def _wave_bytes(duration_ms: int) -> bytes:
    path = Path.cwd() / ".pytest-audio-source.wav"
    _write_wave(path, sample_rate=16000, duration_ms=duration_ms, channels=1)
    try:
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def _write_wave(
    path: Path, *, sample_rate: int, duration_ms: int, channels: int
) -> None:
    frame_count = math.ceil(sample_rate * duration_ms / 1000)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        frames = bytearray()
        for index in range(frame_count):
            sample = int(8000 * math.sin(index / 16))
            frames.extend(sample.to_bytes(2, "little", signed=True) * channels)
        handle.writeframes(bytes(frames))


def _duration_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as handle:
        return round(handle.getnframes() / handle.getframerate() * 1000)

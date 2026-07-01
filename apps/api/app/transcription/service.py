from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.assets.repository import get_asset
from app.config import settings
from app.db.models import (
    AssetType,
    JobStatus,
    JobType,
    MeetingAsset,
    MeetingSection,
    MeetingStatus,
    ProcessingJob,
    TranscriptSegment,
)
from app.exceptions import ConflictError, NotFoundError
from app.jobs.service import get_processing_job
from app.meetings.service import get_meeting
from app.object_storage.local import LocalObjectStorage
from app.providers.asr.base import Transcriber
from app.retrieval.repository import delete_embeddings_for_meeting
from app.transcription import repository
from app.transcription.audio import AudioProcessor
from app.transcription.schemas import TranscriptSegmentCreate


@dataclass(frozen=True)
class TranscriptionRunResult:
    job: ProcessingJob
    asset: MeetingAsset
    segments: list[TranscriptSegment]


def create_segment(
    session: Session, meeting_id: UUID, payload: TranscriptSegmentCreate
) -> TranscriptSegment:
    get_meeting(session, meeting_id)
    _ensure_source_asset_belongs_to_meeting(session, meeting_id, payload)
    _ensure_speaker_belongs_to_meeting(session, meeting_id, payload)
    segment = TranscriptSegment(meeting_id=meeting_id, **payload.model_dump())
    repository.create_segment(session, segment)
    delete_embeddings_for_meeting(session, meeting_id)
    repository.delete_sections_for_meeting(session, meeting_id)
    session.commit()
    session.refresh(segment)
    return segment


def list_segments(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 200
) -> list[TranscriptSegment]:
    get_meeting(session, meeting_id)
    return repository.list_segments(session, meeting_id, offset=offset, limit=limit)


def count_segments(session: Session, meeting_id: UUID) -> int:
    get_meeting(session, meeting_id)
    return repository.count_segments(session, meeting_id)


def list_sections(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[MeetingSection]:
    get_meeting(session, meeting_id)
    sections = repository.list_sections(session, meeting_id, offset=offset, limit=limit)
    if sections:
        return sections

    # Auto-generate basic sections if none exist (only for first page).
    if offset > 0:
        return []
    all_sections = repository.list_sections(session, meeting_id)
    if all_sections:
        return all_sections

    segments = repository.list_segments(session, meeting_id)
    if not segments:
        return []

    sections = _build_basic_sections(meeting_id, segments)
    for section in sections:
        repository.create_section(session, section)
    session.commit()
    for section in sections:
        session.refresh(section)
    return sections


def count_sections(session: Session, meeting_id: UUID) -> int:
    get_meeting(session, meeting_id)
    return repository.count_sections(session, meeting_id)


def get_segment_for_meeting(
    session: Session, meeting_id: UUID, segment_id: UUID
) -> TranscriptSegment:
    segment = repository.get_segment(session, segment_id)
    if segment is None or segment.meeting_id != meeting_id:
        raise NotFoundError("Transcript segment not found")
    return segment


def run_transcription_job(
    session: Session,
    job_id: UUID,
    *,
    transcriber: Transcriber,
    audio_processor: AudioProcessor | None = None,
) -> TranscriptionRunResult:
    job = get_processing_job(session, job_id)
    if job.job_type != JobType.TRANSCRIBE:
        raise ConflictError("Only transcribe jobs can run transcription")
    if job.input_asset_id is None:
        raise ConflictError("Transcription job requires an input asset")

    meeting = get_meeting(session, job.meeting_id)
    asset = get_asset(session, job.input_asset_id)
    if asset is None or asset.deleted_at is not None:
        raise NotFoundError("Asset not found")
    if asset.meeting_id != job.meeting_id:
        raise ConflictError("Input asset does not belong to this meeting")
    if asset.asset_type not in {AssetType.AUDIO, AssetType.VIDEO}:
        raise ConflictError("Transcription requires an audio or video asset")

    processor = audio_processor or AudioProcessor(
        chunk_ms=settings.transcription_chunk_ms
    )
    storage = LocalObjectStorage(settings.upload_storage_dir)
    source_path = storage.path_for_uri(asset.storage_uri)
    work_dir = Path(settings.transcription_work_dir) / str(job.id)

    job.status = JobStatus.RUNNING
    job.progress = 10
    job.started_at = job.started_at or datetime.now(UTC)
    meeting.status = MeetingStatus.TRANSCRIBING
    session.commit()

    try:
        normalized = processor.normalize_to_wav(source_path, work_dir)
        chunks = processor.slice_audio(normalized.path, work_dir / "chunks")
        repository.delete_segments_for_asset(session, asset.id)
        repository.delete_sections_for_meeting(session, job.meeting_id)
        delete_embeddings_for_meeting(session, job.meeting_id)
        segments: list[TranscriptSegment] = []

        for chunk in chunks:
            for result in transcriber.transcribe(chunk.path, meeting.language):
                segment = TranscriptSegment(
                    meeting_id=job.meeting_id,
                    source_asset_id=asset.id,
                    chunk_index=chunk.index,
                    start_ms=chunk.offset_start_ms + result.start_ms,
                    end_ms=min(
                        chunk.offset_start_ms + result.end_ms,
                        chunk.offset_start_ms + chunk.duration_ms,
                    ),
                    text=result.text,
                    confidence=result.confidence,
                )
                repository.create_segment(session, segment)
                segments.append(segment)

        asset.duration_ms = normalized.duration_ms
        job.status = JobStatus.SUCCEEDED
        job.progress = 100
        job.finished_at = datetime.now(UTC)
        meeting.status = MeetingStatus.SEGMENTING
        session.commit()
        for segment in segments:
            session.refresh(segment)
        session.refresh(asset)
        session.refresh(job)
        return TranscriptionRunResult(job=job, asset=asset, segments=segments)
    except Exception as exc:
        session.rollback()
        job = get_processing_job(session, job_id)
        meeting = get_meeting(session, job.meeting_id)
        failed_at = datetime.now(UTC)
        job.status = JobStatus.FAILED
        job.progress = 100
        job.failure_code = "transcription_failed"
        job.failure_message = str(exc)
        job.retryable = True
        job.failed_at = failed_at
        job.finished_at = failed_at
        meeting.status = MeetingStatus.FAILED_TRANSCRIPTION
        session.commit()
        raise


def _ensure_source_asset_belongs_to_meeting(
    session: Session, meeting_id: UUID, payload: TranscriptSegmentCreate
) -> None:
    if payload.source_asset_id is None:
        return

    asset = get_asset(session, payload.source_asset_id)
    if asset is None or asset.deleted_at is not None:
        raise NotFoundError("Source asset not found")
    if asset.meeting_id != meeting_id:
        raise ConflictError("Source asset does not belong to this meeting")


def _ensure_speaker_belongs_to_meeting(
    session: Session, meeting_id: UUID, payload: TranscriptSegmentCreate
) -> None:
    if payload.speaker_id is None:
        return

    speaker = repository.get_speaker(session, payload.speaker_id)
    if speaker is None:
        raise NotFoundError("Speaker not found")
    if speaker.meeting_id != meeting_id:
        raise ConflictError("Speaker does not belong to this meeting")


def _build_basic_sections(
    meeting_id: UUID, segments: list[TranscriptSegment], *, group_size: int = 5
) -> list[MeetingSection]:
    sections: list[MeetingSection] = []
    for index in range(0, len(segments), group_size):
        group = segments[index : index + group_size]
        sections.append(
            MeetingSection(
                meeting_id=meeting_id,
                title=_section_title_from_text(group[0].text),
                summary=None,
                start_ms=group[0].start_ms,
                end_ms=group[-1].end_ms,
                topic_tags=["auto"],
            )
        )
    return sections


def _section_title_from_text(text: str) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= 48:
        return normalized
    return f"{normalized[:45]}..."

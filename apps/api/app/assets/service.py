from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.assets import repository
from app.config import settings
from app.db.models import AssetType, JobStatus, JobType, MeetingAsset, ProcessingJob
from app.exceptions import InvalidFileTypeError, NotFoundError
from app.jobs.repository import create_job
from app.meetings.service import get_meeting
from app.object_storage.local import LocalObjectStorage

ALLOWED_SUFFIXES: dict[str, AssetType] = {
    ".mp3": AssetType.AUDIO,
    ".wav": AssetType.AUDIO,
    ".m4a": AssetType.AUDIO,
    ".mp4": AssetType.VIDEO,
    ".webm": AssetType.VIDEO,
    ".txt": AssetType.TRANSCRIPT,
    ".srt": AssetType.SUBTITLE,
    ".vtt": AssetType.SUBTITLE,
}


@dataclass(frozen=True)
class AssetUploadResult:
    asset: MeetingAsset
    job: ProcessingJob | None
    duplicate: bool


async def upload_asset(
    session: Session, meeting_id: UUID, upload: UploadFile
) -> AssetUploadResult:
    get_meeting(session, meeting_id)
    suffix = _validate_file_suffix(upload.filename)
    asset_type = ALLOWED_SUFFIXES[suffix]
    storage = LocalObjectStorage(settings.upload_storage_dir)
    stored = await storage.save_upload(meeting_id, upload, suffix)

    existing_asset = repository.find_active_asset_by_hash(
        session, meeting_id, stored.sha256
    )
    if existing_asset is not None:
        return AssetUploadResult(asset=existing_asset, job=None, duplicate=True)

    asset = MeetingAsset(
        meeting_id=meeting_id,
        asset_type=asset_type,
        storage_uri=stored.storage_uri,
        original_filename=Path(upload.filename or "").name or None,
        mime_type=upload.content_type,
        size_bytes=stored.size_bytes,
        sha256=stored.sha256,
    )
    repository.create_asset(session, asset)
    session.flush()

    job = ProcessingJob(
        meeting_id=meeting_id,
        job_type=_job_type_for_asset(asset_type),
        status=JobStatus.QUEUED,
        progress=0,
        provider="local-upload",
        input_asset_id=asset.id,
    )
    create_job(session, job)
    session.commit()
    session.refresh(asset)
    session.refresh(job)
    return AssetUploadResult(asset=asset, job=job, duplicate=False)


def list_assets(session: Session, meeting_id: UUID) -> list[MeetingAsset]:
    get_meeting(session, meeting_id)
    return repository.list_assets(session, meeting_id)


def delete_asset(session: Session, asset_id: UUID) -> None:
    asset = repository.get_asset(session, asset_id)
    if asset is None or asset.deleted_at is not None:
        raise NotFoundError("Asset not found")

    asset.deleted_at = datetime.now(UTC)
    LocalObjectStorage(settings.upload_storage_dir).delete_uri(asset.storage_uri)
    session.commit()


def _validate_file_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise InvalidFileTypeError()
    return suffix


def _job_type_for_asset(asset_type: AssetType) -> JobType:
    if asset_type in {AssetType.AUDIO, AssetType.VIDEO}:
        return JobType.TRANSCRIBE
    return JobType.STRUCTURE

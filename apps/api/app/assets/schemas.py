from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.models import AssetType
from app.jobs.schemas import ProcessingJobRead


class MeetingAssetRead(BaseModel):
    id: UUID
    meeting_id: UUID
    asset_type: AssetType
    storage_uri: str
    original_filename: str | None
    mime_type: str | None
    size_bytes: int | None
    sha256: str | None
    duration_ms: int | None
    created_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AssetUploadRead(BaseModel):
    asset: MeetingAssetRead
    job: ProcessingJobRead | None
    duplicate: bool

    model_config = ConfigDict(from_attributes=True)

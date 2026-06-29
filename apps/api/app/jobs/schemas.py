from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import JobStatus, JobType


class ProcessingJobCreate(BaseModel):
    job_type: JobType
    provider: str | None = None
    input_asset_id: UUID | None = None


class ProcessingJobRead(BaseModel):
    id: UUID
    meeting_id: UUID
    job_type: JobType
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    provider: str | None
    input_asset_id: UUID | None
    failure_code: str | None
    failure_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

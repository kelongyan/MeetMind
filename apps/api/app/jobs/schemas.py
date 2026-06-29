from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    retry_of_job_id: UUID | None
    attempt_number: int
    failure_code: str | None
    failure_message: str | None
    retryable: bool
    failed_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcessingJobUpdate(BaseModel):
    status: JobStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    provider: str | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    retryable: bool | None = None

    @model_validator(mode="after")
    def validate_failed_job_details(self) -> "ProcessingJobUpdate":
        if self.status == JobStatus.FAILED and (
            not self.failure_code or not self.failure_message
        ):
            raise ValueError("failed jobs require failure_code and failure_message")
        return self

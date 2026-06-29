from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TranscriptSegmentCreate(BaseModel):
    speaker_id: UUID | None = None
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)
    text: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_asset_id: UUID | None = None
    chunk_index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_time_range(self) -> "TranscriptSegmentCreate":
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms must be greater than or equal to start_ms")
        return self


class TranscriptSegmentRead(BaseModel):
    id: UUID
    meeting_id: UUID
    speaker_id: UUID | None
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None
    source_asset_id: UUID | None
    chunk_index: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

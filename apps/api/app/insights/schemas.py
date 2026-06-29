from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.db.models import (
    ActionItemStatus,
    CitationTargetType,
    InsightStatus,
    InsightType,
)


class InsightItemCreate(BaseModel):
    section_id: UUID | None = None
    type: InsightType
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    status: InsightStatus = InsightStatus.PROPOSED
    confidence: float | None = Field(default=None, ge=0, le=1)
    model_name: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None


class InsightItemRead(BaseModel):
    id: UUID
    meeting_id: UUID
    section_id: UUID | None
    type: InsightType
    title: str
    body: str
    status: InsightStatus
    confidence: float | None
    model_name: str | None
    model_version: str | None
    prompt_version: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionItemCreate(BaseModel):
    section_id: UUID | None = None
    description: str = Field(min_length=1)
    owner_text: str | None = None
    owner_user_id: str | None = None
    due_text: str | None = None
    due_date: date | None = None
    status: ActionItemStatus = ActionItemStatus.PROPOSED
    confidence: float | None = Field(default=None, ge=0, le=1)
    created_by_ai: bool = True
    confirmed_by_user_id: str | None = None
    confirmed_at: datetime | None = None


class ActionItemRead(BaseModel):
    id: UUID
    meeting_id: UUID
    section_id: UUID | None
    description: str
    owner_text: str | None
    owner_user_id: str | None
    due_text: str | None
    due_date: date | None
    status: ActionItemStatus
    confidence: float | None
    created_by_ai: bool
    confirmed_by_user_id: str | None
    confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CitationCreate(BaseModel):
    target_type: CitationTargetType
    target_id: UUID
    segment_id: UUID
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)
    quote: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def validate_time_range(self) -> "CitationCreate":
        if self.end_ms < self.start_ms:
            raise ValueError("end_ms must be greater than or equal to start_ms")
        return self


class CitationRead(BaseModel):
    id: UUID
    meeting_id: UUID
    target_type: CitationTargetType
    target_id: UUID
    segment_id: UUID
    start_ms: int
    end_ms: int
    quote: str
    confidence: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

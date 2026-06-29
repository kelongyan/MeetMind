from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import CitationTargetType, QAMessageRole


class QAQuestionCreate(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None


class QAMessageRead(BaseModel):
    id: UUID
    meeting_id: UUID
    conversation_id: UUID
    role: QAMessageRole
    content: str
    citation_ids: list[str]
    model_name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QACitationRead(BaseModel):
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


class QAAnswerRead(BaseModel):
    conversation_id: UUID
    question: QAMessageRead
    answer: QAMessageRead
    citations: list[QACitationRead]

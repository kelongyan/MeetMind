from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.insights.schemas import ActionItemRead, CitationRead


class KnowledgeSearchResultRead(BaseModel):
    meeting_id: UUID
    meeting_title: str
    source_type: str
    source_id: UUID
    segment_id: UUID | None
    start_ms: int | None
    end_ms: int | None
    title: str
    snippet: str
    created_at: datetime
    score: float | None = None


class KnowledgeDecisionRead(BaseModel):
    id: UUID
    meeting_id: UUID
    meeting_title: str
    title: str
    body: str
    status: str
    confidence: float | None
    created_at: datetime
    citations: list[CitationRead]

    model_config = ConfigDict(from_attributes=True)


class DuplicateActionGroupRead(BaseModel):
    reason: str
    items: list[ActionItemRead]

    model_config = ConfigDict(from_attributes=True)

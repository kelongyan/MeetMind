from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.insights.schemas import ActionItemRead, CitationRead, InsightItemRead
from app.jobs.schemas import ProcessingJobRead


class StructuredCitationDraft(BaseModel):
    segment_id: UUID
    start_ms: int | None = Field(default=None, ge=0)
    end_ms: int | None = Field(default=None, ge=0)
    quote: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def validate_time_range(self) -> StructuredCitationDraft:
        if (
            self.start_ms is not None
            and self.end_ms is not None
            and self.end_ms < self.start_ms
        ):
            raise ValueError(
                "citation end_ms must be greater than or equal to start_ms"
            )
        return self


class StructuredMeetingBrief(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    citations: list[StructuredCitationDraft] = Field(default_factory=list)


class StructuredInsightDraft(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    citations: list[StructuredCitationDraft] = Field(default_factory=list)


class StructuredActionItemDraft(BaseModel):
    description: str = Field(min_length=1)
    owner_text: str | None = None
    due_text: str | None = None
    due_date: date | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    citations: list[StructuredCitationDraft] = Field(default_factory=list)


class StructuredMeetingExtraction(BaseModel):
    meeting_brief: StructuredMeetingBrief | None = None
    discussion_points: list[StructuredInsightDraft] = Field(default_factory=list)
    decisions: list[StructuredInsightDraft] = Field(default_factory=list)
    risks: list[StructuredInsightDraft] = Field(default_factory=list)
    open_questions: list[StructuredInsightDraft] = Field(default_factory=list)
    action_items: list[StructuredActionItemDraft] = Field(default_factory=list)


class StructuringRunRead(BaseModel):
    job: ProcessingJobRead
    insights: list[InsightItemRead]
    action_items: list[ActionItemRead]
    citations: list[CitationRead]

    model_config = ConfigDict(from_attributes=True)

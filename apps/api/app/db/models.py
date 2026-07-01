from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


def enum_type(enum_cls: type[StrEnum]) -> SQLEnum:
    return SQLEnum(
        enum_cls,
        values_callable=lambda values: [item.value for item in values],
        native_enum=False,
        length=64,
    )


class MeetingStatus(StrEnum):
    UPLOADED = "uploaded"
    MEDIA_PROCESSING = "media_processing"
    TRANSCRIBING = "transcribing"
    SEGMENTING = "segmenting"
    STRUCTURING = "structuring"
    CITING = "citing"
    EMBEDDING = "embedding"
    READY_FOR_REVIEW = "ready_for_review"
    PUBLISHED = "published"
    FAILED_MEDIA_PROCESSING = "failed_media_processing"
    FAILED_TRANSCRIPTION = "failed_transcription"
    FAILED_STRUCTURING = "failed_structuring"
    FAILED_EMBEDDING = "failed_embedding"


class AssetType(StrEnum):
    AUDIO = "audio"
    VIDEO = "video"
    TRANSCRIPT = "transcript"
    SUBTITLE = "subtitle"
    EXPORT = "export"


class JobType(StrEnum):
    TRANSCRIBE = "transcribe"
    STRUCTURE = "structure"
    EMBED = "embed"
    EXPORT = "export"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class InsightType(StrEnum):
    DISCUSSION_POINT = "discussion_point"
    DECISION = "decision"
    RISK = "risk"
    OPEN_QUESTION = "open_question"


class InsightStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


class ActionItemStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class CitationTargetType(StrEnum):
    INSIGHT_ITEM = "insight_item"
    ACTION_ITEM = "action_item"
    ANSWER = "answer"


class EmbeddingSourceType(StrEnum):
    TRANSCRIPT_SEGMENT = "transcript_segment"
    MEETING_SECTION = "meeting_section"
    INSIGHT_ITEM = "insight_item"
    ACTION_ITEM = "action_item"


class QAMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[str | None] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[MeetingStatus] = mapped_column(
        enum_type(MeetingStatus), default=MeetingStatus.UPLOADED
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    assets: Mapped[list[MeetingAsset]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[ProcessingJob]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    speakers: Mapped[list[Speaker]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    transcript_segments: Mapped[list[TranscriptSegment]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    sections: Mapped[list[MeetingSection]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    insight_items: Mapped[list[InsightItem]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    action_items: Mapped[list[ActionItem]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    citations: Mapped[list[Citation]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    embeddings: Mapped[list[EmbeddingRecord]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    qa_messages: Mapped[list[QAMessage]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )


class MeetingAsset(Base):
    __tablename__ = "meeting_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    asset_type: Mapped[AssetType] = mapped_column(enum_type(AssetType))
    storage_uri: Mapped[str] = mapped_column(Text)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    sha256: Mapped[str | None] = mapped_column(String(64), index=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    meeting: Mapped[Meeting] = relationship(back_populates="assets")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    job_type: Mapped[JobType] = mapped_column(enum_type(JobType))
    status: Mapped[JobStatus] = mapped_column(
        enum_type(JobStatus), default=JobStatus.QUEUED
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    provider: Mapped[str | None] = mapped_column(String(128))
    input_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meeting_assets.id", ondelete="SET NULL")
    )
    retry_of_job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="SET NULL")
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    failure_code: Mapped[str | None] = mapped_column(String(128))
    failure_message: Mapped[str | None] = mapped_column(Text)
    retryable: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="jobs")


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    display_name: Mapped[str] = mapped_column(String(255))
    canonical_user_id: Mapped[str | None] = mapped_column(String(128))
    confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="speakers")
    transcript_segments: Mapped[list[TranscriptSegment]] = relationship(
        back_populates="speaker"
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    speaker_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("speakers.id", ondelete="SET NULL")
    )
    start_ms: Mapped[int] = mapped_column(Integer)
    end_ms: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    source_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meeting_assets.id", ondelete="SET NULL")
    )
    chunk_index: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="transcript_segments")
    speaker: Mapped[Speaker | None] = relationship(back_populates="transcript_segments")


class MeetingSection(Base):
    __tablename__ = "meeting_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    start_ms: Mapped[int | None] = mapped_column(Integer)
    end_ms: Mapped[int | None] = mapped_column(Integer)
    topic_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="sections")


class InsightItem(Base):
    __tablename__ = "insight_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meeting_sections.id", ondelete="SET NULL")
    )
    type: Mapped[InsightType] = mapped_column(enum_type(InsightType))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[InsightStatus] = mapped_column(
        enum_type(InsightStatus), default=InsightStatus.PROPOSED
    )
    confidence: Mapped[float | None] = mapped_column(Float)
    model_name: Mapped[str | None] = mapped_column(String(128))
    model_version: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="insight_items")


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meeting_sections.id", ondelete="SET NULL")
    )
    description: Mapped[str] = mapped_column(Text)
    owner_text: Mapped[str | None] = mapped_column(String(255))
    owner_user_id: Mapped[str | None] = mapped_column(String(128))
    due_text: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ActionItemStatus] = mapped_column(
        enum_type(ActionItemStatus), default=ActionItemStatus.PROPOSED
    )
    confidence: Mapped[float | None] = mapped_column(Float)
    model_name: Mapped[str | None] = mapped_column(String(128))
    model_version: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[str | None] = mapped_column(String(128))
    created_by_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed_by_user_id: Mapped[str | None] = mapped_column(String(128))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="action_items")


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    target_type: Mapped[CitationTargetType] = mapped_column(
        enum_type(CitationTargetType)
    )
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    segment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("transcript_segments.id", ondelete="CASCADE"),
        index=True,
    )
    start_ms: Mapped[int] = mapped_column(Integer)
    end_ms: Mapped[int] = mapped_column(Integer)
    quote: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="citations")


class EmbeddingRecord(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[EmbeddingSourceType] = mapped_column(
        enum_type(EmbeddingSourceType)
    )
    source_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    embedding_model: Mapped[str] = mapped_column(String(128))
    vector: Mapped[list[float]] = mapped_column(Vector(1536))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="embeddings")


class QAMessage(Base):
    __tablename__ = "qa_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), index=True
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    role: Mapped[QAMessageRole] = mapped_column(enum_type(QAMessageRole))
    content: Mapped[str] = mapped_column(Text)
    citation_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    model_name: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    meeting: Mapped[Meeting] = relationship(back_populates="qa_messages")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(enum_type(UserRole), default=UserRole.MEMBER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ProviderTelemetryRecord(Base):
    __tablename__ = "provider_telemetry"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider: Mapped[str] = mapped_column(String(128), index=True)
    operation: Mapped[str] = mapped_column(String(128))
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[str | None] = mapped_column(String(128))
    latency_ms: Mapped[int] = mapped_column(Integer)
    estimated_units: Mapped[int] = mapped_column(Integer, default=0)
    cost_estimate_usd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32))
    failure_type: Mapped[str | None] = mapped_column(String(128))
    failure_message: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )

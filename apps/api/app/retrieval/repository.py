from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import (
    ActionItem,
    Citation,
    CitationTargetType,
    EmbeddingRecord,
    InsightItem,
    MeetingSection,
    TranscriptSegment,
)


def delete_embeddings_for_meeting(session: Session, meeting_id: UUID) -> None:
    session.execute(
        delete(EmbeddingRecord).where(EmbeddingRecord.meeting_id == meeting_id)
    )


def create_embedding(session: Session, embedding: EmbeddingRecord) -> EmbeddingRecord:
    session.add(embedding)
    return embedding


def count_embeddings_for_meeting(session: Session, meeting_id: UUID) -> int:
    from sqlalchemy import func

    return (
        session.scalar(
            select(func.count())
            .select_from(EmbeddingRecord)
            .where(EmbeddingRecord.meeting_id == meeting_id)
        )
        or 0
    )


def list_embedding_models_for_meeting(session: Session, meeting_id: UUID) -> set[str]:
    return set(
        session.scalars(
            select(EmbeddingRecord.embedding_model)
            .where(EmbeddingRecord.meeting_id == meeting_id)
            .distinct()
        )
    )


def list_transcript_segments(
    session: Session, meeting_id: UUID
) -> list[TranscriptSegment]:
    return list(
        session.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.start_ms, TranscriptSegment.id)
        )
    )


def list_sections(session: Session, meeting_id: UUID) -> list[MeetingSection]:
    return list(
        session.scalars(
            select(MeetingSection)
            .where(MeetingSection.meeting_id == meeting_id)
            .order_by(MeetingSection.start_ms, MeetingSection.id)
        )
    )


def list_insights(session: Session, meeting_id: UUID) -> list[InsightItem]:
    return list(
        session.scalars(
            select(InsightItem)
            .where(InsightItem.meeting_id == meeting_id)
            .order_by(InsightItem.created_at, InsightItem.id)
        )
    )


def list_action_items(session: Session, meeting_id: UUID) -> list[ActionItem]:
    return list(
        session.scalars(
            select(ActionItem)
            .where(ActionItem.meeting_id == meeting_id)
            .order_by(ActionItem.created_at, ActionItem.id)
        )
    )


def search_embeddings(
    session: Session,
    meeting_id: UUID,
    query_vector: list[float],
    *,
    limit: int,
) -> list[tuple[EmbeddingRecord, float]]:
    distance = EmbeddingRecord.vector.cosine_distance(query_vector).label("distance")
    rows = session.execute(
        select(EmbeddingRecord, distance)
        .where(EmbeddingRecord.meeting_id == meeting_id)
        .order_by(distance, EmbeddingRecord.id)
        .limit(limit)
    ).all()
    return [(row[0], float(row[1])) for row in rows]


def get_transcript_segment(
    session: Session, segment_id: UUID
) -> TranscriptSegment | None:
    return session.get(TranscriptSegment, segment_id)


def get_insight(session: Session, insight_id: UUID) -> InsightItem | None:
    return session.get(InsightItem, insight_id)


def get_action_item(session: Session, action_item_id: UUID) -> ActionItem | None:
    return session.get(ActionItem, action_item_id)


def get_section(session: Session, section_id: UUID) -> MeetingSection | None:
    return session.get(MeetingSection, section_id)


def list_citations_for_target(
    session: Session,
    meeting_id: UUID,
    target_type: CitationTargetType,
    target_id: UUID,
) -> list[Citation]:
    return list(
        session.scalars(
            select(Citation)
            .where(
                Citation.meeting_id == meeting_id,
                Citation.target_type == target_type,
                Citation.target_id == target_id,
            )
            .order_by(Citation.start_ms, Citation.id)
        )
    )

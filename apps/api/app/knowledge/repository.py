from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ActionItem,
    Citation,
    CitationTargetType,
    InsightItem,
    InsightType,
    Meeting,
    TranscriptSegment,
)


def list_meetings_for_workspace(session: Session, workspace_id: str) -> list[Meeting]:
    return list(
        session.scalars(
            select(Meeting)
            .where(Meeting.workspace_id == workspace_id)
            .order_by(Meeting.created_at, Meeting.id)
        )
    )


def list_transcript_segments_for_meetings(
    session: Session, meeting_ids: list[UUID]
) -> list[TranscriptSegment]:
    if not meeting_ids:
        return []
    return list(
        session.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id.in_(meeting_ids))
            .order_by(TranscriptSegment.created_at, TranscriptSegment.id)
        )
    )


def list_insights_for_meetings(
    session: Session,
    meeting_ids: list[UUID],
    *,
    insight_type: InsightType | None = None,
) -> list[InsightItem]:
    if not meeting_ids:
        return []
    query = select(InsightItem).where(InsightItem.meeting_id.in_(meeting_ids))
    if insight_type is not None:
        query = query.where(InsightItem.type == insight_type)
    return list(session.scalars(query.order_by(InsightItem.created_at, InsightItem.id)))


def list_action_items_for_meetings(
    session: Session, meeting_ids: list[UUID]
) -> list[ActionItem]:
    if not meeting_ids:
        return []
    return list(
        session.scalars(
            select(ActionItem)
            .where(ActionItem.meeting_id.in_(meeting_ids))
            .order_by(ActionItem.created_at, ActionItem.id)
        )
    )


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
            .order_by(Citation.created_at, Citation.id)
        )
    )

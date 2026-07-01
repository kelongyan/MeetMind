from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.models import (
    ActionItem,
    ActionItemStatus,
    Citation,
    InsightItem,
    MeetingSection,
    QAMessage,
)


def create_insight(session: Session, insight: InsightItem) -> InsightItem:
    session.add(insight)
    return insight


def list_insights(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[InsightItem]:
    return list(
        session.scalars(
            select(InsightItem)
            .where(InsightItem.meeting_id == meeting_id)
            .order_by(InsightItem.created_at, InsightItem.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_insights(session: Session, meeting_id: UUID) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(InsightItem)
            .where(InsightItem.meeting_id == meeting_id)
        )
        or 0
    )


def create_action_item(session: Session, action_item: ActionItem) -> ActionItem:
    session.add(action_item)
    return action_item


def list_action_items(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[ActionItem]:
    return list(
        session.scalars(
            select(ActionItem)
            .where(ActionItem.meeting_id == meeting_id)
            .order_by(ActionItem.created_at, ActionItem.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_action_items(session: Session, meeting_id: UUID) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(ActionItem)
            .where(ActionItem.meeting_id == meeting_id)
        )
        or 0
    )


def list_global_action_items(
    session: Session,
    *,
    status: ActionItemStatus | None = None,
    meeting_id: UUID | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[ActionItem]:
    query: Select[tuple[ActionItem]] = select(ActionItem)
    if status is not None:
        query = query.where(ActionItem.status == status)
    if meeting_id is not None:
        query = query.where(ActionItem.meeting_id == meeting_id)
    return list(
        session.scalars(
            query.order_by(ActionItem.created_at, ActionItem.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_global_action_items(
    session: Session,
    *,
    status: ActionItemStatus | None = None,
    meeting_id: UUID | None = None,
) -> int:
    query = select(func.count()).select_from(ActionItem)
    if status is not None:
        query = query.where(ActionItem.status == status)
    if meeting_id is not None:
        query = query.where(ActionItem.meeting_id == meeting_id)
    return session.scalar(query) or 0


def get_action_item(session: Session, action_item_id: UUID) -> ActionItem | None:
    return session.get(ActionItem, action_item_id)


def get_insight(session: Session, insight_id: UUID) -> InsightItem | None:
    return session.get(InsightItem, insight_id)


def get_section(session: Session, section_id: UUID) -> MeetingSection | None:
    return session.get(MeetingSection, section_id)


def get_qa_message(session: Session, message_id: UUID) -> QAMessage | None:
    return session.get(QAMessage, message_id)


def create_citation(session: Session, citation: Citation) -> Citation:
    session.add(citation)
    return citation


def list_citations(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[Citation]:
    return list(
        session.scalars(
            select(Citation)
            .where(Citation.meeting_id == meeting_id)
            .order_by(Citation.created_at, Citation.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_citations(session: Session, meeting_id: UUID) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(Citation)
            .where(Citation.meeting_id == meeting_id)
        )
        or 0
    )

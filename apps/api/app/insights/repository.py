from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ActionItem, Citation, InsightItem


def create_insight(session: Session, insight: InsightItem) -> InsightItem:
    session.add(insight)
    return insight


def list_insights(session: Session, meeting_id: UUID) -> list[InsightItem]:
    return list(
        session.scalars(
            select(InsightItem)
            .where(InsightItem.meeting_id == meeting_id)
            .order_by(InsightItem.created_at, InsightItem.id)
        )
    )


def create_action_item(session: Session, action_item: ActionItem) -> ActionItem:
    session.add(action_item)
    return action_item


def list_action_items(session: Session, meeting_id: UUID) -> list[ActionItem]:
    return list(
        session.scalars(
            select(ActionItem)
            .where(ActionItem.meeting_id == meeting_id)
            .order_by(ActionItem.created_at, ActionItem.id)
        )
    )


def get_action_item(session: Session, action_item_id: UUID) -> ActionItem | None:
    return session.get(ActionItem, action_item_id)


def get_insight(session: Session, insight_id: UUID) -> InsightItem | None:
    return session.get(InsightItem, insight_id)


def create_citation(session: Session, citation: Citation) -> Citation:
    session.add(citation)
    return citation


def list_citations(session: Session, meeting_id: UUID) -> list[Citation]:
    return list(
        session.scalars(
            select(Citation)
            .where(Citation.meeting_id == meeting_id)
            .order_by(Citation.created_at, Citation.id)
        )
    )

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import (
    ActionItem,
    ActionItemStatus,
    Citation,
    CitationTargetType,
    InsightItem,
    InsightStatus,
)


def create_insight(session: Session, insight: InsightItem) -> InsightItem:
    session.add(insight)
    return insight


def create_action_item(session: Session, action_item: ActionItem) -> ActionItem:
    session.add(action_item)
    return action_item


def create_citation(session: Session, citation: Citation) -> Citation:
    session.add(citation)
    return citation


def delete_generated_outputs(
    session: Session, meeting_id: UUID, *, prompt_version: str
) -> None:
    insight_ids = list(
        session.scalars(
            select(InsightItem.id).where(
                InsightItem.meeting_id == meeting_id,
                InsightItem.status == InsightStatus.PROPOSED,
                InsightItem.prompt_version == prompt_version,
            )
        )
    )
    action_item_ids = list(
        session.scalars(
            select(ActionItem.id).where(
                ActionItem.meeting_id == meeting_id,
                ActionItem.status == ActionItemStatus.PROPOSED,
                ActionItem.created_by_ai.is_(True),
                ActionItem.prompt_version == prompt_version,
            )
        )
    )

    if insight_ids:
        session.execute(
            delete(Citation).where(
                Citation.meeting_id == meeting_id,
                Citation.target_type == CitationTargetType.INSIGHT_ITEM,
                Citation.target_id.in_(insight_ids),
            )
        )
        session.execute(delete(InsightItem).where(InsightItem.id.in_(insight_ids)))

    if action_item_ids:
        session.execute(
            delete(Citation).where(
                Citation.meeting_id == meeting_id,
                Citation.target_type == CitationTargetType.ACTION_ITEM,
                Citation.target_id.in_(action_item_ids),
            )
        )
        session.execute(delete(ActionItem).where(ActionItem.id.in_(action_item_ids)))

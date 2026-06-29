from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import (
    ActionItem,
    ActionItemStatus,
    Citation,
    CitationTargetType,
    InsightItem,
)
from app.exceptions import ConflictError, NotFoundError
from app.insights import repository
from app.insights.schemas import (
    ActionItemCreate,
    ActionItemUpdate,
    CitationCreate,
    InsightItemCreate,
    InsightItemUpdate,
)
from app.meetings.service import get_meeting
from app.retrieval.repository import delete_embeddings_for_meeting
from app.transcription.service import get_segment_for_meeting

ACTION_ITEM_TRANSITIONS: dict[ActionItemStatus, set[ActionItemStatus]] = {
    ActionItemStatus.PROPOSED: {
        ActionItemStatus.CONFIRMED,
        ActionItemStatus.CANCELED,
    },
    ActionItemStatus.CONFIRMED: {
        ActionItemStatus.IN_PROGRESS,
        ActionItemStatus.DONE,
        ActionItemStatus.CANCELED,
    },
    ActionItemStatus.IN_PROGRESS: {
        ActionItemStatus.DONE,
        ActionItemStatus.CANCELED,
    },
    ActionItemStatus.DONE: {ActionItemStatus.DONE},
    ActionItemStatus.CANCELED: {ActionItemStatus.CANCELED},
}


def create_insight(
    session: Session, meeting_id: UUID, payload: InsightItemCreate
) -> InsightItem:
    get_meeting(session, meeting_id)
    insight = InsightItem(meeting_id=meeting_id, **payload.model_dump())
    repository.create_insight(session, insight)
    session.commit()
    session.refresh(insight)
    return insight


def list_insights(session: Session, meeting_id: UUID) -> list[InsightItem]:
    get_meeting(session, meeting_id)
    return repository.list_insights(session, meeting_id)


def update_insight(
    session: Session,
    meeting_id: UUID,
    insight_id: UUID,
    payload: InsightItemUpdate,
) -> InsightItem:
    insight = _get_insight_for_meeting(session, meeting_id, insight_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(insight, field, value)
    delete_embeddings_for_meeting(session, meeting_id)
    session.commit()
    session.refresh(insight)
    return insight


def create_action_item(
    session: Session, meeting_id: UUID, payload: ActionItemCreate
) -> ActionItem:
    get_meeting(session, meeting_id)
    action_item = ActionItem(meeting_id=meeting_id, **payload.model_dump())
    repository.create_action_item(session, action_item)
    session.commit()
    session.refresh(action_item)
    return action_item


def list_action_items(session: Session, meeting_id: UUID) -> list[ActionItem]:
    get_meeting(session, meeting_id)
    return repository.list_action_items(session, meeting_id)


def update_action_item(
    session: Session,
    meeting_id: UUID,
    action_item_id: UUID,
    payload: ActionItemUpdate,
) -> ActionItem:
    action_item = _get_action_item_for_meeting(session, meeting_id, action_item_id)
    data = payload.model_dump(exclude_unset=True)
    next_status = data.pop("status", None)

    for field, value in data.items():
        setattr(action_item, field, value)

    if next_status is not None:
        _apply_action_item_status(action_item, next_status, payload)

    delete_embeddings_for_meeting(session, meeting_id)
    session.commit()
    session.refresh(action_item)
    return action_item


def create_citation(
    session: Session, meeting_id: UUID, payload: CitationCreate
) -> Citation:
    get_meeting(session, meeting_id)
    get_segment_for_meeting(session, meeting_id, payload.segment_id)
    _ensure_target_belongs_to_meeting(session, meeting_id, payload)
    citation = Citation(meeting_id=meeting_id, **payload.model_dump())
    repository.create_citation(session, citation)
    session.commit()
    session.refresh(citation)
    return citation


def list_citations(session: Session, meeting_id: UUID) -> list[Citation]:
    get_meeting(session, meeting_id)
    return repository.list_citations(session, meeting_id)


def _ensure_target_belongs_to_meeting(
    session: Session, meeting_id: UUID, payload: CitationCreate
) -> None:
    if payload.target_type == CitationTargetType.ACTION_ITEM:
        action_item = repository.get_action_item(session, payload.target_id)
        if action_item is None or action_item.meeting_id != meeting_id:
            raise NotFoundError("Action item not found")
    if payload.target_type == CitationTargetType.INSIGHT_ITEM:
        insight = repository.get_insight(session, payload.target_id)
        if insight is None or insight.meeting_id != meeting_id:
            raise NotFoundError("Insight item not found")


def _get_action_item_for_meeting(
    session: Session, meeting_id: UUID, action_item_id: UUID
) -> ActionItem:
    get_meeting(session, meeting_id)
    action_item = repository.get_action_item(session, action_item_id)
    if action_item is None or action_item.meeting_id != meeting_id:
        raise NotFoundError("Action item not found")
    return action_item


def _get_insight_for_meeting(
    session: Session, meeting_id: UUID, insight_id: UUID
) -> InsightItem:
    get_meeting(session, meeting_id)
    insight = repository.get_insight(session, insight_id)
    if insight is None or insight.meeting_id != meeting_id:
        raise NotFoundError("Insight item not found")
    return insight


def _apply_action_item_status(
    action_item: ActionItem,
    next_status: ActionItemStatus,
    payload: ActionItemUpdate,
) -> None:
    current_status = action_item.status
    if next_status == current_status:
        return

    allowed = ACTION_ITEM_TRANSITIONS[current_status]
    if next_status not in allowed:
        raise ConflictError(
            "Invalid action item status transition: "
            f"{current_status.value} -> {next_status.value}"
        )

    if next_status == ActionItemStatus.CONFIRMED:
        confirmed_by = payload.confirmed_by_user_id or action_item.confirmed_by_user_id
        if not confirmed_by:
            raise ConflictError(
                "confirmed action items require confirmed_by_user_id"
            )
        action_item.confirmed_by_user_id = confirmed_by
        action_item.confirmed_at = action_item.confirmed_at or datetime.now(UTC)

    action_item.status = next_status

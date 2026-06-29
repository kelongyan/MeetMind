from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ActionItem, Citation, CitationTargetType, InsightItem
from app.exceptions import NotFoundError
from app.insights import repository
from app.insights.schemas import ActionItemCreate, CitationCreate, InsightItemCreate
from app.meetings.service import get_meeting
from app.transcription.service import get_segment_for_meeting


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

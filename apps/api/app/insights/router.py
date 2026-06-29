from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.insights import service
from app.insights.schemas import (
    ActionItemCreate,
    ActionItemRead,
    ActionItemUpdate,
    CitationCreate,
    CitationRead,
    InsightItemCreate,
    InsightItemRead,
    InsightItemUpdate,
)

router = APIRouter(prefix="/api/meetings/{meeting_id}", tags=["insights"])


@router.post(
    "/insights", response_model=InsightItemRead, status_code=status.HTTP_201_CREATED
)
def create_insight(
    meeting_id: UUID,
    payload: InsightItemCreate,
    session: Session = Depends(get_db_session),
) -> InsightItemRead:
    return service.create_insight(session, meeting_id, payload)


@router.get("/insights", response_model=list[InsightItemRead])
def list_insights(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[InsightItemRead]:
    return service.list_insights(session, meeting_id)


@router.patch("/insights/{insight_id}", response_model=InsightItemRead)
def update_insight(
    meeting_id: UUID,
    insight_id: UUID,
    payload: InsightItemUpdate,
    session: Session = Depends(get_db_session),
) -> InsightItemRead:
    return service.update_insight(session, meeting_id, insight_id, payload)


@router.post(
    "/action-items",
    response_model=ActionItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_action_item(
    meeting_id: UUID,
    payload: ActionItemCreate,
    session: Session = Depends(get_db_session),
) -> ActionItemRead:
    return service.create_action_item(session, meeting_id, payload)


@router.get("/action-items", response_model=list[ActionItemRead])
def list_action_items(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[ActionItemRead]:
    return service.list_action_items(session, meeting_id)


@router.patch("/action-items/{action_item_id}", response_model=ActionItemRead)
def update_action_item(
    meeting_id: UUID,
    action_item_id: UUID,
    payload: ActionItemUpdate,
    session: Session = Depends(get_db_session),
) -> ActionItemRead:
    return service.update_action_item(session, meeting_id, action_item_id, payload)


@router.post(
    "/citations", response_model=CitationRead, status_code=status.HTTP_201_CREATED
)
def create_citation(
    meeting_id: UUID,
    payload: CitationCreate,
    session: Session = Depends(get_db_session),
) -> CitationRead:
    return service.create_citation(session, meeting_id, payload)


@router.get("/citations", response_model=list[CitationRead])
def list_citations(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[CitationRead]:
    return service.list_citations(session, meeting_id)

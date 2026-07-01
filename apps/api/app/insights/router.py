from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
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
from app.pagination import PaginatedResponse

router = APIRouter(prefix="/api/meetings/{meeting_id}", tags=["insights"])


@router.post(
    "/insights", response_model=InsightItemRead, status_code=status.HTTP_201_CREATED
)
def create_insight(
    meeting_id: UUID,
    payload: InsightItemCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> InsightItemRead:
    return service.create_insight(session, meeting_id, payload)


@router.get("/insights", response_model=PaginatedResponse[InsightItemRead])
def list_insights(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[InsightItemRead]:
    items = service.list_insights(session, meeting_id, offset=offset, limit=limit)
    total = service.count_insights(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.patch("/insights/{insight_id}", response_model=InsightItemRead)
def update_insight(
    meeting_id: UUID,
    insight_id: UUID,
    payload: InsightItemUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
) -> ActionItemRead:
    if not payload.confirmed_by_user_id:
        payload.confirmed_by_user_id = str(current_user.id)
    return service.create_action_item(session, meeting_id, payload)


@router.get("/action-items", response_model=PaginatedResponse[ActionItemRead])
def list_action_items(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ActionItemRead]:
    items = service.list_action_items(session, meeting_id, offset=offset, limit=limit)
    total = service.count_action_items(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.patch("/action-items/{action_item_id}", response_model=ActionItemRead)
def update_action_item(
    meeting_id: UUID,
    action_item_id: UUID,
    payload: ActionItemUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ActionItemRead:
    if not payload.confirmed_by_user_id:
        payload.confirmed_by_user_id = str(current_user.id)
    return service.update_action_item(session, meeting_id, action_item_id, payload)


@router.post(
    "/citations", response_model=CitationRead, status_code=status.HTTP_201_CREATED
)
def create_citation(
    meeting_id: UUID,
    payload: CitationCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> CitationRead:
    return service.create_citation(session, meeting_id, payload)


@router.get("/citations", response_model=PaginatedResponse[CitationRead])
def list_citations(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[CitationRead]:
    items = service.list_citations(session, meeting_id, offset=offset, limit=limit)
    total = service.count_citations(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)

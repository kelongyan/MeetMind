from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import ActionItemStatus, User
from app.db.session import get_db_session
from app.insights.repository import (
    count_global_action_items,
    list_global_action_items,
)
from app.insights.schemas import ActionItemRead
from app.pagination import PaginatedResponse

router = APIRouter(prefix="/api/action-items", tags=["action-items"])


@router.get("", response_model=PaginatedResponse[ActionItemRead])
def list_action_items(
    status: ActionItemStatus | None = None,
    meeting_id: UUID | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ActionItemRead]:
    items = list_global_action_items(
        session,
        status=status,
        meeting_id=meeting_id,
        offset=offset,
        limit=limit,
    )
    total = count_global_action_items(session, status=status, meeting_id=meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)

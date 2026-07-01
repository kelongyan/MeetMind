from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import ActionItemStatus
from app.db.session import get_db_session
from app.insights.repository import list_global_action_items
from app.insights.schemas import ActionItemRead

router = APIRouter(prefix="/api/action-items", tags=["action-items"])


@router.get("", response_model=list[ActionItemRead])
def list_action_items(
    status: ActionItemStatus | None = None,
    meeting_id: UUID | None = None,
    session: Session = Depends(get_db_session),
) -> list[ActionItemRead]:
    return list_global_action_items(
        session,
        status=status,
        meeting_id=meeting_id,
    )

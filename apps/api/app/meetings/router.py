from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.meetings import service
from app.meetings.schemas import MeetingCreate, MeetingRead, MeetingUpdate
from app.pagination import PaginatedResponse

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.post("", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(
    payload: MeetingCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MeetingRead:
    return service.create_meeting(session, payload)


@router.get("", response_model=PaginatedResponse[MeetingRead])
def list_meetings(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MeetingRead]:
    items = service.list_meetings(session, offset=offset, limit=limit)
    total = service.count_meetings(session)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MeetingRead:
    return service.get_meeting(session, meeting_id)


@router.patch("/{meeting_id}", response_model=MeetingRead)
def update_meeting(
    meeting_id: UUID,
    payload: MeetingUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MeetingRead:
    return service.update_meeting(session, meeting_id, payload)


@router.post("/{meeting_id}/publish", response_model=MeetingRead)
def publish_meeting(
    meeting_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> MeetingRead:
    return service.publish_meeting(session, meeting_id)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    service.delete_meeting(session, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

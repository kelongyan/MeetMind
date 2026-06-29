from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.meetings import service
from app.meetings.schemas import MeetingCreate, MeetingRead, MeetingUpdate

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.post("", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
def create_meeting(
    payload: MeetingCreate, session: Session = Depends(get_db_session)
) -> MeetingRead:
    return service.create_meeting(session, payload)


@router.get("", response_model=list[MeetingRead])
def list_meetings(session: Session = Depends(get_db_session)) -> list[MeetingRead]:
    return service.list_meetings(session)


@router.get("/{meeting_id}", response_model=MeetingRead)
def get_meeting(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> MeetingRead:
    return service.get_meeting(session, meeting_id)


@router.patch("/{meeting_id}", response_model=MeetingRead)
def update_meeting(
    meeting_id: UUID,
    payload: MeetingUpdate,
    session: Session = Depends(get_db_session),
) -> MeetingRead:
    return service.update_meeting(session, meeting_id, payload)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> Response:
    service.delete_meeting(session, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

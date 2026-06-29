from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Meeting
from app.exceptions import NotFoundError
from app.meetings import repository
from app.meetings.schemas import MeetingCreate, MeetingUpdate
from app.object_storage.local import LocalObjectStorage


def create_meeting(session: Session, payload: MeetingCreate) -> Meeting:
    meeting = Meeting(**payload.model_dump())
    repository.create_meeting(session, meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


def list_meetings(session: Session) -> list[Meeting]:
    return repository.list_meetings(session)


def get_meeting(session: Session, meeting_id: UUID) -> Meeting:
    meeting = repository.get_meeting(session, meeting_id)
    if meeting is None:
        raise NotFoundError("Meeting not found")
    return meeting


def update_meeting(
    session: Session, meeting_id: UUID, payload: MeetingUpdate
) -> Meeting:
    meeting = get_meeting(session, meeting_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(meeting, key, value)
    session.commit()
    session.refresh(meeting)
    return meeting


def delete_meeting(session: Session, meeting_id: UUID) -> None:
    meeting = get_meeting(session, meeting_id)
    storage = LocalObjectStorage(settings.upload_storage_dir)
    for asset in meeting.assets:
        storage.delete_uri(asset.storage_uri)
    storage.delete_meeting(meeting_id)
    repository.delete_meeting(session, meeting)
    session.commit()

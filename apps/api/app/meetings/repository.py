from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Meeting


def create_meeting(session: Session, meeting: Meeting) -> Meeting:
    session.add(meeting)
    return meeting


def list_meetings(
    session: Session, *, offset: int = 0, limit: int = 50
) -> list[Meeting]:
    return list(
        session.scalars(
            select(Meeting)
            .order_by(Meeting.created_at, Meeting.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_meetings(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Meeting)) or 0


def get_meeting(session: Session, meeting_id: UUID) -> Meeting | None:
    return session.get(Meeting, meeting_id)


def delete_meeting(session: Session, meeting: Meeting) -> None:
    session.delete(meeting)

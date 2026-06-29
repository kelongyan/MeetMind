from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import TranscriptSegment
from app.exceptions import NotFoundError
from app.meetings.service import get_meeting
from app.transcription import repository
from app.transcription.schemas import TranscriptSegmentCreate


def create_segment(
    session: Session, meeting_id: UUID, payload: TranscriptSegmentCreate
) -> TranscriptSegment:
    get_meeting(session, meeting_id)
    segment = TranscriptSegment(meeting_id=meeting_id, **payload.model_dump())
    repository.create_segment(session, segment)
    session.commit()
    session.refresh(segment)
    return segment


def list_segments(session: Session, meeting_id: UUID) -> list[TranscriptSegment]:
    get_meeting(session, meeting_id)
    return repository.list_segments(session, meeting_id)


def get_segment_for_meeting(
    session: Session, meeting_id: UUID, segment_id: UUID
) -> TranscriptSegment:
    segment = repository.get_segment(session, segment_id)
    if segment is None or segment.meeting_id != meeting_id:
        raise NotFoundError("Transcript segment not found")
    return segment

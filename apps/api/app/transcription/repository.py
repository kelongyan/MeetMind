from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TranscriptSegment


def create_segment(session: Session, segment: TranscriptSegment) -> TranscriptSegment:
    session.add(segment)
    return segment


def list_segments(session: Session, meeting_id: UUID) -> list[TranscriptSegment]:
    return list(
        session.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.start_ms, TranscriptSegment.id)
        )
    )


def get_segment(session: Session, segment_id: UUID) -> TranscriptSegment | None:
    return session.get(TranscriptSegment, segment_id)

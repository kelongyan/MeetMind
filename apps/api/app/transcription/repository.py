from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import MeetingSection, Speaker, TranscriptSegment


def create_segment(session: Session, segment: TranscriptSegment) -> TranscriptSegment:
    session.add(segment)
    return segment


def list_segments(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 200
) -> list[TranscriptSegment]:
    return list(
        session.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.start_ms, TranscriptSegment.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_segments(session: Session, meeting_id: UUID) -> int:
    from sqlalchemy import func

    return (
        session.scalar(
            select(func.count())
            .select_from(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
        )
        or 0
    )


def get_segment(session: Session, segment_id: UUID) -> TranscriptSegment | None:
    return session.get(TranscriptSegment, segment_id)


def create_section(session: Session, section: MeetingSection) -> MeetingSection:
    session.add(section)
    return section


def list_sections(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[MeetingSection]:
    return list(
        session.scalars(
            select(MeetingSection)
            .where(MeetingSection.meeting_id == meeting_id)
            .order_by(MeetingSection.start_ms, MeetingSection.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_sections(session: Session, meeting_id: UUID) -> int:
    from sqlalchemy import func

    return (
        session.scalar(
            select(func.count())
            .select_from(MeetingSection)
            .where(MeetingSection.meeting_id == meeting_id)
        )
        or 0
    )


def delete_sections_for_meeting(session: Session, meeting_id: UUID) -> None:
    session.execute(
        delete(MeetingSection).where(MeetingSection.meeting_id == meeting_id)
    )


def get_speaker(session: Session, speaker_id: UUID) -> Speaker | None:
    return session.get(Speaker, speaker_id)


def delete_segments_for_asset(session: Session, source_asset_id: UUID) -> None:
    session.execute(
        delete(TranscriptSegment).where(
            TranscriptSegment.source_asset_id == source_asset_id
        )
    )

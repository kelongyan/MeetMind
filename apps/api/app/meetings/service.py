from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import (
    ActionItem,
    Citation,
    CitationTargetType,
    InsightItem,
    InsightType,
    JobStatus,
    Meeting,
    MeetingStatus,
    ProcessingJob,
    TranscriptSegment,
)
from app.exceptions import ConflictError, NotFoundError
from app.meetings import repository
from app.meetings.schemas import MeetingCreate, MeetingUpdate
from app.object_storage.local import LocalObjectStorage


def create_meeting(session: Session, payload: MeetingCreate) -> Meeting:
    meeting = Meeting(**payload.model_dump())
    repository.create_meeting(session, meeting)
    session.commit()
    session.refresh(meeting)
    return meeting


def list_meetings(
    session: Session, *, offset: int = 0, limit: int = 50
) -> list[Meeting]:
    return repository.list_meetings(session, offset=offset, limit=limit)


def count_meetings(session: Session) -> int:
    return repository.count_meetings(session)


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


def publish_meeting(session: Session, meeting_id: UUID) -> Meeting:
    meeting = get_meeting(session, meeting_id)
    _ensure_meeting_can_publish(session, meeting_id)
    meeting.status = MeetingStatus.PUBLISHED
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


def _ensure_meeting_can_publish(session: Session, meeting_id: UUID) -> None:
    has_transcript = session.scalar(
        select(TranscriptSegment.id).where(TranscriptSegment.meeting_id == meeting_id)
    )
    if has_transcript is None:
        raise ConflictError("Cannot publish meeting without transcript segments")

    blocking_job = session.scalar(
        select(ProcessingJob.id).where(
            ProcessingJob.meeting_id == meeting_id,
            ProcessingJob.status.in_(
                [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.FAILED]
            ),
        )
    )
    if blocking_job is not None:
        raise ConflictError(
            "Cannot publish meeting while processing jobs are incomplete"
        )

    action_item_ids = list(
        session.scalars(
            select(ActionItem.id).where(ActionItem.meeting_id == meeting_id)
        )
    )
    decision_ids = list(
        session.scalars(
            select(InsightItem.id).where(
                InsightItem.meeting_id == meeting_id,
                InsightItem.type == InsightType.DECISION,
            )
        )
    )
    if _has_targets_without_citations(
        session, meeting_id, CitationTargetType.ACTION_ITEM, action_item_ids
    ) or _has_targets_without_citations(
        session, meeting_id, CitationTargetType.INSIGHT_ITEM, decision_ids
    ):
        raise ConflictError(
            "Cannot publish meeting while key outputs are missing citations"
        )


def _has_targets_without_citations(
    session: Session,
    meeting_id: UUID,
    target_type: CitationTargetType,
    target_ids: list[UUID],
) -> bool:
    if not target_ids:
        return False

    cited_target_ids = set(
        session.scalars(
            select(Citation.target_id).where(
                Citation.meeting_id == meeting_id,
                Citation.target_type == target_type,
                Citation.target_id.in_(target_ids),
            )
        )
    )
    return any(target_id not in cited_target_ids for target_id in target_ids)

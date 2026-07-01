from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ProcessingJob


def create_job(session: Session, job: ProcessingJob) -> ProcessingJob:
    session.add(job)
    return job


def list_jobs(
    session: Session, meeting_id: UUID, *, offset: int = 0, limit: int = 50
) -> list[ProcessingJob]:
    return list(
        session.scalars(
            select(ProcessingJob)
            .where(ProcessingJob.meeting_id == meeting_id)
            .order_by(ProcessingJob.created_at, ProcessingJob.id)
            .offset(offset)
            .limit(limit)
        )
    )


def count_jobs(session: Session, meeting_id: UUID) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(ProcessingJob)
            .where(ProcessingJob.meeting_id == meeting_id)
        )
        or 0
    )


def get_job(session: Session, job_id: UUID) -> ProcessingJob | None:
    return session.get(ProcessingJob, job_id)

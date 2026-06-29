from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProcessingJob


def create_job(session: Session, job: ProcessingJob) -> ProcessingJob:
    session.add(job)
    return job


def list_jobs(session: Session, meeting_id: UUID) -> list[ProcessingJob]:
    return list(
        session.scalars(
            select(ProcessingJob)
            .where(ProcessingJob.meeting_id == meeting_id)
            .order_by(ProcessingJob.created_at, ProcessingJob.id)
        )
    )


def get_job(session: Session, job_id: UUID) -> ProcessingJob | None:
    return session.get(ProcessingJob, job_id)

from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ProcessingJob


def create_job(session: Session, job: ProcessingJob) -> ProcessingJob:
    session.add(job)
    return job


def get_job(session: Session, job_id: UUID) -> ProcessingJob | None:
    return session.get(ProcessingJob, job_id)

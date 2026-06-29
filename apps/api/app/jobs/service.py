from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import JobStatus, ProcessingJob
from app.exceptions import NotFoundError
from app.jobs import repository
from app.jobs.schemas import ProcessingJobCreate
from app.meetings.service import get_meeting


def create_processing_job(
    session: Session, meeting_id: UUID, payload: ProcessingJobCreate
) -> ProcessingJob:
    get_meeting(session, meeting_id)
    job = ProcessingJob(
        meeting_id=meeting_id,
        status=JobStatus.QUEUED,
        progress=0,
        **payload.model_dump(),
    )
    repository.create_job(session, job)
    session.commit()
    session.refresh(job)
    return job


def get_processing_job(session: Session, job_id: UUID) -> ProcessingJob:
    job = repository.get_job(session, job_id)
    if job is None:
        raise NotFoundError("Processing job not found")
    return job

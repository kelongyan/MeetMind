from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import JobStatus, ProcessingJob
from app.exceptions import ConflictError, NotFoundError
from app.jobs import repository
from app.jobs.schemas import ProcessingJobCreate, ProcessingJobUpdate
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


def update_processing_job(
    session: Session, job_id: UUID, payload: ProcessingJobUpdate
) -> ProcessingJob:
    job = get_processing_job(session, job_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(job, key, value)

    if payload.status == JobStatus.RUNNING and job.started_at is None:
        job.started_at = datetime.now(UTC)
    if payload.status in {JobStatus.SUCCEEDED, JobStatus.FAILED}:
        job.finished_at = datetime.now(UTC)
    if payload.status == JobStatus.FAILED:
        job.failed_at = job.finished_at

    session.commit()
    session.refresh(job)
    return job


def retry_processing_job(session: Session, job_id: UUID) -> ProcessingJob:
    job = get_processing_job(session, job_id)
    if job.status != JobStatus.FAILED:
        raise ConflictError("Only failed jobs can be retried")
    if not job.retryable:
        raise ConflictError("Job is marked as non-retryable")

    retry_job = ProcessingJob(
        meeting_id=job.meeting_id,
        job_type=job.job_type,
        status=JobStatus.QUEUED,
        progress=0,
        provider=job.provider,
        input_asset_id=job.input_asset_id,
        retry_of_job_id=job.id,
        attempt_number=job.attempt_number + 1,
        retryable=True,
    )
    repository.create_job(session, retry_job)
    session.commit()
    session.refresh(retry_job)
    return retry_job

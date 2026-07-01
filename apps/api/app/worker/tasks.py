"""Celery task definitions for the MeetMind processing pipeline."""

from __future__ import annotations

import logging
from uuid import UUID

from app.worker import celery_app

logger = logging.getLogger(__name__)

# Maximum retry count and base delay (seconds) for exponential backoff.
_MAX_RETRIES = 3
_BASE_DELAY = 60


def _backoff(retries: int) -> int:
    """Exponential backoff capped at 600 seconds."""
    return min(_BASE_DELAY * (2**retries), 600)


@celery_app.task(bind=True, max_retries=_MAX_RETRIES, name="meetmind.transcribe")
def run_transcription_task(self, job_id: str) -> dict:
    """Execute a TRANSCRIBE job and chain STRUCTURE on success."""
    from app.db.models import JobStatus
    from app.db.session import SessionLocal
    from app.jobs.service import get_processing_job
    from app.providers.asr.dependencies import get_transcriber
    from app.transcription.service import run_transcription_job

    job_uuid = UUID(job_id)
    with SessionLocal() as session:
        job = get_processing_job(session, job_uuid)
        job.status = JobStatus.RUNNING
        session.commit()

        try:
            transcriber = get_transcriber()
            result = run_transcription_job(session, job_uuid, transcriber=transcriber)
        except Exception as exc:
            logger.exception("Transcription task failed for job %s", job_id)
            raise self.retry(exc=exc, countdown=_backoff(self.request.retries)) from exc

        if result.job.status == JobStatus.SUCCEEDED:
            # Chain the next step: structuring.
            run_structuring_task.delay(str(result.job.meeting_id))

        return {"job_id": job_id, "status": result.job.status.value}


@celery_app.task(bind=True, max_retries=_MAX_RETRIES, name="meetmind.structure")
def run_structuring_task(self, meeting_or_job_id: str) -> dict:
    """Execute a STRUCTURE job and chain EMBEDDING on success."""
    from app.db.models import JobStatus, JobType, ProcessingJob
    from app.db.session import SessionLocal
    from app.jobs.schemas import ProcessingJobCreate
    from app.jobs.service import create_processing_job
    from app.providers.llm.dependencies import get_llm_extractor
    from app.structuring.service import run_structuring_job

    id_uuid = UUID(meeting_or_job_id)
    with SessionLocal() as session:
        # Determine if the id is a job_id or meeting_id.
        job = session.get(ProcessingJob, id_uuid)
        if job is not None and job.job_type == JobType.STRUCTURE:
            job_id = job.id
            meeting_id = job.meeting_id
        else:
            # Treat as meeting_id – find or create a STRUCTURE job.
            from sqlalchemy import select

            existing = session.scalar(
                select(ProcessingJob.id).where(
                    ProcessingJob.meeting_id == id_uuid,
                    ProcessingJob.job_type == JobType.STRUCTURE,
                    ProcessingJob.status == JobStatus.QUEUED,
                )
            )
            if existing is not None:
                job_id = existing
                meeting_id = id_uuid
            else:
                new_job = create_processing_job(
                    session,
                    id_uuid,
                    ProcessingJobCreate(job_type=JobType.STRUCTURE, provider="celery"),
                )
                job_id = new_job.id
                meeting_id = id_uuid

        try:
            extractor = get_llm_extractor()
            result = run_structuring_job(session, job_id, extractor=extractor)
        except Exception as exc:
            logger.exception("Structuring task failed for %s", meeting_or_job_id)
            raise self.retry(exc=exc, countdown=_backoff(self.request.retries)) from exc

        if result.job.status == JobStatus.SUCCEEDED:
            run_embedding_task.delay(str(meeting_id))

        return {"job_id": str(job_id), "status": result.job.status.value}


@celery_app.task(bind=True, max_retries=2, name="meetmind.embed")
def run_embedding_task(self, meeting_id: str) -> dict:
    """Build vector embeddings for a meeting."""
    from app.db.session import SessionLocal
    from app.providers.embedding.dependencies import get_embedder
    from app.retrieval.service import rebuild_meeting_embeddings

    meeting_uuid = UUID(meeting_id)
    with SessionLocal() as session:
        try:
            embedder = get_embedder()
            rebuild_meeting_embeddings(session, meeting_uuid, embedder=embedder)
        except Exception as exc:
            logger.exception("Embedding task failed for meeting %s", meeting_id)
            raise self.retry(exc=exc, countdown=_backoff(self.request.retries)) from exc

    return {"meeting_id": meeting_id, "status": "succeeded"}


def dispatch_pipeline_celery(job_id: UUID, job_type: str) -> None:
    """Dispatch the appropriate Celery task for a given job."""
    if job_type == "transcribe":
        run_transcription_task.delay(str(job_id))
    elif job_type == "structure":
        run_structuring_task.delay(str(job_id))

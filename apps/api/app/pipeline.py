"""Auto-processing pipeline dispatcher.

Chains job execution: TRANSCRIBE -> STRUCTURE -> EMBEDDING.

Each pipeline step runs its work and *returns* a ``BackgroundTasks``
object that Starlette will execute after the current task completes,
providing automatic sequential chaining without requiring Starlette to
inject parameters into background task functions.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.db.models import JobStatus, JobType
from app.jobs.schemas import ProcessingJobCreate
from app.jobs.service import create_processing_job
from app.providers.asr.base import Transcriber
from app.providers.embedding.base import Embedder
from app.providers.llm.base import LLMExtractor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def dispatch_pipeline(
    session: Session,
    job_id: UUID,
    *,
    background_tasks: BackgroundTasks,
    transcriber: Transcriber | None = None,
    extractor: LLMExtractor | None = None,
    embedder: Embedder | None = None,
    skip_first: bool = False,
) -> None:
    """Schedule the first pipeline step as a background task.

    When *skip_first* is ``True``, the initial step is skipped (used when
    the caller has already executed the job synchronously).

    When ``settings.celery_enabled`` is True, tasks are dispatched to
    Celery workers instead of running as in-process background tasks.
    """
    from app.config import settings
    from app.jobs.service import get_processing_job

    job = get_processing_job(session, job_id)

    if settings.celery_enabled:
        from app.worker.tasks import (
            run_embedding_task,
            run_structuring_task,
            run_transcription_task,
        )

        if job.job_type == JobType.TRANSCRIBE:
            if skip_first or job.status == JobStatus.SUCCEEDED:
                run_structuring_task.delay(str(job.meeting_id))
            else:
                run_transcription_task.delay(str(job.id))
        elif job.job_type == JobType.STRUCTURE:
            if skip_first or job.status == JobStatus.SUCCEEDED:
                run_embedding_task.delay(str(job.meeting_id))
            else:
                run_structuring_task.delay(str(job.id))
        return

    # Fallback: in-process BackgroundTasks chaining.
    if job.job_type == JobType.TRANSCRIBE:
        if skip_first or job.status == JobStatus.SUCCEEDED:
            background_tasks.add_task(_run_structure, job.meeting_id, None)
        else:
            background_tasks.add_task(_run_transcription, job.id, transcriber)
    elif job.job_type == JobType.STRUCTURE:
        if skip_first or job.status == JobStatus.SUCCEEDED:
            background_tasks.add_task(_run_embedding, job.meeting_id)
        else:
            background_tasks.add_task(_run_structure, job.id, extractor)


def run_pipeline_sync(
    session: Session,
    job_id: UUID,
    *,
    transcriber: Transcriber | None = None,
    extractor: LLMExtractor | None = None,
) -> None:
    """Execute the pipeline synchronously within the current request.

    Used when ``auto_process=true`` so the response reflects the final
    job status.  Chains TRANSCRIBE → STRUCTURE → EMBEDDING inline.
    """
    from app.jobs.service import get_processing_job

    job = get_processing_job(session, job_id)

    if job.job_type == JobType.TRANSCRIBE:
        next_tasks = _run_transcription(job.id, transcriber)
    elif job.job_type == JobType.STRUCTURE:
        next_tasks = _run_structure(job.id, extractor)
    else:
        return

    # BackgroundTasks.__call__ is async, so we cannot await it here.
    # Instead, drain the task queue and run each step synchronously,
    # following any further chaining returned by each step.
    while next_tasks is not None:
        pending = list(next_tasks.tasks)
        next_tasks = None
        for task in pending:
            result = task.func(*task.args)
            if isinstance(result, BackgroundTasks):
                next_tasks = result


# ---------------------------------------------------------------------------
# Step 1 – Transcription
# ---------------------------------------------------------------------------


def _run_transcription(
    job_id: UUID, transcriber: Transcriber | None
) -> BackgroundTasks | None:
    from app.db.session import SessionLocal
    from app.transcription.service import run_transcription_job

    provider = transcriber or _resolve_transcriber()
    with SessionLocal() as session:
        result = run_transcription_job(session, job_id, transcriber=provider)
        if result.job.status == JobStatus.SUCCEEDED:
            next_tasks = BackgroundTasks()
            next_tasks.add_task(_run_structure, result.job.meeting_id, None)
            return next_tasks
    return None


# ---------------------------------------------------------------------------
# Step 2 – Structuring
# ---------------------------------------------------------------------------


def _run_structure(
    meeting_or_job_id: UUID, extractor: LLMExtractor | None
) -> BackgroundTasks | None:
    from app.db.session import SessionLocal
    from app.structuring.service import run_structuring_job

    provider = extractor or _resolve_extractor()

    with SessionLocal() as session:
        job_id = _resolve_structure_job_id(session, meeting_or_job_id)
        if job_id is None:
            logger.warning(
                "No STRUCTURE job found for meeting %s – skipping",
                meeting_or_job_id,
            )
            return None

        result = run_structuring_job(session, job_id, extractor=provider)
        if result.job.status == JobStatus.SUCCEEDED:
            next_tasks = BackgroundTasks()
            next_tasks.add_task(_run_embedding, result.job.meeting_id)
            return next_tasks
    return None


# ---------------------------------------------------------------------------
# Step 3 – Embedding
# ---------------------------------------------------------------------------


def _run_embedding(meeting_id: UUID) -> None:
    from app.db.session import SessionLocal
    from app.retrieval.service import rebuild_meeting_embeddings

    embedder = _resolve_embedder()
    with SessionLocal() as session:
        rebuild_meeting_embeddings(session, meeting_id, embedder=embedder)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_structure_job_id(session: Session, id_value: UUID) -> UUID | None:
    """Return a STRUCTURE job id, creating one if *id_value* is a meeting id."""
    from sqlalchemy import select

    from app.db.models import ProcessingJob

    # First, try interpreting as a job id.
    job = session.get(ProcessingJob, id_value)
    if job is not None and job.job_type == JobType.STRUCTURE:
        return job.id

    # Otherwise treat as meeting id – look for a QUEUED STRUCTURE job.
    existing = session.scalar(
        select(ProcessingJob.id).where(
            ProcessingJob.meeting_id == id_value,
            ProcessingJob.job_type == JobType.STRUCTURE,
            ProcessingJob.status == JobStatus.QUEUED,
        )
    )
    if existing is not None:
        return existing

    # Auto-create a STRUCTURE job for the meeting.
    new_job = create_processing_job(
        session,
        id_value,
        ProcessingJobCreate(job_type=JobType.STRUCTURE, provider="pipeline"),
    )
    return new_job.id


# ---------------------------------------------------------------------------
# Provider resolution (fallbacks when caller does not supply instances)
# ---------------------------------------------------------------------------


def _resolve_transcriber() -> Transcriber:
    from app.providers.asr.dependencies import get_transcriber

    return get_transcriber()


def _resolve_extractor() -> LLMExtractor:
    from app.providers.llm.dependencies import get_llm_extractor

    return get_llm_extractor()


def _resolve_embedder() -> Embedder:
    from app.providers.embedding.dependencies import get_embedder

    return get_embedder()

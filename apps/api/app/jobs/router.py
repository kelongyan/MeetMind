from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.jobs import service
from app.jobs.schemas import ProcessingJobCreate, ProcessingJobRead, ProcessingJobUpdate

router = APIRouter(tags=["jobs"])


@router.post(
    "/api/meetings/{meeting_id}/process",
    response_model=ProcessingJobRead,
    status_code=status.HTTP_201_CREATED,
)
def create_processing_job(
    meeting_id: UUID,
    payload: ProcessingJobCreate,
    session: Session = Depends(get_db_session),
) -> ProcessingJobRead:
    return service.create_processing_job(session, meeting_id, payload)


@router.get("/api/jobs/{job_id}", response_model=ProcessingJobRead)
def get_processing_job(
    job_id: UUID, session: Session = Depends(get_db_session)
) -> ProcessingJobRead:
    return service.get_processing_job(session, job_id)


@router.patch("/api/jobs/{job_id}", response_model=ProcessingJobRead)
def update_processing_job(
    job_id: UUID,
    payload: ProcessingJobUpdate,
    session: Session = Depends(get_db_session),
) -> ProcessingJobRead:
    return service.update_processing_job(session, job_id, payload)


@router.post(
    "/api/jobs/{job_id}/retry",
    response_model=ProcessingJobRead,
    status_code=status.HTTP_201_CREATED,
)
def retry_processing_job(
    job_id: UUID, session: Session = Depends(get_db_session)
) -> ProcessingJobRead:
    return service.retry_processing_job(session, job_id)

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.jobs import service
from app.jobs.schemas import ProcessingJobCreate, ProcessingJobRead, ProcessingJobUpdate
from app.pagination import PaginatedResponse

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
    current_user: User = Depends(get_current_user),
) -> ProcessingJobRead:
    return service.create_processing_job(session, meeting_id, payload)


@router.get(
    "/api/meetings/{meeting_id}/jobs",
    response_model=PaginatedResponse[ProcessingJobRead],
)
def list_processing_jobs(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ProcessingJobRead]:
    items = service.list_processing_jobs(
        session, meeting_id, offset=offset, limit=limit
    )
    total = service.count_processing_jobs(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/api/jobs/{job_id}", response_model=ProcessingJobRead)
def get_processing_job(
    job_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProcessingJobRead:
    return service.get_processing_job(session, job_id)


@router.patch("/api/jobs/{job_id}", response_model=ProcessingJobRead)
def update_processing_job(
    job_id: UUID,
    payload: ProcessingJobUpdate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProcessingJobRead:
    return service.update_processing_job(session, job_id, payload)


@router.post(
    "/api/jobs/{job_id}/retry",
    response_model=ProcessingJobRead,
    status_code=status.HTTP_201_CREATED,
)
def retry_processing_job(
    job_id: UUID,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProcessingJobRead:
    return service.retry_processing_job(session, job_id)

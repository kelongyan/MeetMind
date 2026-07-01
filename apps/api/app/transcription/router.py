from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.pagination import PaginatedResponse
from app.pipeline import dispatch_pipeline
from app.providers.asr.base import Transcriber
from app.providers.asr.dependencies import get_transcriber
from app.providers.embedding.dependencies import get_embedder
from app.providers.llm.dependencies import get_llm_extractor
from app.request_dependencies import resolve_request_dependency
from app.transcription import service
from app.transcription.schemas import (
    MeetingSectionRead,
    TranscriptionRunRead,
    TranscriptSegmentCreate,
    TranscriptSegmentRead,
)

router = APIRouter(tags=["transcript"])


@router.post(
    "/api/meetings/{meeting_id}/transcript",
    response_model=TranscriptSegmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transcript_segment(
    meeting_id: UUID,
    payload: TranscriptSegmentCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> TranscriptSegmentRead:
    return service.create_segment(session, meeting_id, payload)


@router.get(
    "/api/meetings/{meeting_id}/transcript",
    response_model=PaginatedResponse[TranscriptSegmentRead],
)
def list_transcript_segments(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[TranscriptSegmentRead]:
    items = service.list_segments(session, meeting_id, offset=offset, limit=limit)
    total = service.count_segments(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.get(
    "/api/meetings/{meeting_id}/sections",
    response_model=PaginatedResponse[MeetingSectionRead],
)
def list_meeting_sections(
    meeting_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[MeetingSectionRead]:
    items = service.list_sections(session, meeting_id, offset=offset, limit=limit)
    total = service.count_sections(session, meeting_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.post("/api/jobs/{job_id}/run", response_model=TranscriptionRunRead)
def run_transcription_job(
    job_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    auto_process: bool = Query(default=False),
    session: Session = Depends(get_db_session),
    transcriber: Transcriber = Depends(get_transcriber),
    current_user: User = Depends(get_current_user),
) -> TranscriptionRunRead:
    result = service.run_transcription_job(
        session,
        job_id,
        transcriber=transcriber,
    )
    if auto_process:
        extractor = resolve_request_dependency(request, get_llm_extractor)
        embedder = resolve_request_dependency(request, get_embedder)
        dispatch_pipeline(
            session,
            job_id,
            background_tasks=background_tasks,
            transcriber=transcriber,
            extractor=extractor,
            embedder=embedder,
            skip_first=True,
        )
    return result

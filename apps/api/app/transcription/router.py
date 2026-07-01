from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.providers.asr.base import Transcriber
from app.providers.asr.dependencies import get_transcriber
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
) -> TranscriptSegmentRead:
    return service.create_segment(session, meeting_id, payload)


@router.get(
    "/api/meetings/{meeting_id}/transcript",
    response_model=list[TranscriptSegmentRead],
)
def list_transcript_segments(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[TranscriptSegmentRead]:
    return service.list_segments(session, meeting_id)


@router.get(
    "/api/meetings/{meeting_id}/sections",
    response_model=list[MeetingSectionRead],
)
def list_meeting_sections(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[MeetingSectionRead]:
    return service.list_sections(session, meeting_id)


@router.post("/api/jobs/{job_id}/run", response_model=TranscriptionRunRead)
def run_transcription_job(
    job_id: UUID,
    session: Session = Depends(get_db_session),
    transcriber: Transcriber = Depends(get_transcriber),
) -> TranscriptionRunRead:
    return service.run_transcription_job(
        session,
        job_id,
        transcriber=transcriber,
    )

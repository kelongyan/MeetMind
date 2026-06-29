from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.transcription import service
from app.transcription.schemas import TranscriptSegmentCreate, TranscriptSegmentRead

router = APIRouter(prefix="/api/meetings/{meeting_id}/transcript", tags=["transcript"])


@router.post(
    "", response_model=TranscriptSegmentRead, status_code=status.HTTP_201_CREATED
)
def create_transcript_segment(
    meeting_id: UUID,
    payload: TranscriptSegmentCreate,
    session: Session = Depends(get_db_session),
) -> TranscriptSegmentRead:
    return service.create_segment(session, meeting_id, payload)


@router.get("", response_model=list[TranscriptSegmentRead])
def list_transcript_segments(
    meeting_id: UUID, session: Session = Depends(get_db_session)
) -> list[TranscriptSegmentRead]:
    return service.list_segments(session, meeting_id)

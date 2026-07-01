from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.pagination import PaginatedResponse
from app.providers.embedding.base import Embedder
from app.providers.embedding.dependencies import get_embedder
from app.providers.qa.base import AnswerSynthesizer
from app.providers.qa.dependencies import get_answer_synthesizer
from app.qa import service
from app.qa.schemas import QAAnswerRead, QAMessageRead, QAQuestionCreate

router = APIRouter(prefix="/api/meetings/{meeting_id}/qa", tags=["qa"])


@router.post("", response_model=QAAnswerRead)
def ask_meeting_question(
    meeting_id: UUID,
    payload: QAQuestionCreate,
    session: Session = Depends(get_db_session),
    embedder: Embedder = Depends(get_embedder),
    answer_synthesizer: AnswerSynthesizer = Depends(get_answer_synthesizer),
    current_user: User = Depends(get_current_user),
) -> service.QAResult:
    return service.ask_meeting_question(
        session,
        meeting_id,
        payload,
        embedder=embedder,
        answer_synthesizer=answer_synthesizer,
    )


@router.get("", response_model=PaginatedResponse[QAMessageRead])
def list_qa_messages(
    meeting_id: UUID,
    conversation_id: UUID | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[QAMessageRead]:
    items = service.list_qa_messages(
        session, meeting_id, conversation_id, offset=offset, limit=limit
    )
    total = service.count_qa_messages(session, meeting_id, conversation_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)

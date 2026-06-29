from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
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
) -> service.QAResult:
    return service.ask_meeting_question(
        session,
        meeting_id,
        payload,
        embedder=embedder,
        answer_synthesizer=answer_synthesizer,
    )


@router.get("", response_model=list[QAMessageRead])
def list_qa_messages(
    meeting_id: UUID,
    conversation_id: UUID | None = None,
    session: Session = Depends(get_db_session),
) -> list[object]:
    return service.list_qa_messages(session, meeting_id, conversation_id)

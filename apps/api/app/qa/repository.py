from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Citation, QAMessage


def create_message(session: Session, message: QAMessage) -> QAMessage:
    session.add(message)
    return message


def create_citation(session: Session, citation: Citation) -> Citation:
    session.add(citation)
    return citation


def list_messages(
    session: Session, meeting_id: UUID, conversation_id: UUID | None = None
) -> list[QAMessage]:
    query = (
        select(QAMessage)
        .where(QAMessage.meeting_id == meeting_id)
        .order_by(QAMessage.created_at, QAMessage.id)
    )
    if conversation_id is not None:
        query = query.where(QAMessage.conversation_id == conversation_id)
    return list(session.scalars(query))

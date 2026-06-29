from __future__ import annotations

import uuid
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Citation, CitationTargetType, QAMessage, QAMessageRole
from app.meetings.service import get_meeting
from app.observability.provider_telemetry import observe_provider_call
from app.providers.embedding.base import Embedder
from app.providers.qa.base import (
    AnswerEvidence,
    AnswerSynthesisRequest,
    AnswerSynthesizer,
)
from app.qa import repository
from app.qa.schemas import QAQuestionCreate
from app.retrieval.service import ensure_meeting_embeddings, search_meeting_evidence


@dataclass(frozen=True)
class QAResult:
    conversation_id: UUID
    question: QAMessage
    answer: QAMessage
    citations: list[Citation]


def ask_meeting_question(
    session: Session,
    meeting_id: UUID,
    payload: QAQuestionCreate,
    *,
    embedder: Embedder,
    answer_synthesizer: AnswerSynthesizer,
) -> QAResult:
    get_meeting(session, meeting_id)
    conversation_id = payload.conversation_id or uuid.uuid4()
    question_text = payload.question.strip()

    ensure_meeting_embeddings(session, meeting_id, embedder=embedder)
    evidence = search_meeting_evidence(
        session,
        meeting_id,
        question_text,
        embedder=embedder,
    )
    request = AnswerSynthesisRequest(
        meeting_id=meeting_id,
        question=question_text,
        evidence=evidence,
    )
    synthesis = observe_provider_call(
        operation="qa.synthesize",
        provider=getattr(answer_synthesizer, "provider_name", None),
        model=getattr(answer_synthesizer, "model_name", None),
        prompt_version=None,
        estimated_units=_estimate_answer_units(question_text, evidence),
        cost_per_1k_units_usd=settings.qa_cost_per_1k_chars_usd,
        call=lambda: answer_synthesizer.synthesize(request),
        model_from_result=lambda result: result.model_name,
    )

    question = repository.create_message(
        session,
        QAMessage(
            meeting_id=meeting_id,
            conversation_id=conversation_id,
            role=QAMessageRole.USER,
            content=question_text,
            citation_ids=[],
            model_name=None,
        ),
    )
    answer = repository.create_message(
        session,
        QAMessage(
            meeting_id=meeting_id,
            conversation_id=conversation_id,
            role=QAMessageRole.ASSISTANT,
            content=synthesis.content,
            citation_ids=[],
            model_name=synthesis.model_name,
        ),
    )
    session.flush()

    citations = _create_answer_citations(
        session,
        meeting_id,
        answer.id,
        evidence,
        synthesis.selected_evidence_ids,
    )
    session.flush()
    answer.citation_ids = [str(citation.id) for citation in citations]
    session.commit()
    session.refresh(question)
    session.refresh(answer)
    for citation in citations:
        session.refresh(citation)
    return QAResult(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
        citations=citations,
    )


def _estimate_answer_units(question: str, evidence: list[AnswerEvidence]) -> int:
    return len(question) + sum(
        len(item.source_text) + len(item.quote) for item in evidence
    )


def list_qa_messages(
    session: Session, meeting_id: UUID, conversation_id: UUID | None = None
) -> list[QAMessage]:
    get_meeting(session, meeting_id)
    return repository.list_messages(session, meeting_id, conversation_id)


def _create_answer_citations(
    session: Session,
    meeting_id: UUID,
    answer_id: UUID,
    evidence: list[AnswerEvidence],
    selected_evidence_ids: list[str],
) -> list[Citation]:
    evidence_by_id = {item.id: item for item in evidence}
    citations: list[Citation] = []
    for evidence_id in selected_evidence_ids:
        item = evidence_by_id.get(evidence_id)
        if item is None:
            continue
        citation = repository.create_citation(
            session,
            Citation(
                meeting_id=meeting_id,
                target_type=CitationTargetType.ANSWER,
                target_id=answer_id,
                segment_id=item.segment_id,
                start_ms=item.start_ms,
                end_ms=item.end_ms,
                quote=item.quote,
                confidence=item.score,
            ),
        )
        citations.append(citation)
    return citations

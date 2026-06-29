from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import (
    ActionItem,
    Citation,
    CitationTargetType,
    EmbeddingRecord,
    EmbeddingSourceType,
    InsightItem,
    MeetingStatus,
)
from app.meetings.service import get_meeting
from app.providers.embedding.base import Embedder
from app.providers.qa.base import AnswerEvidence
from app.retrieval import repository


@dataclass(frozen=True)
class EmbeddingIndexResult:
    meeting_id: UUID
    model_name: str
    created_count: int
    source_counts: dict[EmbeddingSourceType, int] = field(default_factory=dict)


@dataclass(frozen=True)
class _EmbeddingSource:
    source_type: EmbeddingSourceType
    source_id: UUID
    text: str
    metadata: dict[str, object]


def rebuild_meeting_embeddings(
    session: Session,
    meeting_id: UUID,
    *,
    embedder: Embedder,
) -> EmbeddingIndexResult:
    meeting = get_meeting(session, meeting_id)
    sources = _collect_sources(session, meeting_id)
    model_name = embedder.model_name

    meeting.status = MeetingStatus.EMBEDDING
    repository.delete_embeddings_for_meeting(session, meeting_id)
    if not sources:
        meeting.status = MeetingStatus.READY_FOR_REVIEW
        session.commit()
        return EmbeddingIndexResult(
            meeting_id=meeting_id,
            model_name=model_name,
            created_count=0,
            source_counts={},
        )

    response = embedder.embed([source.text for source in sources])
    source_counts: dict[EmbeddingSourceType, int] = {}
    for source, vector in zip(sources, response.vectors, strict=True):
        repository.create_embedding(
            session,
            EmbeddingRecord(
                meeting_id=meeting_id,
                source_type=source.source_type,
                source_id=source.source_id,
                embedding_model=response.model_name,
                vector=vector,
                metadata_json=source.metadata,
            ),
        )
        source_counts[source.source_type] = (
            source_counts.get(source.source_type, 0) + 1
        )

    meeting.status = MeetingStatus.READY_FOR_REVIEW
    session.commit()
    return EmbeddingIndexResult(
        meeting_id=meeting_id,
        model_name=response.model_name,
        created_count=len(sources),
        source_counts=source_counts,
    )


def ensure_meeting_embeddings(
    session: Session,
    meeting_id: UUID,
    *,
    embedder: Embedder,
) -> None:
    get_meeting(session, meeting_id)
    if repository.count_embeddings_for_meeting(session, meeting_id) == 0:
        rebuild_meeting_embeddings(session, meeting_id, embedder=embedder)


def search_meeting_evidence(
    session: Session,
    meeting_id: UUID,
    question: str,
    *,
    embedder: Embedder,
    limit: int = 5,
    min_score: float | None = None,
) -> list[AnswerEvidence]:
    get_meeting(session, meeting_id)
    response = embedder.embed([question])
    if not response.vectors:
        return []

    minimum = settings.qa_min_retrieval_score if min_score is None else min_score
    evidence: list[AnswerEvidence] = []
    for embedding, distance in repository.search_embeddings(
        session, meeting_id, response.vectors[0], limit=limit
    ):
        score = 1.0 - distance
        if score < minimum:
            continue
        evidence.extend(_embedding_to_evidence(session, embedding, score))
        if len(evidence) >= limit:
            break
    return evidence[:limit]


def _collect_sources(session: Session, meeting_id: UUID) -> list[_EmbeddingSource]:
    sources: list[_EmbeddingSource] = []
    sources.extend(
        _EmbeddingSource(
            source_type=EmbeddingSourceType.TRANSCRIPT_SEGMENT,
            source_id=segment.id,
            text=segment.text,
            metadata={
                "start_ms": segment.start_ms,
                "end_ms": segment.end_ms,
            },
        )
        for segment in repository.list_transcript_segments(session, meeting_id)
        if segment.text.strip()
    )
    sources.extend(
        _EmbeddingSource(
            source_type=EmbeddingSourceType.MEETING_SECTION,
            source_id=section.id,
            text=" ".join(
                item
                for item in [section.title, section.summary or ""]
                if item.strip()
            ),
            metadata={
                "title": section.title,
                "start_ms": section.start_ms,
                "end_ms": section.end_ms,
            },
        )
        for section in repository.list_sections(session, meeting_id)
    )
    sources.extend(
        _insight_source(insight)
        for insight in repository.list_insights(session, meeting_id)
    )
    sources.extend(
        _action_item_source(item)
        for item in repository.list_action_items(session, meeting_id)
    )
    return [source for source in sources if source.text.strip()]


def _insight_source(insight: InsightItem) -> _EmbeddingSource:
    return _EmbeddingSource(
        source_type=EmbeddingSourceType.INSIGHT_ITEM,
        source_id=insight.id,
        text=f"{insight.title}\n{insight.body}",
        metadata={
            "title": insight.title,
            "status": insight.status.value,
            "type": insight.type.value,
            "confidence": insight.confidence,
        },
    )


def _action_item_source(action_item: ActionItem) -> _EmbeddingSource:
    due = action_item.due_text or (
        action_item.due_date.isoformat() if action_item.due_date else None
    )
    return _EmbeddingSource(
        source_type=EmbeddingSourceType.ACTION_ITEM,
        source_id=action_item.id,
        text=action_item.description,
        metadata={
            "owner_text": action_item.owner_text,
            "due_text": due,
            "status": action_item.status.value,
            "confidence": action_item.confidence,
        },
    )


def _embedding_to_evidence(
    session: Session, embedding: EmbeddingRecord, score: float
) -> list[AnswerEvidence]:
    if embedding.source_type == EmbeddingSourceType.TRANSCRIPT_SEGMENT:
        segment = repository.get_transcript_segment(session, embedding.source_id)
        if segment is None:
            return []
        return [
            AnswerEvidence(
                id=f"transcript_segment:{segment.id}",
                meeting_id=segment.meeting_id,
                source_text=segment.text,
                quote=segment.text,
                source_type=EmbeddingSourceType.TRANSCRIPT_SEGMENT.value,
                source_id=segment.id,
                segment_id=segment.id,
                start_ms=segment.start_ms,
                end_ms=segment.end_ms,
                score=score,
                metadata=embedding.metadata_json or {},
            )
        ]

    if embedding.source_type == EmbeddingSourceType.ACTION_ITEM:
        action_item = repository.get_action_item(session, embedding.source_id)
        if action_item is None:
            return []
        return _target_citations_to_evidence(
            session,
            embedding,
            score,
            CitationTargetType.ACTION_ITEM,
            action_item.id,
            action_item.description,
        )

    if embedding.source_type == EmbeddingSourceType.INSIGHT_ITEM:
        insight = repository.get_insight(session, embedding.source_id)
        if insight is None:
            return []
        return _target_citations_to_evidence(
            session,
            embedding,
            score,
            CitationTargetType.INSIGHT_ITEM,
            insight.id,
            f"{insight.title}: {insight.body}",
        )

    return []


def _target_citations_to_evidence(
    session: Session,
    embedding: EmbeddingRecord,
    score: float,
    target_type: CitationTargetType,
    target_id: UUID,
    source_text: str,
) -> list[AnswerEvidence]:
    citations = repository.list_citations_for_target(
        session, embedding.meeting_id, target_type, target_id
    )
    return [
        _citation_to_evidence(embedding, citation, source_text, score)
        for citation in citations
    ]


def _citation_to_evidence(
    embedding: EmbeddingRecord,
    citation: Citation,
    source_text: str,
    score: float,
) -> AnswerEvidence:
    return AnswerEvidence(
        id=f"{embedding.source_type.value}:{embedding.source_id}:{citation.id}",
        meeting_id=embedding.meeting_id,
        source_text=source_text,
        quote=citation.quote,
        source_type=embedding.source_type.value,
        source_id=embedding.source_id,
        segment_id=citation.segment_id,
        start_ms=citation.start_ms,
        end_ms=citation.end_ms,
        score=score,
        metadata=embedding.metadata_json or {},
    )

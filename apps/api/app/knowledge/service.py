"""Knowledge search service – semantic (vector) with substring fallback."""

from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ActionItem, CitationTargetType, InsightType
from app.knowledge import repository
from app.knowledge.schemas import (
    DuplicateActionGroupRead,
    KnowledgeDecisionRead,
    KnowledgeSearchResultRead,
)
from app.providers.embedding.base import Embedder


@dataclass(frozen=True)
class _WorkspaceContext:
    meeting_ids: list[UUID]
    meeting_titles: dict[UUID, str]


def search_workspace(
    session: Session,
    *,
    workspace_id: str,
    query: str,
    embedder: Embedder | None = None,
    limit: int = 20,
) -> list[KnowledgeSearchResultRead]:
    """Search across all meetings in a workspace.

    When an *embedder* is provided and the workspace has embedded meetings,
    performs semantic vector search.  Falls back to keyword substring
    matching when no embedder is available or no embeddings exist.
    """
    context = _load_workspace_context(session, workspace_id)
    if not context.meeting_ids:
        return []

    # --- Semantic search path ---
    if embedder is not None:
        semantic_results = _semantic_search(
            session, context=context, query=query, embedder=embedder, limit=limit
        )
        if semantic_results is not None:
            return semantic_results

    # --- Keyword fallback ---
    return _keyword_search(session, context=context, query=query, limit=limit)


def _semantic_search(
    session: Session,
    *,
    context: _WorkspaceContext,
    query: str,
    embedder: Embedder,
    limit: int,
) -> list[KnowledgeSearchResultRead] | None:
    """Vector similarity search across workspace meetings.

    Returns ``None`` when no embeddings exist for any meeting in the
    workspace, signalling the caller to fall back to keyword search.
    """
    from app.retrieval import repository as retrieval_repo

    # Check if any meeting in the workspace has embeddings.
    has_any = any(
        retrieval_repo.count_embeddings_for_meeting(session, mid) > 0
        for mid in context.meeting_ids
    )
    if not has_any:
        return None

    # Embed the query.
    try:
        response = embedder.embed([query])
    except Exception:
        return None  # Fall back on provider failure.
    if not response.vectors:
        return None
    query_vector = response.vectors[0]

    # Search per meeting and merge results.
    all_hits: list[tuple[object, float]] = []
    for meeting_id in context.meeting_ids:
        hits = retrieval_repo.search_embeddings(
            session, meeting_id=meeting_id, query_vector=query_vector, limit=limit
        )
        all_hits.extend(hits)

    # Sort by distance (ascending) and take top-K.
    all_hits.sort(key=lambda pair: pair[1])
    top_hits = all_hits[:limit]

    results: list[KnowledgeSearchResultRead] = []
    for record, distance in top_hits:
        result = _embedding_record_to_result(session, context, record, distance)
        if result is not None:
            results.append(result)

    return results


def _embedding_record_to_result(
    session: Session,
    context: _WorkspaceContext,
    record: object,
    distance: float,
) -> KnowledgeSearchResultRead | None:
    """Convert an EmbeddingRecord to a KnowledgeSearchResultRead."""
    from app.db.models import EmbeddingSourceType
    from app.retrieval import repository as retrieval_repo

    source_type = record.source_type
    source_id = record.source_id
    meeting_id = record.meeting_id

    if source_type == EmbeddingSourceType.TRANSCRIPT_SEGMENT:
        segment = retrieval_repo.get_transcript_segment(session, source_id)
        if segment is None:
            return None
        return KnowledgeSearchResultRead(
            meeting_id=meeting_id,
            meeting_title=context.meeting_titles.get(meeting_id, ""),
            source_type="transcript_segment",
            source_id=source_id,
            segment_id=segment.id,
            start_ms=segment.start_ms,
            end_ms=segment.end_ms,
            title="Transcript",
            snippet=segment.text,
            created_at=segment.created_at,
            score=round(1.0 - distance, 4),
        )

    if source_type == EmbeddingSourceType.INSIGHT_ITEM:
        insight = retrieval_repo.get_insight(session, source_id)
        if insight is None:
            return None
        citations = retrieval_repo.list_citations_for_target(
            session, meeting_id, CitationTargetType.INSIGHT_ITEM, source_id
        )
        first = citations[0] if citations else None
        return KnowledgeSearchResultRead(
            meeting_id=meeting_id,
            meeting_title=context.meeting_titles.get(meeting_id, ""),
            source_type="insight_item",
            source_id=source_id,
            segment_id=first.segment_id if first else None,
            start_ms=first.start_ms if first else None,
            end_ms=first.end_ms if first else None,
            title=insight.title,
            snippet=insight.body,
            created_at=insight.created_at,
            score=round(1.0 - distance, 4),
        )

    if source_type == EmbeddingSourceType.ACTION_ITEM:
        action_item = retrieval_repo.get_action_item(session, source_id)
        if action_item is None:
            return None
        citations = retrieval_repo.list_citations_for_target(
            session, meeting_id, CitationTargetType.ACTION_ITEM, source_id
        )
        first = citations[0] if citations else None
        return KnowledgeSearchResultRead(
            meeting_id=meeting_id,
            meeting_title=context.meeting_titles.get(meeting_id, ""),
            source_type="action_item",
            source_id=source_id,
            segment_id=first.segment_id if first else None,
            start_ms=first.start_ms if first else None,
            end_ms=first.end_ms if first else None,
            title="Action item",
            snippet=action_item.description,
            created_at=action_item.created_at,
            score=round(1.0 - distance, 4),
        )

    return None


def _keyword_search(
    session: Session,
    *,
    context: _WorkspaceContext,
    query: str,
    limit: int,
) -> list[KnowledgeSearchResultRead]:
    """Original substring-based keyword search."""
    terms = _terms(query)
    if not terms:
        return []

    results: list[KnowledgeSearchResultRead] = []
    for segment in repository.list_transcript_segments_for_meetings(
        session, context.meeting_ids
    ):
        if _matches(segment.text, terms):
            results.append(
                KnowledgeSearchResultRead(
                    meeting_id=segment.meeting_id,
                    meeting_title=context.meeting_titles[segment.meeting_id],
                    source_type="transcript_segment",
                    source_id=segment.id,
                    segment_id=segment.id,
                    start_ms=segment.start_ms,
                    end_ms=segment.end_ms,
                    title="Transcript",
                    snippet=segment.text,
                    created_at=segment.created_at,
                )
            )

    for insight in repository.list_insights_for_meetings(session, context.meeting_ids):
        text = f"{insight.title} {insight.body}"
        if _matches(text, terms):
            citations = repository.list_citations_for_target(
                session,
                insight.meeting_id,
                CitationTargetType.INSIGHT_ITEM,
                insight.id,
            )
            first_citation = citations[0] if citations else None
            results.append(
                KnowledgeSearchResultRead(
                    meeting_id=insight.meeting_id,
                    meeting_title=context.meeting_titles[insight.meeting_id],
                    source_type="insight_item",
                    source_id=insight.id,
                    segment_id=first_citation.segment_id if first_citation else None,
                    start_ms=first_citation.start_ms if first_citation else None,
                    end_ms=first_citation.end_ms if first_citation else None,
                    title=insight.title,
                    snippet=insight.body,
                    created_at=insight.created_at,
                )
            )

    for action_item in repository.list_action_items_for_meetings(
        session, context.meeting_ids
    ):
        text = " ".join(
            item
            for item in [
                action_item.description,
                action_item.owner_text or "",
                action_item.due_text or "",
            ]
            if item
        )
        if _matches(text, terms):
            citations = repository.list_citations_for_target(
                session,
                action_item.meeting_id,
                CitationTargetType.ACTION_ITEM,
                action_item.id,
            )
            first_citation = citations[0] if citations else None
            results.append(
                KnowledgeSearchResultRead(
                    meeting_id=action_item.meeting_id,
                    meeting_title=context.meeting_titles[action_item.meeting_id],
                    source_type="action_item",
                    source_id=action_item.id,
                    segment_id=first_citation.segment_id if first_citation else None,
                    start_ms=first_citation.start_ms if first_citation else None,
                    end_ms=first_citation.end_ms if first_citation else None,
                    title="Action item",
                    snippet=action_item.description,
                    created_at=action_item.created_at,
                )
            )

    return sorted(results, key=lambda r: r.created_at, reverse=True)[:limit]


def list_workspace_decisions(
    session: Session, *, workspace_id: str, offset: int = 0, limit: int = 50
) -> list[KnowledgeDecisionRead]:
    context = _load_workspace_context(session, workspace_id)
    decisions = repository.list_insights_for_meetings(
        session, context.meeting_ids, insight_type=InsightType.DECISION
    )
    items = [
        KnowledgeDecisionRead(
            id=decision.id,
            meeting_id=decision.meeting_id,
            meeting_title=context.meeting_titles[decision.meeting_id],
            title=decision.title,
            body=decision.body,
            status=decision.status.value,
            confidence=decision.confidence,
            created_at=decision.created_at,
            citations=repository.list_citations_for_target(
                session,
                decision.meeting_id,
                CitationTargetType.INSIGHT_ITEM,
                decision.id,
            ),
        )
        for decision in decisions
    ]
    return items[offset : offset + limit]


def count_workspace_decisions(session: Session, *, workspace_id: str) -> int:
    context = _load_workspace_context(session, workspace_id)
    decisions = repository.list_insights_for_meetings(
        session, context.meeting_ids, insight_type=InsightType.DECISION
    )
    return len(decisions)


def list_duplicate_action_candidates(
    session: Session, *, workspace_id: str, offset: int = 0, limit: int = 50
) -> list[DuplicateActionGroupRead]:
    context = _load_workspace_context(session, workspace_id)
    action_items = repository.list_action_items_for_meetings(
        session, context.meeting_ids
    )
    groups: dict[tuple[str, str], list[ActionItem]] = defaultdict(list)
    for item in action_items:
        key = (_owner_key(item), _description_key(item.description))
        if key[0] and key[1]:
            groups[key].append(item)

    all_groups = [
        DuplicateActionGroupRead(
            reason="similar_owner_and_description",
            items=items,
        )
        for items in groups.values()
        if len(items) > 1
    ]
    return all_groups[offset : offset + limit]


def count_duplicate_action_groups(session: Session, *, workspace_id: str) -> int:
    context = _load_workspace_context(session, workspace_id)
    action_items = repository.list_action_items_for_meetings(
        session, context.meeting_ids
    )
    groups: dict[tuple[str, str], list[ActionItem]] = defaultdict(list)
    for item in action_items:
        key = (_owner_key(item), _description_key(item.description))
        if key[0] and key[1]:
            groups[key].append(item)
    return sum(1 for items in groups.values() if len(items) > 1)


def _load_workspace_context(session: Session, workspace_id: str) -> _WorkspaceContext:
    meetings = repository.list_meetings_for_workspace(session, workspace_id)
    return _WorkspaceContext(
        meeting_ids=[meeting.id for meeting in meetings],
        meeting_titles={meeting.id: meeting.title for meeting in meetings},
    )


def _terms(value: str) -> list[str]:
    return [
        term for term in value.casefold().replace("-", " ").split() if len(term) >= 2
    ]


def _matches(value: str, terms: list[str]) -> bool:
    normalized = value.casefold()
    return all(term in normalized for term in terms)


def _owner_key(item: ActionItem) -> str:
    return (item.owner_user_id or item.owner_text or "").casefold().strip()


def _description_key(description: str) -> str:
    ignored = {"the", "a", "an", "to", "and", "for", "before", "after"}
    terms = [
        term for term in _terms(description) if term not in ignored and len(term) >= 4
    ]
    return " ".join(sorted(set(terms))[:4])

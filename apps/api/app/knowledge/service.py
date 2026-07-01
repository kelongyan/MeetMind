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


@dataclass(frozen=True)
class _WorkspaceContext:
    meeting_ids: list[UUID]
    meeting_titles: dict[UUID, str]


def search_workspace(
    session: Session, *, workspace_id: str, query: str
) -> list[KnowledgeSearchResultRead]:
    context = _load_workspace_context(session, workspace_id)
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

    for insight in repository.list_insights_for_meetings(
        session, context.meeting_ids
    ):
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

    return sorted(results, key=lambda result: result.created_at)


def list_workspace_decisions(
    session: Session, *, workspace_id: str
) -> list[KnowledgeDecisionRead]:
    context = _load_workspace_context(session, workspace_id)
    decisions = repository.list_insights_for_meetings(
        session, context.meeting_ids, insight_type=InsightType.DECISION
    )
    return [
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


def list_duplicate_action_candidates(
    session: Session, *, workspace_id: str
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

    return [
        DuplicateActionGroupRead(
            reason="similar_owner_and_description",
            items=items,
        )
        for items in groups.values()
        if len(items) > 1
    ]


def _load_workspace_context(session: Session, workspace_id: str) -> _WorkspaceContext:
    meetings = repository.list_meetings_for_workspace(session, workspace_id)
    return _WorkspaceContext(
        meeting_ids=[meeting.id for meeting in meetings],
        meeting_titles={meeting.id: meeting.title for meeting in meetings},
    )


def _terms(value: str) -> list[str]:
    return [
        term
        for term in value.casefold().replace("-", " ").split()
        if len(term) >= 2
    ]


def _matches(value: str, terms: list[str]) -> bool:
    normalized = value.casefold()
    return all(term in normalized for term in terms)


def _owner_key(item: ActionItem) -> str:
    return (item.owner_user_id or item.owner_text or "").casefold().strip()


def _description_key(description: str) -> str:
    ignored = {"the", "a", "an", "to", "and", "for", "before", "after"}
    terms = [
        term
        for term in _terms(description)
        if term not in ignored and len(term) >= 4
    ]
    return " ".join(sorted(set(terms))[:4])

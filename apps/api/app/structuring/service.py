from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from json import JSONDecodeError
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import (
    ActionItem,
    ActionItemStatus,
    Citation,
    CitationTargetType,
    InsightItem,
    InsightStatus,
    InsightType,
    JobStatus,
    JobType,
    MeetingStatus,
    ProcessingJob,
    TranscriptSegment,
)
from app.exceptions import ConflictError
from app.jobs.service import get_processing_job
from app.meetings.service import get_meeting
from app.observability.provider_telemetry import observe_provider_call
from app.providers.llm.base import (
    LLMExtractionRequest,
    LLMExtractor,
    TranscriptEvidence,
)
from app.retrieval.repository import delete_embeddings_for_meeting
from app.structuring import repository
from app.structuring.schemas import (
    StructuredCitationDraft,
    StructuredInsightDraft,
    StructuredMeetingBrief,
    StructuredMeetingExtraction,
)
from app.transcription.service import list_segments


class StructuringValidationError(Exception):
    pass


@dataclass(frozen=True)
class StructuringRunResult:
    job: ProcessingJob
    insights: list[InsightItem]
    action_items: list[ActionItem]
    citations: list[Citation]


@dataclass(frozen=True)
class _InsightDraftWithType:
    insight_type: InsightType
    title: str
    body: str
    confidence: float | None
    citations: list[StructuredCitationDraft]


@dataclass(frozen=True)
class _ValidatedCitation:
    segment_id: UUID
    start_ms: int
    end_ms: int
    quote: str
    confidence: float | None


def run_structuring_job(
    session: Session,
    job_id: UUID,
    *,
    extractor: LLMExtractor,
    prompt_version: str | None = None,
) -> StructuringRunResult:
    job = get_processing_job(session, job_id)
    if job.job_type != JobType.STRUCTURE:
        raise ConflictError("Only structure jobs can run structuring")

    meeting = get_meeting(session, job.meeting_id)
    segments = list_segments(session, meeting.id)
    if not segments:
        raise ConflictError("Structuring requires transcript segments")

    version = prompt_version or settings.llm_prompt_version
    job.status = JobStatus.RUNNING
    job.progress = 10
    job.provider = getattr(extractor, "provider_name", job.provider)
    job.started_at = job.started_at or datetime.now(UTC)
    meeting.status = MeetingStatus.STRUCTURING
    session.commit()

    try:
        response = None
        extraction = None
        retry_instruction: str | None = None
        last_error: StructuringValidationError | None = None

        for attempt in range(2):
            request = _build_request(
                meeting.id,
                segments,
                prompt_version=version,
                retry_instruction=retry_instruction,
            )
            response = observe_provider_call(
                operation="llm.extract",
                provider=getattr(extractor, "provider_name", None),
                model=getattr(extractor, "model_name", None),
                prompt_version=version,
                estimated_units=_estimate_extraction_units(request),
                cost_per_1k_units_usd=settings.llm_cost_per_1k_chars_usd,
                call=lambda request=request: extractor.extract(request),
                model_from_result=lambda result: result.model_name,
            )
            try:
                extraction = _parse_extraction(response.content)
                _validate_extraction(extraction, segments)
                break
            except StructuringValidationError as exc:
                last_error = exc
                if attempt == 1:
                    raise
                retry_instruction = (
                    "Previous output failed JSON/schema/citation validation: "
                    f"{exc}"
                )

        if response is None or extraction is None:
            raise last_error or StructuringValidationError("structuring failed")

        repository.delete_generated_outputs(
            session, meeting.id, prompt_version=version
        )
        delete_embeddings_for_meeting(session, meeting.id)
        insights, action_items, citations = _persist_extraction(
            session,
            job.meeting_id,
            extraction,
            segments,
            model_name=response.model_name,
            model_version=response.model_version,
            prompt_version=version,
        )

        job.status = JobStatus.SUCCEEDED
        job.progress = 100
        job.finished_at = datetime.now(UTC)
        meeting.status = MeetingStatus.READY_FOR_REVIEW
        session.commit()
        _refresh_all(session, [job, *insights, *action_items, *citations])
        return StructuringRunResult(
            job=job,
            insights=insights,
            action_items=action_items,
            citations=citations,
        )
    except Exception as exc:
        session.rollback()
        job = get_processing_job(session, job_id)
        meeting = get_meeting(session, job.meeting_id)
        failed_at = datetime.now(UTC)
        job.status = JobStatus.FAILED
        job.progress = 100
        job.failure_code = "structuring_failed"
        job.failure_message = str(exc)
        job.retryable = True
        job.failed_at = failed_at
        job.finished_at = failed_at
        meeting.status = MeetingStatus.FAILED_STRUCTURING
        session.commit()
        raise


def _build_request(
    meeting_id: UUID,
    segments: list[TranscriptSegment],
    *,
    prompt_version: str,
    retry_instruction: str | None,
) -> LLMExtractionRequest:
    return LLMExtractionRequest(
        meeting_id=meeting_id,
        transcript=[
            TranscriptEvidence(
                segment_id=segment.id,
                start_ms=segment.start_ms,
                end_ms=segment.end_ms,
                text=segment.text,
            )
            for segment in segments
        ],
        json_schema=StructuredMeetingExtraction.model_json_schema(),
        prompt_version=prompt_version,
        retry_instruction=retry_instruction,
    )


def _estimate_extraction_units(request: LLMExtractionRequest) -> int:
    schema_size = len(json.dumps(request.json_schema, separators=(",", ":")))
    transcript_size = sum(len(segment.text) for segment in request.transcript)
    retry_size = len(request.retry_instruction or "")
    return schema_size + transcript_size + retry_size


def _parse_extraction(content: str) -> StructuredMeetingExtraction:
    try:
        data = json.loads(content)
    except JSONDecodeError as exc:
        raise StructuringValidationError(f"Invalid JSON: {exc.msg}") from exc

    try:
        return StructuredMeetingExtraction.model_validate(data)
    except ValidationError as exc:
        raise StructuringValidationError(f"Invalid extraction schema: {exc}") from exc


def _validate_extraction(
    extraction: StructuredMeetingExtraction, segments: list[TranscriptSegment]
) -> None:
    segments_by_id = {segment.id: segment for segment in segments}

    for insight in _iter_insights(extraction):
        if not insight.citations:
            raise StructuringValidationError(
                f"{insight.insight_type.value} requires at least one citation"
            )
        for citation in insight.citations:
            _validate_citation(citation, segments_by_id)

    for action_item in extraction.action_items:
        if not action_item.citations:
            raise StructuringValidationError(
                "action_item requires at least one citation"
            )
        for citation in action_item.citations:
            _validate_citation(citation, segments_by_id)


def _persist_extraction(
    session: Session,
    meeting_id: UUID,
    extraction: StructuredMeetingExtraction,
    segments: list[TranscriptSegment],
    *,
    model_name: str,
    model_version: str | None,
    prompt_version: str,
) -> tuple[list[InsightItem], list[ActionItem], list[Citation]]:
    segments_by_id = {segment.id: segment for segment in segments}
    insights: list[InsightItem] = []
    action_items: list[ActionItem] = []
    citations: list[Citation] = []

    for draft in _iter_insights(extraction):
        insight = InsightItem(
            meeting_id=meeting_id,
            type=draft.insight_type,
            title=draft.title,
            body=draft.body,
            status=InsightStatus.PROPOSED,
            confidence=draft.confidence,
            model_name=model_name,
            model_version=model_version,
            prompt_version=prompt_version,
        )
        repository.create_insight(session, insight)
        session.flush()
        insights.append(insight)
        citations.extend(
            _create_citations(
                session,
                meeting_id,
                CitationTargetType.INSIGHT_ITEM,
                insight.id,
                draft.citations,
                segments_by_id,
            )
        )

    for draft in extraction.action_items:
        action_item = ActionItem(
            meeting_id=meeting_id,
            description=draft.description,
            owner_text=draft.owner_text,
            due_text=draft.due_text,
            due_date=draft.due_date,
            status=ActionItemStatus.PROPOSED,
            confidence=draft.confidence,
            model_name=model_name,
            model_version=model_version,
            prompt_version=prompt_version,
            created_by_ai=True,
        )
        repository.create_action_item(session, action_item)
        session.flush()
        action_items.append(action_item)
        citations.extend(
            _create_citations(
                session,
                meeting_id,
                CitationTargetType.ACTION_ITEM,
                action_item.id,
                draft.citations,
                segments_by_id,
            )
        )

    return insights, action_items, citations


def _iter_insights(
    extraction: StructuredMeetingExtraction,
) -> list[_InsightDraftWithType]:
    insights: list[_InsightDraftWithType] = []
    if extraction.meeting_brief:
        insights.append(_brief_to_insight(extraction.meeting_brief))

    insights.extend(
        _InsightDraftWithType(
            insight_type=InsightType.DISCUSSION_POINT,
            title=item.title,
            body=item.body,
            confidence=item.confidence,
            citations=item.citations,
        )
        for item in extraction.discussion_points
    )
    insights.extend(_map_insights(InsightType.DECISION, extraction.decisions))
    insights.extend(_map_insights(InsightType.RISK, extraction.risks))
    insights.extend(_map_insights(InsightType.OPEN_QUESTION, extraction.open_questions))
    return insights


def _brief_to_insight(brief: StructuredMeetingBrief) -> _InsightDraftWithType:
    return _InsightDraftWithType(
        insight_type=InsightType.DISCUSSION_POINT,
        title=brief.title,
        body=brief.summary,
        confidence=brief.confidence,
        citations=brief.citations,
    )


def _map_insights(
    insight_type: InsightType, drafts: list[StructuredInsightDraft]
) -> list[_InsightDraftWithType]:
    return [
        _InsightDraftWithType(
            insight_type=insight_type,
            title=draft.title,
            body=draft.body,
            confidence=draft.confidence,
            citations=draft.citations,
        )
        for draft in drafts
    ]


def _create_citations(
    session: Session,
    meeting_id: UUID,
    target_type: CitationTargetType,
    target_id: UUID,
    citation_drafts: list[StructuredCitationDraft],
    segments_by_id: dict[UUID, TranscriptSegment],
) -> list[Citation]:
    citations: list[Citation] = []
    for draft in citation_drafts:
        validated = _validate_citation(draft, segments_by_id)
        citation = Citation(
            meeting_id=meeting_id,
            target_type=target_type,
            target_id=target_id,
            segment_id=validated.segment_id,
            start_ms=validated.start_ms,
            end_ms=validated.end_ms,
            quote=validated.quote,
            confidence=validated.confidence,
        )
        repository.create_citation(session, citation)
        citations.append(citation)
    return citations


def _validate_citation(
    draft: StructuredCitationDraft, segments_by_id: dict[UUID, TranscriptSegment]
) -> _ValidatedCitation:
    segment = segments_by_id.get(draft.segment_id)
    if segment is None:
        raise StructuringValidationError(
            f"citation references unknown segment_id {draft.segment_id}"
        )

    start_ms = draft.start_ms if draft.start_ms is not None else segment.start_ms
    end_ms = draft.end_ms if draft.end_ms is not None else segment.end_ms
    if start_ms < segment.start_ms or end_ms > segment.end_ms or end_ms < start_ms:
        raise StructuringValidationError(
            "citation time range must stay within transcript segment bounds"
        )
    if draft.quote.casefold() not in segment.text.casefold():
        raise StructuringValidationError(
            "citation quote must appear in the referenced transcript segment"
        )
    return _ValidatedCitation(
        segment_id=draft.segment_id,
        start_ms=start_ms,
        end_ms=end_ms,
        quote=draft.quote,
        confidence=draft.confidence,
    )


def _refresh_all(session: Session, objects: list[object]) -> None:
    for item in objects:
        session.refresh(item)

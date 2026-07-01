"""Markdown export service for meeting knowledge artefacts."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assets import repository as assets_repository
from app.config import settings
from app.db.models import (
    ActionItem,
    AssetType,
    Citation,
    InsightItem,
    InsightType,
    Meeting,
    MeetingAsset,
    MeetingSection,
    TranscriptSegment,
)
from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExportResult:
    """Outcome of a meeting export."""

    asset: MeetingAsset
    markdown: str
    filename: str


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def export_meeting_markdown(session: Session, meeting_id: UUID) -> ExportResult:
    """Generate a Markdown export of a meeting and persist it as an EXPORT asset.

    The export includes:
    - Meeting metadata (title, date, language, status)
    - Sections (if available)
    - Decisions, risks, open questions, discussion points
    - Action items with owner, due date, status
    - Citation references back to transcript segments

    If an EXPORT asset already exists for this meeting, it is replaced.
    """
    meeting = _get_meeting(session, meeting_id)
    markdown = _build_markdown(session, meeting)
    return _persist_export(session, meeting_id, meeting.title, markdown)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def _build_markdown(session: Session, meeting: Meeting) -> str:
    """Assemble a Markdown document from meeting data."""

    lines: list[str] = []

    # --- Header ---
    lines.append(f"# {meeting.title}")
    lines.append("")
    meta_parts = []
    if meeting.language:
        meta_parts.append(f"**语言**：{meeting.language}")
    meta_parts.append(f"**状态**：{_status_label(meeting.status)}")
    if meeting.started_at:
        meta_parts.append(f"**日期**：{meeting.started_at.strftime('%Y-%m-%d %H:%M')}")
    if meeting.duration_ms:
        minutes = meeting.duration_ms // 60_000
        meta_parts.append(f"**时长**：{minutes} 分钟")
    lines.append(" · ".join(meta_parts))
    lines.append("")

    if meeting.description:
        lines.append(f"> {meeting.description}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # --- Sections ---
    sections = _load_sections(session, meeting.id)
    if sections:
        lines.append("## 会议章节")
        lines.append("")
        for i, section in enumerate(sections, 1):
            time_str = _format_time(section.start_ms) if section.start_ms else ""
            lines.append(f"{i}. **{section.title}** {time_str}")
        lines.append("")

    # --- Insights grouped by type ---
    insights = _load_insights(session, meeting.id)

    for insight_type, label in [
        (InsightType.DECISION, "决策"),
        (InsightType.RISK, "风险"),
        (InsightType.OPEN_QUESTION, "待解决问题"),
        (InsightType.DISCUSSION_POINT, "讨论要点"),
    ]:
        typed = [i for i in insights if i.type == insight_type]
        if typed:
            lines.append(f"## {label}")
            lines.append("")
            for item in typed:
                lines.append(f"### {item.title}")
                lines.append("")
                lines.append(item.body)
                lines.append("")
                _append_citations(session, lines, "insight_item", item.id)

    # --- Action items ---
    action_items = _load_action_items(session, meeting.id)
    if action_items:
        lines.append("## 行动项")
        lines.append("")
        lines.append("| # | 描述 | 负责人 | 截止 | 状态 |")
        lines.append("|---|------|--------|------|------|")
        for idx, ai in enumerate(action_items, 1):
            owner = ai.owner_text or "未指定"
            due = ai.due_text or ai.due_date or "—"
            status = _action_status_label(ai.status)
            lines.append(f"| {idx} | {ai.description} | {owner} | {due} | {status} |")
        lines.append("")

        # Citations for action items
        for ai in action_items:
            _append_citations(session, lines, "action_item", ai.id)

    # --- Footer ---
    lines.append("---")
    lines.append("")
    exported_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"*导出于 {exported_at} · MeetMind*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _persist_export(
    session: Session, meeting_id: UUID, title: str, markdown: str
) -> ExportResult:
    """Save the Markdown to disk and create/replace an EXPORT asset."""
    content_bytes = markdown.encode("utf-8")
    digest = hashlib.sha256(content_bytes).hexdigest()
    size = len(content_bytes)

    # Write file
    storage_root = Path(settings.upload_storage_dir)
    target_dir = storage_root / str(meeting_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:48]
    filename = f"{safe_title}.md"
    target_path = target_dir / f"{digest}.md"
    target_path.write_bytes(content_bytes)

    storage_uri = f"local://{meeting_id}/{digest}.md"

    # Soft-delete previous EXPORT assets
    existing = session.scalars(
        select(MeetingAsset).where(
            MeetingAsset.meeting_id == meeting_id,
            MeetingAsset.asset_type == AssetType.EXPORT,
            MeetingAsset.deleted_at.is_(None),
        )
    ).all()
    now = datetime.now(UTC)
    for old_asset in existing:
        old_asset.deleted_at = now

    # Create new asset
    asset = MeetingAsset(
        meeting_id=meeting_id,
        asset_type=AssetType.EXPORT,
        storage_uri=storage_uri,
        original_filename=filename,
        mime_type="text/markdown",
        size_bytes=size,
        sha256=digest,
    )
    assets_repository.create_asset(session, asset)
    session.flush()

    logger.info("Exported meeting %s to %s (%d bytes)", meeting_id, filename, size)
    return ExportResult(asset=asset, markdown=markdown, filename=filename)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_meeting(session: Session, meeting_id: UUID) -> Meeting:
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        raise NotFoundError(f"Meeting {meeting_id} not found")
    return meeting


def _load_sections(session: Session, meeting_id: UUID) -> list[MeetingSection]:
    return list(
        session.scalars(
            select(MeetingSection)
            .where(MeetingSection.meeting_id == meeting_id)
            .order_by(MeetingSection.start_ms.nulls_last())
        ).all()
    )


def _load_insights(session: Session, meeting_id: UUID) -> list[InsightItem]:
    return list(
        session.scalars(
            select(InsightItem)
            .where(InsightItem.meeting_id == meeting_id)
            .order_by(InsightItem.created_at)
        ).all()
    )


def _load_action_items(session: Session, meeting_id: UUID) -> list[ActionItem]:
    return list(
        session.scalars(
            select(ActionItem)
            .where(ActionItem.meeting_id == meeting_id)
            .order_by(ActionItem.created_at)
        ).all()
    )


def _append_citations(
    session: Session,
    lines: list[str],
    target_type: str,
    target_id: UUID,
) -> None:
    """Append citation references in a blockquote style."""
    citations = session.scalars(
        select(Citation)
        .where(
            Citation.target_type == target_type,
            Citation.target_id == target_id,
        )
        .order_by(Citation.start_ms)
    ).all()

    if not citations:
        return

    for c in citations:
        time_str = _format_time(c.start_ms)
        lines.append(f"> 📌 *{time_str}* — \u201c{c.quote}\u201d")
        lines.append(">")
    lines.append("")


def _format_time(ms: int | None) -> str:
    if ms is None:
        return ""
    total_seconds = ms // 1000
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"[{hours}:{minutes:02d}:{seconds:02d}]"
    return f"[{minutes}:{seconds:02d}]"


def _status_label(status: str) -> str:
    labels = {
        "uploaded": "已上传",
        "media_processing": "媒体处理中",
        "transcribing": "转写中",
        "structuring": "结构化中",
        "embedding": "向量化中",
        "ready_for_review": "待审阅",
        "published": "已发布",
    }
    return labels.get(status, status)


def _action_status_label(status: str) -> str:
    labels = {
        "proposed": "待审阅",
        "confirmed": "已确认",
        "in_progress": "进行中",
        "done": "已完成",
        "canceled": "已取消",
    }
    return labels.get(status, status)


def _load_transcript_segments(
    session: Session, meeting_id: UUID
) -> list[TranscriptSegment]:
    """Load all transcript segments for a meeting (unused currently, reserved)."""
    return list(
        session.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.start_ms)
        ).all()
    )

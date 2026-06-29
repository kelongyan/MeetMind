from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.db.models import AssetType

TIMING_PATTERN = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[\.,]\d{3})\s*-->\s*"
    r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?[\.,]\d{3})"
)
TAG_PATTERN = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class ImportedTranscriptSegment:
    start_ms: int
    end_ms: int
    text: str
    chunk_index: int


def import_transcript_file(
    path: Path, asset_type: AssetType
) -> list[ImportedTranscriptSegment]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if asset_type == AssetType.SUBTITLE:
        return _subtitle_segments(text)
    return _plain_text_segments(text)


def _plain_text_segments(text: str) -> list[ImportedTranscriptSegment]:
    blocks = [
        block.strip()
        for block in re.split(r"(?:\r?\n\s*){2,}|\r?\n", text)
        if block.strip()
    ]
    return [
        ImportedTranscriptSegment(
            start_ms=index * 1000,
            end_ms=(index + 1) * 1000,
            text=block,
            chunk_index=index,
        )
        for index, block in enumerate(blocks)
    ]


def _subtitle_segments(text: str) -> list[ImportedTranscriptSegment]:
    blocks = re.split(r"(?:\r?\n\s*){2,}", text)
    segments: list[ImportedTranscriptSegment] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines or lines[0].upper().startswith("WEBVTT"):
            continue

        timing_index = next(
            (index for index, line in enumerate(lines) if "-->" in line), None
        )
        if timing_index is None:
            continue

        match = TIMING_PATTERN.search(lines[timing_index])
        if match is None:
            continue

        cue_text = " ".join(
            _clean_subtitle_text(line) for line in lines[timing_index + 1 :]
        ).strip()
        if not cue_text:
            continue

        segments.append(
            ImportedTranscriptSegment(
                start_ms=_parse_timestamp_ms(match.group("start")),
                end_ms=_parse_timestamp_ms(match.group("end")),
                text=cue_text,
                chunk_index=len(segments),
            )
        )
    return segments


def _parse_timestamp_ms(value: str) -> int:
    normalized = value.replace(",", ".")
    main, milliseconds = normalized.split(".", 1)
    parts = [int(part) for part in main.split(":")]
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    else:
        hours, minutes, seconds = parts
    return ((hours * 3600 + minutes * 60 + seconds) * 1000) + int(
        milliseconds[:3].ljust(3, "0")
    )


def _clean_subtitle_text(text: str) -> str:
    return TAG_PATTERN.sub("", text).strip()

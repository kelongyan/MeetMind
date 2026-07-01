import { cn } from "@/lib/utils";
import { formatTimestamp } from "../../view-model";
import type { TranscriptSegment } from "../../types";
import { segmentDomId } from "../shared/tone-utils";

/**
 * Resolve a human-readable label from the segment's voice identifier.
 * Falls back to a generic label when no information is available.
 */
function resolveVoiceLabel(segment: TranscriptSegment): string {
  if (segment.speaker_id) {
    // ASR 提供者通常返回 "SPEAKER_00", "spk_1" 等格式。
    // 统一转换为友好标签，如"发言人 1"。
    const match = segment.speaker_id.match(/(\d+)/);
    if (match) {
      return `发言人 ${Number(match[1]) + 1}`;
    }
    return segment.speaker_id;
  }
  return "发言人";
}

export function TranscriptSegmentItem({
  segment,
  highlighted,
  pulsed,
}: {
  segment: TranscriptSegment;
  highlighted: boolean;
  pulsed: boolean;
}) {
  const voiceLabel = resolveVoiceLabel(segment);

  return (
    <article
      className={cn(
        "grid grid-cols-[96px_minmax(0,1fr)] gap-4 rounded-md border border-transparent px-2 py-3 outline-none transition-[background-color,border-color,box-shadow] duration-200 motion-reduce:transition-none",
        highlighted
          ? "border-evidence-border bg-evidence-soft"
          : "hover:border-border hover:bg-surface-subtle",
        pulsed
          ? "ring-2 ring-evidence/25 shadow-[0_0_0_4px_var(--color-evidence-soft)]"
          : "",
      )}
      data-timeline-segment
      data-evidence-active={highlighted ? "true" : "false"}
      data-evidence-pulse={pulsed ? "true" : "false"}
      id={segmentDomId(segment.id)}
      tabIndex={-1}
    >
      <div className="flex flex-col items-start gap-2 border-l-2 border-l-transparent pl-3">
        <time className="font-mono text-xs font-semibold tabular-nums text-evidence">
          {formatTimestamp(segment.start_ms)}
        </time>
        <span
          className="rounded-md bg-surface-subtle px-2 py-0.5 text-xs font-medium text-text-muted"
          title={segment.speaker_id ?? undefined}
        >
          {voiceLabel}
        </span>
      </div>

      <div
        className={cn(
          "min-w-0 border-l-2 pl-4",
          highlighted ? "border-l-evidence" : "border-l-border",
        )}
      >
        {segment.confidence !== undefined &&
        segment.confidence !== null &&
        segment.confidence < 0.7 ? (
          <span className="mb-1 inline-flex rounded-md border border-warning/25 bg-warning-soft px-2 py-0.5 text-xs font-medium text-warning">
            需核对
          </span>
        ) : null}
        <p className="break-words text-sm leading-6 text-text-primary">{segment.text}</p>
      </div>
    </article>
  );
}

import { cn } from "@/lib/utils";
import { formatTimestamp } from "../../view-model";
import type { TranscriptSegment } from "../../types";
import { segmentDomId } from "../shared/tone-utils";

export function TranscriptSegmentItem({
  segment,
  highlighted,
  pulsed,
}: {
  segment: TranscriptSegment;
  highlighted: boolean;
  pulsed: boolean;
}) {
  return (
    <article
      className={cn(
        "grid grid-cols-[88px_minmax(0,1fr)] gap-4 rounded-md border border-transparent px-2 py-3 outline-none transition-[background-color,border-color,box-shadow] duration-200",
        highlighted
          ? "border-evidence-border bg-evidence-soft"
          : "hover:border-border hover:bg-surface-subtle",
        pulsed ? "ring-2 ring-evidence/25 shadow-[0_0_0_4px_rgba(8,145,178,0.10)]" : ""
      )}
      data-evidence-active={highlighted ? "true" : "false"}
      data-evidence-pulse={pulsed ? "true" : "false"}
      id={segmentDomId(segment.id)}
      tabIndex={-1}
    >
      <div className="flex flex-col items-start gap-2 border-l-2 border-l-transparent pl-3">
        <time className="font-mono text-xs font-semibold text-evidence">
          {formatTimestamp(segment.start_ms)}
        </time>
        <span className="rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-text-muted">
          发言人
        </span>
      </div>

      <div
        className={cn(
          "min-w-0 border-l-2 pl-4",
          highlighted ? "border-l-evidence" : "border-l-border"
        )}
      >
        {segment.confidence !== undefined &&
        segment.confidence !== null &&
        segment.confidence < 0.7 ? (
          <span className="mb-1 inline-flex rounded-md border border-warning/25 bg-warning-soft px-2 py-0.5 text-xs font-medium text-warning">
            需核对
          </span>
        ) : null}
        <p className="text-sm leading-6 text-text-primary">{segment.text}</p>
      </div>
    </article>
  );
}

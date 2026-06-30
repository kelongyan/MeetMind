import { confidenceLabel } from "../../view-model";
import type { CitationChipView, InsightItemView } from "../../view-model";
import type { UpdateInsightPayload } from "../../api";
import { StatusBadge } from "../shared/status-badge";
import { CitationChip } from "../citations/citation-chip";
import { InsightReviewControls } from "./insight-review-controls";

export function InsightCard({
  item,
  reviewDisabled,
  onUpdateInsight,
  onCitationClick,
}: {
  item: InsightItemView;
  reviewDisabled: boolean;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  onCitationClick: (citation: CitationChipView) => void;
}) {
  return (
    <article className="rounded-md border border-border bg-surface p-3">
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <StatusBadge
          label={insightStatusLabel(item.status)}
          tone={item.status === "confirmed" ? "success" : "info"}
        />
        <span className="text-xs font-medium text-text-muted">
          {confidenceLabel(item.confidence)}
        </span>
      </div>
      <h5 className="text-sm font-semibold leading-5 text-text-primary">{item.title}</h5>
      {item.body !== item.title ? (
        <p className="mt-3 text-sm leading-6 text-text-secondary">{item.body}</p>
      ) : null}
      <div className="mt-3 flex flex-wrap gap-2">
        {item.citations.length === 0 ? (
          <span className="rounded-md border border-warning/25 bg-warning-soft px-2 py-1 text-xs font-medium text-warning">
            需补充证据
          </span>
        ) : (
          item.citations.map((citation) => (
            <CitationChip key={citation.id} citation={citation} onClick={onCitationClick} />
          ))
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-2 border-t border-border pt-3">
        <InsightReviewControls
          disabled={reviewDisabled}
          item={item}
          onUpdate={onUpdateInsight}
        />
      </div>
    </article>
  );
}

function insightStatusLabel(status: string): string {
  if (status === "confirmed") return "已确认";
  if (status === "dismissed") return "已忽略";
  return "待审阅";
}

import { Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { InsightGroupView, CitationChipView } from "../../view-model";
import type { UpdateInsightPayload, UpdateActionItemPayload } from "../../api";
import type { LoadState } from "../shared/load-state";
import { StatusNote } from "../shared/status-note";
import { InsightGroup } from "./insight-group";

export function InsightsPanel({
  insightGroups,
  reviewState,
  reviewMessage,
  onUpdateActionItem,
  onUpdateInsight,
  onCitationClick,
}: {
  insightGroups: InsightGroupView[];
  reviewState: LoadState;
  reviewMessage: string | null;
  onUpdateActionItem: (actionItemId: string, payload: UpdateActionItemPayload) => void;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  onCitationClick: (citation: CitationChipView) => void;
}) {
  const reviewDisabled = reviewState === "loading";

  return (
    <section className="flex min-h-0 flex-col">
      <div className="flex h-14 items-center justify-between border-b border-border bg-surface px-4">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">审阅任务</h3>
          <p className="mt-0.5 text-xs text-text-muted">
            先确认行动项，再核对决策、风险和摘要
          </p>
        </div>
        {reviewState === "loading" ? (
          <Loader2 className="h-4 w-4 animate-spin text-brand-primary" aria-hidden="true" />
        ) : (
          <span className="rounded-md border border-brand-border bg-brand-soft px-2 py-1 text-xs font-medium text-brand-primary">
            AI 草稿
          </span>
        )}
      </div>
      <ScrollArea className="flex-1">
        <div className="p-3">
          {reviewMessage ? (
            <div className="mb-3">
              <StatusNote message={reviewMessage} state={reviewState} />
            </div>
          ) : null}
          <div className="space-y-4">
            {insightGroups.map((group) => (
              <InsightGroup
                key={group.id}
                group={group}
                reviewDisabled={reviewDisabled}
                onUpdateActionItem={onUpdateActionItem}
                onUpdateInsight={onUpdateInsight}
                onCitationClick={onCitationClick}
              />
            ))}
          </div>
        </div>
      </ScrollArea>
    </section>
  );
}

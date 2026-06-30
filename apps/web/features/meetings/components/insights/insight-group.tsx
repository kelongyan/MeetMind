import type { InsightGroupView, CitationChipView } from "../../view-model";
import type { UpdateInsightPayload, UpdateActionItemPayload } from "../../api";
import { ActionItemCard } from "./action-item-card";
import { InsightCard } from "./insight-card";

export function InsightGroup({
  group,
  reviewDisabled,
  onUpdateActionItem,
  onUpdateInsight,
  onCitationClick,
}: {
  group: InsightGroupView;
  reviewDisabled: boolean;
  onUpdateActionItem: (actionItemId: string, payload: UpdateActionItemPayload) => void;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  onCitationClick: (citation: CitationChipView) => void;
}) {
  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-text-primary">{group.title}</h4>
        <span className="rounded-md border border-border bg-muted px-2 py-0.5 text-xs font-medium text-text-secondary">
          {group.items.length}
        </span>
      </div>
      {group.items.length === 0 ? (
        <p className="rounded-md border border-dashed border-border px-3 py-3 text-sm text-text-muted">
          {group.emptyLabel}
        </p>
      ) : (
        <div className="space-y-2">
          {group.items.map((item) => (
            group.id === "action_items" ? (
              <ActionItemCard
                key={item.id}
                item={item}
                reviewDisabled={reviewDisabled}
                onUpdateActionItem={onUpdateActionItem}
                onCitationClick={onCitationClick}
              />
            ) : (
              <InsightCard
                key={item.id}
                item={item}
                reviewDisabled={reviewDisabled}
                onUpdateInsight={onUpdateInsight}
                onCitationClick={onCitationClick}
              />
            )
          ))}
        </div>
      )}
    </section>
  );
}

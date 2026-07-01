import { CalendarClock, UserRound } from "lucide-react";
import type { ComponentType } from "react";
import { confidenceLabel } from "../../view-model";
import type { CitationChipView, InsightItemView } from "../../view-model";
import type { UpdateActionItemPayload } from "../../api";
import { cn } from "@/lib/utils";
import { CitationChip } from "../citations/citation-chip";
import { StatusBadge } from "../shared/status-badge";
import type { StatusTone } from "../shared/tone-utils";
import { ActionReviewControls } from "./action-review-controls";

export function ActionItemCard({
  item,
  reviewDisabled,
  onUpdateActionItem,
  onCitationClick,
}: {
  item: InsightItemView;
  reviewDisabled: boolean;
  onUpdateActionItem: (
    actionItemId: string,
    payload: UpdateActionItemPayload
  ) => void;
  onCitationClick: (citation: CitationChipView) => void;
}) {
  return (
    <article
      className={cn(
        "overflow-hidden rounded-lg border border-border bg-surface shadow-sm",
        actionAccentClassName(item.status)
      )}
    >
      <header className="border-b border-border bg-surface-subtle px-3 py-3">
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge
            label={actionStatusLabel(item.status)}
            tone={actionStatusTone(item.status)}
          />
          <span className="text-xs font-medium text-text-muted">
            {confidenceLabel(item.confidence)}
          </span>
        </div>
        <h5 className="mt-2 break-words text-sm font-semibold leading-6 text-text-primary">
          {item.title}
        </h5>
      </header>

      <div className="space-y-3 p-3">
        <div className="grid gap-2 sm:grid-cols-2">
          <ActionMeta
            icon={UserRound}
            label="负责人"
            value={item.ownerText || "未指定"}
          />
          <ActionMeta
            icon={CalendarClock}
            label="截止"
            value={item.dueText || "未设置"}
          />
        </div>

        <div>
          <div className="mb-2 text-xs font-medium text-text-muted">证据</div>
          <div className="flex flex-wrap gap-2">
            {item.citations.length === 0 ? (
              <span className="rounded-md border border-warning/25 bg-warning-soft px-2 py-1 text-xs font-medium text-warning">
                需补充证据
              </span>
            ) : (
              item.citations.map((citation) => (
                <CitationChip
                  key={citation.id}
                  citation={citation}
                  onClick={onCitationClick}
                />
              ))
            )}
          </div>
        </div>
      </div>

      <footer className="flex flex-wrap gap-2 border-t border-border bg-surface-subtle px-3 py-3">
        <ActionReviewControls
          disabled={reviewDisabled}
          item={item}
          onUpdate={onUpdateActionItem}
        />
      </footer>
    </article>
  );
}

function ActionMeta({
  icon: Icon,
  label,
  value,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-border bg-surface px-2.5 py-2">
      <div className="flex items-center gap-1.5 text-xs font-medium text-text-muted">
        <Icon className="h-3.5 w-3.5" aria-hidden="true" />
        {label}
      </div>
      <div className="mt-1 break-words text-sm font-medium text-text-primary">
        {value}
      </div>
    </div>
  );
}

function actionStatusTone(status: string): StatusTone {
  if (status === "confirmed" || status === "done") return "success";
  if (status === "canceled") return "danger";
  if (status === "in_progress") return "info";
  return "warning";
}

function actionStatusLabel(status: string): string {
  if (status === "confirmed") return "已确认";
  if (status === "in_progress") return "进行中";
  if (status === "done") return "已完成";
  if (status === "canceled") return "已取消";
  return "待审阅";
}

function actionAccentClassName(status: string): string {
  if (status === "confirmed" || status === "done") {
    return "border-l-4 border-l-success";
  }
  if (status === "canceled") return "border-l-4 border-l-danger";
  if (status === "in_progress") return "border-l-4 border-l-brand-primary";
  return "border-l-4 border-l-warning";
}

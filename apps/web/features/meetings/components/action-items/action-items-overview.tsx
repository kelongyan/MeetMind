import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ListChecks } from "lucide-react";
import type { ActionItem, ActionItemStatus, Meeting } from "../../types";
import type { LoadState } from "../shared/load-state";
import { PanelState } from "../shared/panel-state";
import { StatusBadge } from "../shared/status-badge";
import type { StatusTone } from "../shared/tone-utils";

export type ActionStatusFilter = "all" | ActionItemStatus;

const statusFilters: Array<{ value: ActionStatusFilter; label: string }> = [
  { value: "all", label: "全部状态" },
  { value: "proposed", label: "待审阅" },
  { value: "confirmed", label: "已确认" },
  { value: "in_progress", label: "进行中" },
  { value: "done", label: "已完成" },
  { value: "canceled", label: "已取消" },
];

export function ActionItemsOverview({
  actionItems,
  meetings,
  statusFilter,
  loadState,
  error,
  onStatusFilterChange,
  onOpenMeeting,
  onRefresh,
}: {
  actionItems: ActionItem[];
  meetings: Meeting[];
  statusFilter: ActionStatusFilter;
  loadState: LoadState;
  error: string | null;
  onStatusFilterChange: (filter: ActionStatusFilter) => void;
  onOpenMeeting: (meetingId: string) => void;
  onRefresh: () => void;
}) {
  const meetingsById = new Map(meetings.map((meeting) => [meeting.id, meeting]));
  const selectedStatusLabel =
    statusFilters.find((filter) => filter.value === statusFilter)?.label ??
    "全部状态";

  return (
    <section className="flex min-h-[calc(100vh-112px)] min-w-0 flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4">
        <div>
          <div className="flex items-center gap-2">
            <ListChecks className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h1 className="text-xl font-semibold tracking-normal text-text-primary">
              全部行动项
            </h1>
          </div>
          <p className="mt-1 text-sm text-text-muted">
            跨会议查看负责人、状态和来源会议。
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Select
            value={statusFilter}
            onValueChange={(value) =>
              onStatusFilterChange(value as ActionStatusFilter)
            }
          >
            <SelectTrigger className="w-36">
              <SelectValue>{selectedStatusLabel}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {statusFilters.map((filter) => (
                <SelectItem key={filter.value} value={filter.value}>
                  {filter.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={onRefresh} type="button">
            刷新
          </Button>
        </div>
      </div>

      {loadState === "error" ? (
        <PanelState label={error ?? "无法读取行动项。"} tone="danger" />
      ) : actionItems.length === 0 ? (
        <PanelState label="暂无匹配的行动项。" />
      ) : (
        <ScrollArea className="flex-1">
          <div className="divide-y divide-border">
            {actionItems.map((item) => {
              const meeting = item.meeting_id
                ? meetingsById.get(item.meeting_id)
                : undefined;
              return (
                <article key={item.id} className="grid gap-3 p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <StatusBadge
                          label={actionStatusLabel(item.status)}
                          tone={actionStatusTone(item.status)}
                        />
                        <span className="text-xs text-text-muted">
                          {meeting?.title ?? "未知会议"}
                        </span>
                      </div>
                      <h2 className="mt-2 text-sm font-semibold leading-6 text-text-primary">
                        {item.description}
                      </h2>
                      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-muted">
                        <span>负责人：{item.owner_text || "未指定"}</span>
                        <span>截止：{item.due_text || item.due_date || "未设置"}</span>
                      </div>
                    </div>
                    {item.meeting_id ? (
                      <Button
                        variant="outline"
                        size="sm"
                        type="button"
                        onClick={() => onOpenMeeting(item.meeting_id as string)}
                      >
                        打开来源
                      </Button>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        </ScrollArea>
      )}
    </section>
  );
}

function actionStatusTone(status: ActionItemStatus): StatusTone {
  if (status === "confirmed" || status === "done") return "success";
  if (status === "canceled") return "danger";
  if (status === "in_progress") return "info";
  return "warning";
}

function actionStatusLabel(status: ActionItemStatus): string {
  if (status === "confirmed") return "已确认";
  if (status === "in_progress") return "进行中";
  if (status === "done") return "已完成";
  if (status === "canceled") return "已取消";
  return "待审阅";
}

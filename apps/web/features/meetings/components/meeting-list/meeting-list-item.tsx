import { cn } from "@/lib/utils";
import { formatDateTime, formatDuration, getMeetingStatusMeta } from "../../view-model";
import type { Meeting } from "../../types";
import { StatusBadge } from "../shared/status-badge";

export function MeetingListItem({
  meeting,
  isSelected,
  onSelect,
}: {
  meeting: Meeting;
  isSelected: boolean;
  onSelect: (meetingId: string) => void;
}) {
  const meta = getMeetingStatusMeta(meeting.status);

  return (
    <button
      className={cn(
        "grid w-full gap-2 text-left transition-colors hover:bg-muted focus:outline-none focus:ring-2 focus:ring-inset focus:ring-ring",
        isSelected
          ? "border-l-[3px] border-l-brand-primary bg-brand-soft py-3.5 pl-[13px] pr-4"
          : "border-l-[3px] border-l-transparent px-4 py-3.5"
      )}
      onClick={() => onSelect(meeting.id)}
      type="button"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="min-w-0 truncate text-sm font-semibold text-text-primary">
          {meeting.title}
        </span>
        <StatusBadge label={meta.label} tone={meta.tone} />
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-text-muted">
        <span>{formatDateTime(meeting.created_at)}</span>
        <span className="text-right">{formatDuration(meeting.duration_ms)}</span>
      </div>
    </button>
  );
}

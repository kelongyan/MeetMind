import { formatDateTime, formatDuration, getMeetingStatusMeta } from "../../view-model";
import type { Meeting, MeetingDetailData } from "../../types";
import { StatusBadge } from "../shared/status-badge";

export function MeetingHeader({
  selectedMeeting,
  detail,
}: {
  selectedMeeting: Meeting;
  detail: MeetingDetailData | null;
}) {
  const status = getMeetingStatusMeta(selectedMeeting.status);

  return (
    <div className="border-b border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="truncate text-xl font-semibold tracking-normal text-text-primary">
              {selectedMeeting.title}
            </h2>
            <StatusBadge label={status.label} tone={status.tone} />
          </div>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-xs text-text-muted">
            <span>{selectedMeeting.language ?? "自动识别语言"}</span>
            <span>{formatDuration(selectedMeeting.duration_ms)}</span>
            <span>更新于 {formatDateTime(selectedMeeting.updated_at)}</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-right text-xs">
          <div className="rounded-md border border-border bg-muted px-2 py-1">
            <div className="font-semibold text-text-primary">{detail?.assets.length ?? 0}</div>
            <div className="text-text-muted">资源</div>
          </div>
          <div className="rounded-md border border-evidence-border bg-evidence-soft px-2 py-1">
            <div className="font-semibold text-evidence">{detail?.citations.length ?? 0}</div>
            <div className="text-evidence">证据</div>
          </div>
        </div>
      </div>
    </div>
  );
}

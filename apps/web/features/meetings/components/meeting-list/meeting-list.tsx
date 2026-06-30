import { Skeleton } from "@/components/ui/skeleton";
import type { Meeting } from "../../types";
import type { LoadState } from "../shared/load-state";
import { PanelState } from "../shared/panel-state";
import { MeetingListItem } from "./meeting-list-item";

export function MeetingList({
  meetings,
  selectedMeetingId,
  listState,
  listError,
  onSelectMeeting,
}: {
  meetings: Meeting[];
  selectedMeetingId: string | null;
  listState: LoadState;
  listError: string | null;
  onSelectMeeting: (meetingId: string) => void;
}) {
  if (listState === "loading" && meetings.length === 0) {
    return <MeetingListSkeleton />;
  }
  if (listState === "error") {
    return <PanelState label={listError ?? "无法读取会议列表。"} tone="danger" />;
  }
  if (meetings.length === 0) {
    return <PanelState label="暂无会议。" />;
  }

  return (
    <div className="divide-y divide-border">
      {meetings.map((meeting) => (
        <MeetingListItem
          key={meeting.id}
          meeting={meeting}
          isSelected={meeting.id === selectedMeetingId}
          onSelect={onSelectMeeting}
        />
      ))}
    </div>
  );
}

function MeetingListSkeleton() {
  return (
    <div className="divide-y divide-border">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="grid gap-2 px-4 py-3.5">
          <div className="flex items-start justify-between gap-3">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-6 w-16 rounded-md" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-16 justify-self-end" />
          </div>
        </div>
      ))}
    </div>
  );
}

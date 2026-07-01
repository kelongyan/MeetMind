import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import type { MeetingSection, TranscriptSegment } from "../../types";
import { PanelState } from "../shared/panel-state";
import { SectionNav } from "./section-nav";
import { TranscriptSegmentItem } from "./transcript-segment";

export function TranscriptPanel({
  segments,
  sections,
  highlightedSegmentId,
  pulsedSegmentId,
  isLoading,
  onSectionClick,
}: {
  segments: TranscriptSegment[];
  sections: MeetingSection[];
  highlightedSegmentId: string | null;
  pulsedSegmentId: string | null;
  isLoading: boolean;
  onSectionClick: (section: MeetingSection) => void;
}) {
  return (
    <section aria-label="转写证据流" className="flex min-h-0 min-w-0 flex-col">
      <div className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-surface/90">
        <div>
          <h3 className="text-sm font-semibold text-text-primary">转写记录</h3>
          <p className="mt-0.5 text-xs text-text-muted">原始发言是所有结论的证据源</p>
        </div>
        <span className="rounded-md border border-border bg-surface-subtle px-2 py-1 text-xs font-medium text-text-secondary">
          {segments.length} 段发言
        </span>
      </div>

      {isLoading ? (
        <TranscriptSkeleton />
      ) : segments.length === 0 ? (
        <PanelState label="暂无转写记录。" />
      ) : (
        <>
          <SectionNav sections={sections} onSectionClick={onSectionClick} />
          <ScrollArea className="flex-1">
            <div className="space-y-2 p-4 pb-6">
              {segments.map((segment) => (
                <TranscriptSegmentItem
                  key={segment.id}
                  segment={segment}
                  highlighted={highlightedSegmentId === segment.id}
                  pulsed={pulsedSegmentId === segment.id}
                />
              ))}
            </div>
          </ScrollArea>
        </>
      )}
    </section>
  );
}

function TranscriptSkeleton() {
  return (
    <div className="space-y-2 p-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="grid grid-cols-[96px_minmax(0,1fr)] gap-4 rounded-md px-2 py-3">
          <div className="space-y-2">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-12 rounded-md" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      ))}
    </div>
  );
}

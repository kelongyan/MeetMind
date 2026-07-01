import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileAudio, Lightbulb, MessageSquareText, Activity } from "lucide-react";
import type { FormEvent } from "react";
import type {
  Citation,
  Meeting,
  MeetingDetailData,
  MeetingSection,
  ProcessingJob,
  QAResponse,
} from "../../types";
import type { CitationChipView, InsightGroupView } from "../../view-model";
import type { UpdateActionItemPayload, UpdateInsightPayload } from "../../api";
import type { LoadState } from "../shared/load-state";
import { PanelState } from "../shared/panel-state";
import { MeetingHeader } from "./meeting-header";
import { TranscriptPanel } from "../transcript/transcript-panel";
import { JobsPanel } from "../jobs/jobs-panel";
import { QAPanel } from "../qa/qa-panel";
import { InsightsPanel } from "../insights/insights-panel";

export function MeetingDetail({
  selectedMeeting,
  detail,
  detailState,
  detailError,
  highlightedSegmentId,
  pulsedSegmentId,
  insightGroups,
  jobState,
  jobMessage,
  qaQuestion,
  qaResponses,
  qaState,
  qaError,
  reviewState,
  reviewMessage,
  onCitationClick,
  onSectionClick,
  onRunJob,
  onRetryJob,
  onQaQuestionChange,
  onSubmitQuestion,
  onUpdateActionItem,
  onUpdateInsight,
  onPublishMeeting,
}: {
  selectedMeeting: Meeting | null;
  detail: MeetingDetailData | null;
  detailState: LoadState;
  detailError: string | null;
  highlightedSegmentId: string | null;
  pulsedSegmentId: string | null;
  insightGroups: InsightGroupView[];
  jobState: LoadState;
  jobMessage: string | null;
  qaQuestion: string;
  qaResponses: QAResponse[];
  qaState: LoadState;
  qaError: string | null;
  reviewState: LoadState;
  reviewMessage: string | null;
  onCitationClick: (citation: Citation | CitationChipView | { segmentId: string }) => void;
  onSectionClick: (section: MeetingSection) => void;
  onRunJob: (job: ProcessingJob) => void;
  onRetryJob: (jobId: string) => void;
  onQaQuestionChange: (question: string) => void;
  onSubmitQuestion: (event: FormEvent<HTMLFormElement>) => void;
  onUpdateActionItem: (actionItemId: string, payload: UpdateActionItemPayload) => void;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  onPublishMeeting: () => void;
}) {
  if (!selectedMeeting) {
    return (
      <section className="flex min-h-[calc(100vh-144px)] items-center justify-center rounded-lg border border-border bg-surface p-6 shadow-sm">
        <div className="flex flex-col items-center gap-4 text-center max-w-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-lg border border-brand-border bg-brand-soft">
            <FileAudio className="h-8 w-8 text-brand-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-text-primary">选择一场会议</h2>
            <p className="mt-2 text-sm text-text-muted">
              从左侧打开会议，查看转写、证据和待审阅行动项。
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              document
                .querySelector<HTMLInputElement>("#meeting-title")
                ?.focus();
            }}
          >
            创建新会议
          </Button>
        </div>
      </section>
    );
  }

  if (detailState === "loading" && !detail) {
    return <MeetingDetailSkeleton />;
  }

  return (
    <section
      data-workspace-region="evidence-review"
      className="flex min-h-[calc(100vh-144px)] min-w-0 flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-sm ring-1 ring-border/40"
    >
      <MeetingHeader
        selectedMeeting={selectedMeeting}
        detail={detail}
        onPublishMeeting={onPublishMeeting}
      />

      {detailState === "error" ? (
        <PanelState
          label={detailError ?? "无法读取会议详情。"}
          tone="danger"
        />
      ) : null}

      {detail ? (
        <div className="flex min-h-0 flex-1 min-w-0 flex-col lg:grid lg:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]">
          <TranscriptPanel
            segments={detail.transcriptSegments}
            sections={detail.sections}
            highlightedSegmentId={highlightedSegmentId}
            pulsedSegmentId={pulsedSegmentId}
            isLoading={false}
            onSectionClick={onSectionClick}
          />

          <section
            aria-label="审阅辅助区"
            className="flex min-h-0 min-w-0 flex-col border-t border-border bg-surface-subtle/70 lg:border-t-0 lg:border-l"
          >
            <Tabs defaultValue="insights" className="flex min-h-0 flex-1 flex-col">
              <TabsList className="sticky top-0 z-10 grid h-12 w-full shrink-0 grid-cols-3 rounded-none border-b border-border bg-surface px-2">
                <TabsTrigger value="insights" className="gap-1.5">
                  <Lightbulb className="h-4 w-4" />
                  任务
                </TabsTrigger>
                <TabsTrigger value="qa" className="gap-1.5">
                  <MessageSquareText className="h-4 w-4" />
                  问答
                </TabsTrigger>
                <TabsTrigger value="jobs" className="gap-1.5">
                  <Activity className="h-4 w-4" />
                  处理
                </TabsTrigger>
              </TabsList>
              <TabsContent value="insights" className="mt-0 flex-1 data-[state=active]:flex data-[state=active]:flex-col">
                <InsightsPanel
                  insightGroups={insightGroups}
                  reviewState={reviewState}
                  reviewMessage={reviewMessage}
                  onUpdateActionItem={onUpdateActionItem}
                  onUpdateInsight={onUpdateInsight}
                  onCitationClick={(citation) => onCitationClick(citation)}
                />
              </TabsContent>
              <TabsContent value="qa" className="mt-0 flex-1 data-[state=active]:flex data-[state=active]:flex-col">
                <QAPanel
                  qaQuestion={qaQuestion}
                  qaResponses={qaResponses}
                  qaState={qaState}
                  qaError={qaError}
                  onQuestionChange={onQaQuestionChange}
                  onSubmitQuestion={onSubmitQuestion}
                  onCitationClick={(citation) => {
                    if ("segment_id" in citation) {
                      onCitationClick(citation);
                    }
                  }}
                />
              </TabsContent>
              <TabsContent value="jobs" className="mt-0 flex-1 data-[state=active]:flex data-[state=active]:flex-col">
                <JobsPanel
                  jobs={detail.jobs}
                  jobState={jobState}
                  jobMessage={jobMessage}
                  onRunJob={onRunJob}
                  onRetryJob={onRetryJob}
                />
              </TabsContent>
            </Tabs>
          </section>
        </div>
      ) : null}
    </section>
  );
}

function MeetingDetailSkeleton() {
  return (
    <section className="min-w-0 overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
      <div className="border-b border-border p-4">
        <div className="flex items-center gap-2">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-6 w-20 rounded-md" />
        </div>
        <div className="mt-2 flex gap-4">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-32" />
        </div>
      </div>
      <div className="flex flex-1 lg:grid lg:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]">
        <div className="space-y-3 p-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-md border border-border p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-5 w-16 rounded-md" />
              </div>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </div>
        <div className="border-t border-border lg:border-t-0 lg:border-l p-3 space-y-4">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-32 w-full rounded-md" />
          <Skeleton className="h-32 w-full rounded-md" />
        </div>
      </div>
    </section>
  );
}

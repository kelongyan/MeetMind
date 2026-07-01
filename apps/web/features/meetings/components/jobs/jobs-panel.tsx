import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Loader2 } from "lucide-react";
import type { ProcessingJob } from "../../types";
import type { LoadState } from "../shared/load-state";
import { StatusNote } from "../shared/status-note";
import { JobCard } from "./job-card";

export function JobsPanel({
  jobs,
  jobState,
  jobMessage,
  onRunJob,
  onRetryJob,
}: {
  jobs: ProcessingJob[];
  jobState: LoadState;
  jobMessage: string | null;
  onRunJob: (job: ProcessingJob) => void;
  onRetryJob: (jobId: string) => void;
}) {
  const busy = jobState === "loading";

  return (
    <section className="flex min-h-0 flex-col">
      <div className="sticky top-0 z-10 flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-surface/90">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h3 className="text-sm font-semibold text-text-primary">处理流水线</h3>
          </div>
          <p className="mt-0.5 text-xs text-text-muted">转写、结构化和索引任务状态</p>
        </div>
        {busy ? (
          <Loader2 className="h-4 w-4 animate-spin text-brand-primary" aria-hidden="true" />
        ) : (
          <span className="rounded-md border border-border bg-muted px-2 py-1 text-xs font-medium text-text-secondary">
            {jobs.length} 项任务
          </span>
        )}
      </div>
      <ScrollArea className="flex-1">
        <div className="space-y-3 p-4">
          {jobMessage ? <StatusNote message={jobMessage} state={jobState} /> : null}
          {jobs.length === 0 ? (
            <p className="rounded-md border border-dashed border-border bg-surface px-3 py-3 text-sm leading-6 text-text-muted">
              暂无处理任务。上传音视频后，系统会在这里显示转写、结构化和索引进度。
            </p>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  busy={busy}
                  onRun={onRunJob}
                  onRetry={onRetryJob}
                />
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
    </section>
  );
}

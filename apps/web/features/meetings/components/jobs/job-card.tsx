import { Play, RefreshCcw } from "lucide-react";
import type { ProcessingJob } from "../../types";
import { cn } from "@/lib/utils";
import { ReviewButton } from "../shared/review-button";
import { StatusBadge } from "../shared/status-badge";
import {
  jobStatusLabel,
  jobStatusTone,
  jobTypeLabel,
} from "../shared/tone-utils";

export function JobCard({
  job,
  busy,
  onRun,
  onRetry,
}: {
  job: ProcessingJob;
  busy: boolean;
  onRun: (job: ProcessingJob) => void;
  onRetry: (jobId: string) => void;
}) {
  const canRun =
    job.status === "queued" &&
    (job.job_type === "transcribe" || job.job_type === "structure");
  const canRetry = job.status === "failed" && job.retryable !== false;

  return (
    <article
      className={cn(
        "rounded-md border border-border border-l-4 bg-surface p-3",
        jobAccentClassName(job.status)
      )}
      data-job-status={job.status}
      key={job.id}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-text-primary">
              {jobTypeLabel(job.job_type)}
            </span>
            <StatusBadge
              label={jobStatusLabel(job.status)}
              tone={jobStatusTone(job.status)}
            />
          </div>
          <div className="mt-1 truncate text-xs text-text-muted">
            {job.provider ?? "本地处理"} · 第 {job.attempt_number ?? 1} 次尝试
          </div>
          {job.failure_message ? (
            <p className="mt-2 text-xs leading-5 text-danger">{job.failure_message}</p>
          ) : null}
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          {canRun ? (
            <ReviewButton disabled={busy} onClick={() => onRun(job)}>
              <Play className="h-3.5 w-3.5" aria-hidden="true" />
              开始处理
            </ReviewButton>
          ) : null}
          {canRetry ? (
            <ReviewButton disabled={busy} onClick={() => onRetry(job.id)}>
              <RefreshCcw className="h-3.5 w-3.5" aria-hidden="true" />
              重新排队
            </ReviewButton>
          ) : null}
        </div>
      </div>
    </article>
  );
}

function jobAccentClassName(status: ProcessingJob["status"]): string {
  if (status === "succeeded") return "border-l-success";
  if (status === "failed") return "border-l-danger";
  if (status === "running") return "border-l-brand-primary";
  return "border-l-warning";
}

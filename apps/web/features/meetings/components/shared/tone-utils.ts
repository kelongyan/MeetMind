import type { ProcessingJob } from "../../types";

export type StatusTone = "neutral" | "info" | "success" | "warning" | "danger";

export function toneClassName(tone: StatusTone): string {
  if (tone === "success") return "border-success/20 bg-success-soft text-success";
  if (tone === "warning") return "border-warning/25 bg-warning-soft text-warning";
  if (tone === "danger") return "border-danger/20 bg-danger-soft text-danger";
  if (tone === "info") return "border-brand-primary/20 bg-brand-soft text-brand-primary";
  return "border-border bg-surface-subtle text-text-secondary";
}

export function jobStatusTone(status: ProcessingJob["status"]): StatusTone {
  if (status === "succeeded") return "success";
  if (status === "failed") return "danger";
  if (status === "running") return "info";
  return "warning";
}

export function jobStatusLabel(status: ProcessingJob["status"]): string {
  if (status === "succeeded") return "已完成";
  if (status === "failed") return "失败";
  if (status === "running") return "处理中";
  return "排队中";
}

export function jobTypeLabel(jobType: ProcessingJob["job_type"]): string {
  if (jobType === "transcribe") return "转写";
  if (jobType === "structure") return "结构化";
  if (jobType === "embed") return "索引";
  if (jobType === "export") return "导出";
  return jobType;
}

export function reviewButtonToneClassName(tone: "neutral" | "success" | "danger"): string {
  if (tone === "success") {
    return "border-success/20 bg-success-soft text-success hover:bg-success-soft/80";
  }
  if (tone === "danger") {
    return "border-danger/20 bg-danger-soft text-danger hover:bg-danger-soft/80";
  }
  return "border-border bg-surface text-text-secondary hover:bg-surface-subtle";
}

export function toErrorMessage(error: unknown, fallback: string): string {
  if (
    error instanceof TypeError &&
    (error.message === "Failed to fetch" ||
      error.message.includes("NetworkError"))
  ) {
    return fallback;
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

export function segmentDomId(segmentId: string): string {
  return `transcript-segment-${segmentId}`;
}

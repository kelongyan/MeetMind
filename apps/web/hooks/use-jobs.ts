"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import type { ProcessingJob } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import {
  jobStatusLabel,
  jobTypeLabel,
  toErrorMessage,
} from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useJobs(
  api: MeetMindApi,
  selectedMeetingId: string | null,
  onRefresh: () => void,
  onDetailReload: (meetingId: string) => void,
) {
  const [jobState, setJobState] = useState<LoadState>("idle");
  const [jobMessage, setJobMessage] = useState<string | null>(null);

  const handleRunJob = useCallback(
    async (job: ProcessingJob) => {
      if (!selectedMeetingId) return;
      setJobState("loading");
      setJobMessage(null);
      try {
        const result = await api.runJob(job);
        await onRefresh();
        await onDetailReload(selectedMeetingId);
        const msg = `处理任务已更新：${jobTypeLabel(job.job_type)} · ${jobStatusLabel(result.job.status)}。`;
        setJobState("success");
        setJobMessage(msg);
        toast.success(msg);
      } catch (error) {
        const msg = toErrorMessage(error, "无法运行处理任务。");
        setJobState("error");
        setJobMessage(msg);
        toast.error(msg);
      }
    },
    [api, selectedMeetingId, onRefresh, onDetailReload],
  );

  const handleRetryJob = useCallback(
    async (jobId: string) => {
      if (!selectedMeetingId) return;
      setJobState("loading");
      setJobMessage(null);
      try {
        await api.retryJob(jobId);
        await onRefresh();
        await onDetailReload(selectedMeetingId);
        const msg = "重试任务已排队。";
        setJobState("success");
        setJobMessage(msg);
        toast.success(msg);
      } catch (error) {
        const msg = toErrorMessage(error, "无法重试处理任务。");
        setJobState("error");
        setJobMessage(msg);
        toast.error(msg);
      }
    },
    [api, selectedMeetingId, onRefresh, onDetailReload],
  );

  return { jobState, jobMessage, setJobState, setJobMessage, handleRunJob, handleRetryJob };
}

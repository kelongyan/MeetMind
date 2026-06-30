"use client";

import { useCallback, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import type { ProcessingJob } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useUpload(
  api: MeetMindApi,
  onMeetingCreated: (meetingId: string) => void,
  onRefresh: () => void,
) {
  const [title, setTitle] = useState("");
  const [language, setLanguage] = useState("zh-CN");
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<LoadState>("idle");
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [lastUploadJob, setLastUploadJob] = useState<ProcessingJob | null>(null);

  const handleCreateAndUpload = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmedTitle = title.trim();
      if (!trimmedTitle) {
        setUploadState("error");
        setUploadMessage("会议标题不能为空。");
        return;
      }

      setUploadState("loading");
      setUploadMessage(null);
      setLastUploadJob(null);
      try {
        const meeting = await api.createMeeting({
          title: trimmedTitle,
          language: language || null,
        });
        let job: ProcessingJob | null = null;
        if (file) {
          const upload = await api.uploadAsset(meeting.id, file);
          job = upload.job;
          const msg = upload.duplicate
            ? "文件已存在，已打开对应会议。"
            : "文件已上传，处理任务已排队。";
          setUploadMessage(msg);
          toast.success(msg);
        } else {
          const msg = "会议已创建。";
          setUploadMessage(msg);
          toast.success(msg);
        }
        setLastUploadJob(job);
        setTitle("");
        setFile(null);
        onMeetingCreated(meeting.id);
        setUploadState("success");
        await onRefresh();
      } catch (error) {
        const msg = toErrorMessage(error, "上传失败，请检查文件后重试。");
        setUploadState("error");
        setUploadMessage(msg);
        toast.error(msg);
      }
    },
    [api, title, language, file, onMeetingCreated, onRefresh],
  );

  return {
    title,
    language,
    file,
    uploadState,
    uploadMessage,
    lastUploadJob,
    setTitle,
    setLanguage,
    setFile,
    handleCreateAndUpload,
  };
}

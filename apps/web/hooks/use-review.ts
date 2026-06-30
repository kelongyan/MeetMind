"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi, UpdateActionItemPayload, UpdateInsightPayload } from "@/features/meetings/api";

export function useReview(
  api: MeetMindApi,
  selectedMeetingId: string | null,
  onDetailReload: (meetingId: string) => void,
) {
  const [reviewState, setReviewState] = useState<LoadState>("idle");
  const [reviewMessage, setReviewMessage] = useState<string | null>(null);

  const handleUpdateInsight = useCallback(
    async (insightId: string, payload: UpdateInsightPayload) => {
      if (!selectedMeetingId) return;
      setReviewState("loading");
      setReviewMessage(null);
      try {
        await api.updateInsight(selectedMeetingId, insightId, payload);
        await onDetailReload(selectedMeetingId);
        setReviewState("success");
        setReviewMessage("审阅结果已更新。");
        toast.success("审阅结果已更新。");
      } catch (error) {
        const msg = toErrorMessage(error, "无法更新审阅结果。");
        setReviewState("error");
        setReviewMessage(msg);
        toast.error(msg);
      }
    },
    [api, selectedMeetingId, onDetailReload],
  );

  const handleUpdateActionItem = useCallback(
    async (actionItemId: string, payload: UpdateActionItemPayload) => {
      if (!selectedMeetingId) return;
      setReviewState("loading");
      setReviewMessage(null);
      try {
        await api.updateActionItem(selectedMeetingId, actionItemId, payload);
        await onDetailReload(selectedMeetingId);
        setReviewState("success");
        setReviewMessage("行动项已更新。");
        toast.success("行动项已更新。");
      } catch (error) {
        const msg = toErrorMessage(error, "无法更新行动项。");
        setReviewState("error");
        setReviewMessage(msg);
        toast.error(msg);
      }
    },
    [api, selectedMeetingId, onDetailReload],
  );

  return { reviewState, reviewMessage, handleUpdateInsight, handleUpdateActionItem };
}

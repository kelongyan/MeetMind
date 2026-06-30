"use client";

import { useCallback, useEffect, useState } from "react";
import type { MeetingDetailData } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useMeetingDetail(api: MeetMindApi, selectedMeetingId: string | null) {
  const [detail, setDetail] = useState<MeetingDetailData | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);

  const loadDetail = useCallback(
    async (meetingId: string) => {
      setDetailState("loading");
      setDetailError(null);
      try {
        const nextDetail = await api.loadMeetingDetail(meetingId);
        setDetail(nextDetail);
        setDetailState("success");
      } catch (error) {
        setDetailState("error");
        setDetailError(toErrorMessage(error, "无法读取会议详情，请稍后重试。"));
      }
    },
    [api],
  );

  useEffect(() => {
    if (selectedMeetingId) {
      void loadDetail(selectedMeetingId);
    } else {
      setDetail(null);
      setDetailState("idle");
    }
  }, [loadDetail, selectedMeetingId]);

  return { detail, detailState, detailError, loadDetail };
}

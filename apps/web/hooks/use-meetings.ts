"use client";

import { useCallback, useEffect, useState } from "react";
import type { Meeting } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useMeetings(api: MeetMindApi) {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [listState, setListState] = useState<LoadState>("idle");
  const [listError, setListError] = useState<string | null>(null);

  const refreshMeetings = useCallback(async () => {
    setListState("loading");
    setListError(null);
    try {
      const nextMeetings = await api.listMeetings();
      setMeetings(nextMeetings);
      setListState("success");
    } catch (error) {
      setListState("error");
      setListError(toErrorMessage(error, "无法读取会议列表，请稍后重试。"));
    }
  }, [api]);

  useEffect(() => {
    void refreshMeetings();
  }, [refreshMeetings]);

  return { meetings, listState, listError, refreshMeetings };
}

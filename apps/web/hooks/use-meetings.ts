"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Meeting } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useMeetings(api: MeetMindApi) {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [listState, setListState] = useState<LoadState>("idle");
  const [listError, setListError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const refreshMeetings = useCallback(async () => {
    // Cancel any in-flight request to avoid race conditions.
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setListState("loading");
    setListError(null);
    try {
      const nextMeetings = await api.listMeetings();
      if (controller.signal.aborted) return;
      setMeetings(nextMeetings);
      setListState("success");
    } catch (error) {
      if (controller.signal.aborted) return;
      setListState("error");
      setListError(toErrorMessage(error, "无法读取会议列表，请稍后重试。"));
    }
  }, [api]);

  useEffect(() => {
    void refreshMeetings();
  }, [refreshMeetings]);

  // Abort on unmount.
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  return { meetings, listState, listError, refreshMeetings };
}

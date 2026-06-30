"use client";

import { useCallback, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import type { QAResponse } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useQA(api: MeetMindApi, selectedMeetingId: string | null) {
  const [qaQuestion, setQaQuestion] = useState("");
  const [qaResponses, setQaResponses] = useState<QAResponse[]>([]);
  const [qaState, setQaState] = useState<LoadState>("idle");
  const [qaError, setQaError] = useState<string | null>(null);

  const handleAskQuestion = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const trimmedQuestion = qaQuestion.trim();
      if (!selectedMeetingId || !trimmedQuestion) return;

      setQaState("loading");
      setQaError(null);
      try {
        const response = await api.askQuestion(selectedMeetingId, {
          question: trimmedQuestion,
          conversation_id: qaResponses[0]?.conversation_id ?? null,
        });
        setQaResponses((current) => [...current, response]);
        setQaQuestion("");
        setQaState("success");
      } catch (error) {
        const msg = toErrorMessage(error, "无法回答该问题，请稍后重试。");
        setQaState("error");
        setQaError(msg);
        toast.error(msg);
      }
    },
    [api, selectedMeetingId, qaQuestion, qaResponses],
  );

  return {
    qaQuestion,
    qaResponses,
    qaState,
    qaError,
    setQaQuestion,
    setQaResponses,
    setQaState,
    setQaError,
    handleAskQuestion,
  };
}

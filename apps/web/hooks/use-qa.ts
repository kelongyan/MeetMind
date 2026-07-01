"use client";

import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";
import type { Citation, QAMessage, QAResponse } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { toErrorMessage } from "@/features/meetings/components/shared/tone-utils";
import type { MeetMindApi } from "@/features/meetings/api";

export function useQA(
  api: MeetMindApi,
  selectedMeetingId: string | null,
  citations?: Citation[],
) {
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

  useEffect(() => {
    if (!selectedMeetingId) {
      setQaResponses([]);
      setQaState("idle");
      setQaError(null);
      return;
    }

    const meetingId = selectedMeetingId;
    let cancelled = false;
    async function loadHistory() {
      setQaState("loading");
      setQaError(null);
      try {
        const messages = await api.listQAMessages(meetingId);
        if (cancelled) return;
        setQaResponses(buildQAResponsesFromMessages(messages, citations ?? []));
        setQaState("success");
      } catch (error) {
        if (cancelled) return;
        setQaState("error");
        setQaError(toErrorMessage(error, "无法读取历史问答。"));
      }
    }

    void loadHistory();
    return () => {
      cancelled = true;
    };
  }, [api, selectedMeetingId, citations]);

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

function buildQAResponsesFromMessages(
  messages: QAMessage[],
  citations: Citation[],
): QAResponse[] {
  const citationsById = new Map(citations.map((citation) => [citation.id, citation]));
  const responses: QAResponse[] = [];
  let pendingQuestion: QAMessage | null = null;

  for (const message of messages) {
    if (message.role === "user") {
      pendingQuestion = message;
      continue;
    }

    if (message.role === "assistant" && pendingQuestion) {
      responses.push({
        conversation_id: message.conversation_id,
        question: pendingQuestion,
        answer: message,
        citations: message.citation_ids
          .map((citationId) => citationsById.get(citationId))
          .filter((citation): citation is Citation => Boolean(citation)),
      });
      pendingQuestion = null;
    }
  }

  return responses;
}

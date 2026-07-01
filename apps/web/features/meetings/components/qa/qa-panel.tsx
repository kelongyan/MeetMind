import { MessageSquareText } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { Citation, QAResponse } from "../../types";
import type { LoadState } from "../shared/load-state";
import { StatusNote } from "../shared/status-note";
import { QAInput } from "./qa-input";
import { QAMessage } from "./qa-message";
import type { FormEvent } from "react";

export function QAPanel({
  qaQuestion,
  qaResponses,
  qaState,
  qaError,
  onQuestionChange,
  onSubmitQuestion,
  onCitationClick,
}: {
  qaQuestion: string;
  qaResponses: QAResponse[];
  qaState: LoadState;
  qaError: string | null;
  onQuestionChange: (question: string) => void;
  onSubmitQuestion: (event: FormEvent<HTMLFormElement>) => void;
  onCitationClick: (citation: Citation | { id: string; start_ms: number; quote: string }) => void;
}) {
  return (
    <section className="flex min-h-0 flex-col">
      <div className="sticky top-0 z-10 flex h-14 items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-surface/90">
        <div>
          <div className="flex items-center gap-2">
            <MessageSquareText className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h3 className="text-sm font-semibold text-text-primary">证据问答</h3>
          </div>
          <p className="mt-0.5 text-xs text-text-muted">提一个问题，MeetMind 会优先从转写证据里回答。</p>
        </div>
        <span className="rounded-md border border-evidence-border bg-evidence-soft px-2 py-1 text-xs font-medium text-evidence">
          基于当前会议
        </span>
      </div>
      <div className="flex min-h-0 flex-1 flex-col gap-3 p-4">
        <QAInput
          question={qaQuestion}
          qaState={qaState}
          onQuestionChange={onQuestionChange}
          onSubmit={onSubmitQuestion}
        />

        {qaError ? <StatusNote message={qaError} state="error" /> : null}

        <ScrollArea className="min-h-0 flex-1">
          <div className="space-y-3">
            {qaResponses.length === 0 ? (
              <p className="rounded-md border border-dashed border-evidence-border bg-evidence-soft px-3 py-3 text-sm leading-6 text-evidence">
                还没有问答记录。可以询问负责人、截止时间、风险或会议结论，回答会附上引用证据。
              </p>
            ) : (
              qaResponses.map((response) => (
                <QAMessage
                  key={response.answer.id}
                  response={response}
                  onCitationClick={onCitationClick}
                />
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </section>
  );
}

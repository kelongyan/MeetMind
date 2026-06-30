import { Bot, UserRound } from "lucide-react";
import type { Citation, QAResponse } from "../../types";
import { CitationTimestampChip } from "../citations/citation-chip";

export function QAMessage({
  response,
  onCitationClick,
}: {
  response: QAResponse;
  onCitationClick: (citation: Citation | { id: string; start_ms: number; quote: string }) => void;
}) {
  return (
    <article className="overflow-hidden rounded-md border border-border bg-surface" key={response.answer.id}>
      <div className="border-b border-border bg-surface-subtle px-3 py-2">
        <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-text-muted">
          <UserRound className="h-3.5 w-3.5" aria-hidden="true" />
          你的问题
        </div>
        <p className="text-sm leading-6 text-text-primary">{response.question.content}</p>
      </div>
      <div className="flex gap-2 px-3 py-3">
        <Bot className="mt-1 h-4 w-4 shrink-0 text-brand-primary" aria-hidden="true" />
        <div className="min-w-0 flex-1 space-y-3">
          <div>
            <div className="mb-1 text-xs font-medium text-text-muted">AI 回答</div>
            <p className="text-sm leading-6 text-text-primary">{response.answer.content}</p>
          </div>
          <div className="rounded-md border border-evidence-border bg-evidence-soft p-2">
            <div className="mb-2 text-xs font-medium text-evidence">引用证据</div>
            <div className="flex flex-wrap gap-2">
              {response.citations.length === 0 ? (
                <span className="rounded-md border border-warning/25 bg-warning-soft px-2 py-1 text-xs font-medium text-warning">
                  未找到引用证据
                </span>
              ) : (
                response.citations.map((citation) => (
                  <CitationTimestampChip
                    key={citation.id}
                    citation={citation}
                    onClick={onCitationClick}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

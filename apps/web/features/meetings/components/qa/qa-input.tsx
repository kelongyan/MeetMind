import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2, Send } from "lucide-react";
import type { FormEvent } from "react";
import type { LoadState } from "../shared/load-state";

export function QAInput({
  question,
  qaState,
  onQuestionChange,
  onSubmit,
}: {
  question: string;
  qaState: LoadState;
  onQuestionChange: (question: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="space-y-2" onSubmit={onSubmit}>
      <Label htmlFor="qa-question" className="text-sm font-medium">
        问题
      </Label>
      <Textarea
        id="qa-question"
        className="min-h-20 resize-y border-border bg-surface"
        placeholder="这次会议有哪些待办由谁负责？"
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
      />
      <Button
        type="submit"
        className="w-full"
        disabled={qaState === "loading" || question.trim().length === 0}
      >
        {qaState === "loading" ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            正在检索证据
          </>
        ) : (
          <>
            <Send className="h-4 w-4" aria-hidden="true" />
            发送问题
          </>
        )}
      </Button>
    </form>
  );
}

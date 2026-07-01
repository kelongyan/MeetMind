import { AlertCircle } from "lucide-react";
import type { LoadState } from "./load-state";
import { toneClassName } from "./tone-utils";

export function StatusNote({
  message,
  state,
}: {
  message: string;
  state: LoadState;
}) {
  const tone = state === "error" ? "danger" : state === "success" ? "success" : "info";
  return (
    <div
      data-slot="status-note"
      role={state === "error" ? "alert" : "status"}
      aria-live={state === "error" ? "assertive" : "polite"}
      className={[
        toneClassName(tone),
        "flex gap-2 rounded-md border bg-surface-subtle/80 p-3 text-xs leading-5",
      ].join(" ")}
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span className="break-words">{message}</span>
    </div>
  );
}

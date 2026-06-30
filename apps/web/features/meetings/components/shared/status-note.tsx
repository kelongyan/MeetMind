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
    <div className={["flex gap-2 rounded-md border p-3 text-xs", toneClassName(tone)].join(" ")}>
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

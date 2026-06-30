import { Loader2 } from "lucide-react";
import { toneClassName } from "./tone-utils";
import type { StatusTone } from "./tone-utils";

export function PanelState({
  label,
  tone = "neutral",
  variant = "default",
}: {
  label: string;
  tone?: StatusTone;
  variant?: "default" | "loading";
}) {
  return (
    <div className="flex min-h-40 items-center justify-center p-6">
      <div
        className={[
          "flex items-center gap-2 rounded-md border px-3 py-2 text-sm",
          toneClassName(tone),
        ].join(" ")}
      >
        {variant === "loading" ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        ) : null}
        {label}
      </div>
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 p-6 text-center">
      {Icon ? <Icon className="h-10 w-10 text-text-muted" aria-hidden="true" /> : null}
      <div>
        <p className="text-sm font-medium text-text-primary">{title}</p>
        {description ? (
          <p className="mt-1 text-xs text-text-muted">{description}</p>
        ) : null}
      </div>
      {action}
    </div>
  );
}

export function LoadingState({ label = "加载中..." }: { label?: string }) {
  return (
    <div className="flex min-h-40 items-center justify-center p-6">
      <div className="flex items-center gap-2 text-sm text-text-muted">
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        {label}
      </div>
    </div>
  );
}

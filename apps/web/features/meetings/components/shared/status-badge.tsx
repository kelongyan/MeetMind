import { Badge } from "@/components/ui/badge";
import { toneClassName } from "./tone-utils";
import type { StatusTone } from "./tone-utils";

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <Badge
      variant="outline"
      data-status-tone={tone}
      className={["h-6 rounded-md px-2.5", toneClassName(tone)].join(" ")}
    >
      {label}
    </Badge>
  );
}

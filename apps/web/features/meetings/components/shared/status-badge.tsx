import { Badge } from "@/components/ui/badge";
import { toneClassName } from "./tone-utils";
import type { StatusTone } from "./tone-utils";

export function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <Badge variant="outline" className={toneClassName(tone)}>
      {label}
    </Badge>
  );
}

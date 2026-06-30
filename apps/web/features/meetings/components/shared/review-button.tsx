import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { ReactNode } from "react";
import { reviewButtonToneClassName } from "./tone-utils";

export function ReviewButton({
  children,
  disabled,
  onClick,
  tone = "neutral",
}: {
  children: ReactNode;
  disabled: boolean;
  onClick: () => void;
  tone?: "neutral" | "success" | "danger";
}) {
  return (
    <Button
      variant="outline"
      size="sm"
      disabled={disabled}
      onClick={onClick}
      type="button"
      className={cn("h-8", reviewButtonToneClassName(tone))}
    >
      {children}
    </Button>
  );
}

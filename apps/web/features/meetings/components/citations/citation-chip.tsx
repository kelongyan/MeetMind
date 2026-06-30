import { Button } from "@/components/ui/button";
import { Link2 } from "lucide-react";
import { formatTimestamp } from "../../view-model";
import type { CitationChipView } from "../../view-model";

export function CitationChip({
  citation,
  onClick,
}: {
  citation: CitationChipView;
  onClick: (citation: CitationChipView) => void;
}) {
  return (
    <EvidenceJumpButton
      label={citation.label}
      quote={citation.quote}
      onClick={() => onClick(citation)}
    />
  );
}

export function CitationTimestampChip({
  citation,
  onClick,
}: {
  citation: { id: string; start_ms: number; quote: string };
  onClick: (citation: { id: string; start_ms: number; quote: string }) => void;
}) {
  const label = formatTimestamp(citation.start_ms);

  return (
    <EvidenceJumpButton
      label={label}
      quote={citation.quote}
      onClick={() => onClick(citation)}
    />
  );
}

function EvidenceJumpButton({
  label,
  quote,
  onClick,
}: {
  label: string;
  quote: string;
  onClick: () => void;
}) {
  return (
    <Button
      data-citation-chip
      data-citation-time={label}
      variant="outline"
      size="sm"
      className="h-auto min-h-8 gap-2 rounded-md border-evidence-border bg-evidence-soft px-2.5 py-1.5 text-left text-xs font-medium text-evidence hover:border-evidence hover:bg-cyan-50 focus-visible:ring-evidence/30"
      onClick={onClick}
      aria-label={`跳转到证据 ${label}：${quote}`}
      title={quote}
      type="button"
    >
      <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
      <span className="grid leading-tight">
        <span className="text-[11px] font-semibold">证据来源</span>
        <span className="font-mono text-xs">{label}</span>
      </span>
    </Button>
  );
}

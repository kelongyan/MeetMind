import type { MeetingSection } from "../../types";
import { formatTimestamp } from "../../view-model";

export function SectionNav({
  sections,
  onSectionClick,
}: {
  sections: MeetingSection[];
  onSectionClick: (section: MeetingSection) => void;
}) {
  if (sections.length === 0) return null;

  return (
    <nav
      aria-label="会议章节"
      className="border-b border-border bg-surface-subtle px-4 py-3"
    >
      <div className="mb-2 text-xs font-medium text-text-muted">章节导航</div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {sections.map((section) => (
          <button
            key={section.id}
            type="button"
            className="max-w-56 shrink-0 rounded-md border border-border bg-surface px-2.5 py-2 text-left text-xs hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
            onClick={() => onSectionClick(section)}
          >
            <div className="truncate font-semibold text-text-primary">
              {section.title}
            </div>
            {section.start_ms !== null && section.start_ms !== undefined ? (
              <div className="mt-0.5 font-mono text-[11px] text-evidence">
                {formatTimestamp(section.start_ms)}
              </div>
            ) : null}
          </button>
        ))}
      </div>
    </nav>
  );
}

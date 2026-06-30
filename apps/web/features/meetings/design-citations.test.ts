import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind citation evidence interaction design", () => {
  it("renders citation chips as explicit evidence jump controls", () => {
    const citationChip = source(
      "features/meetings/components/citations/citation-chip.tsx"
    );

    expect(citationChip).toContain("data-citation-chip");
    expect(citationChip).toContain("data-citation-time");
    expect(citationChip).toContain("跳转到证据");
    expect(citationChip).toContain("证据来源");
    expect(citationChip).toContain("border-evidence-border");
  });

  it("tracks temporary citation pulse separately from selected evidence", () => {
    const workbench = source("features/meetings/meeting-workbench.tsx");

    expect(workbench).toContain("highlightResetRef");
    expect(workbench).toContain("setPulsedSegmentId");
    expect(workbench).toContain("window.setTimeout");
    expect(workbench).toContain("2800");
  });

  it("marks transcript segments with evidence active and pulse states", () => {
    const detail = source(
      "features/meetings/components/meeting-detail/meeting-detail.tsx"
    );
    const panel = source(
      "features/meetings/components/transcript/transcript-panel.tsx"
    );
    const segment = source(
      "features/meetings/components/transcript/transcript-segment.tsx"
    );

    expect(detail).toContain("pulsedSegmentId");
    expect(panel).toContain("pulsedSegmentId");
    expect(segment).toContain("data-evidence-active");
    expect(segment).toContain("data-evidence-pulse");
    expect(segment).toContain("ring-evidence/25");
  });
});

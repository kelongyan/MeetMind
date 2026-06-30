import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind workbench layout design", () => {
  it("uses a roomier app shell and meeting list rail", () => {
    expect(source("components/layout/app-shell.tsx")).toContain(
      "grid-rows-[64px_1fr]"
    );
    expect(source("components/layout/app-shell.tsx")).toContain(
      "md:grid-cols-[280px_minmax(0,1fr)]"
    );
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "lg:grid-cols-[360px_minmax(0,1fr)]"
    );
  });

  it("presents the detail area as an evidence review workspace", () => {
    const detail = source(
      "features/meetings/components/meeting-detail/meeting-detail.tsx"
    );

    expect(detail).toContain(
      "lg:grid-cols-[minmax(0,1.45fr)_minmax(380px,0.95fr)]"
    );
    expect(detail).toContain("任务");
    expect(detail).toContain("问答");
    expect(detail).toContain("处理");
  });

  it("uses a timeline-style transcript reader with evidence highlighting", () => {
    const panel = source(
      "features/meetings/components/transcript/transcript-panel.tsx"
    );
    const segment = source(
      "features/meetings/components/transcript/transcript-segment.tsx"
    );

    expect(panel).toContain("转写记录");
    expect(panel).toContain("段发言");
    expect(segment).toContain("grid-cols-[88px_minmax(0,1fr)]");
    expect(segment).toContain("border-l-evidence");
    expect(segment).toContain("bg-evidence-soft");
  });
});

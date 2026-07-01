import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind stage B workflow design", () => {
  it("adds section navigation to the transcript panel", () => {
    expect(
      existsSync(
        resolve(
          webRoot,
          "features/meetings/components/transcript/section-nav.tsx"
        )
      )
    ).toBe(true);
    expect(
      source("features/meetings/components/transcript/transcript-panel.tsx")
    ).toContain("SectionNav");
    expect(
      source("features/meetings/components/transcript/section-nav.tsx")
    ).toContain("章节导航");
  });

  it("adds a global action items overview", () => {
    expect(
      existsSync(
        resolve(
          webRoot,
          "features/meetings/components/action-items/action-items-overview.tsx"
        )
      )
    ).toBe(true);
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "action-items"
    );
    expect(
      source(
        "features/meetings/components/action-items/action-items-overview.tsx"
      )
    ).toContain("全部行动项");
  });
});

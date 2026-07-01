import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind stage C knowledge workflow design", () => {
  it("adds a workspace knowledge overview to the workbench", () => {
    expect(
      existsSync(
        resolve(
          webRoot,
          "features/meetings/components/knowledge/knowledge-overview.tsx",
        ),
      ),
    ).toBe(true);
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "KnowledgeOverview",
    );
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "knowledge",
    );
  });

  it("keeps search, decisions, and duplicate action candidates visible", () => {
    const overview = source(
      "features/meetings/components/knowledge/knowledge-overview.tsx",
    );

    expect(overview).toContain("知识库");
    expect(overview).toContain("搜索历史会议、决策或行动项");
    expect(overview).toContain("历史决策");
    expect(overview).toContain("可能重复行动项");
  });
});

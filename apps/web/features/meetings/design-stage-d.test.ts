import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind stage D operations readiness design", () => {
  it("adds a read-only operations overview to the workbench", () => {
    expect(
      existsSync(
        resolve(
          webRoot,
          "features/meetings/components/operations/operations-overview.tsx",
        ),
      ),
    ).toBe(true);
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "OperationsOverview",
    );
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "operations",
    );
  });

  it("keeps provider, telemetry, and task sync readiness visible", () => {
    const overview = source(
      "features/meetings/components/operations/operations-overview.tsx",
    );

    expect(overview).toContain("Provider 配置");
    expect(overview).toContain("调用观测");
    expect(overview).toContain("任务同步");
    expect(overview).not.toContain("API key");
  });
});

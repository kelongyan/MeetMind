import { describe, expect, it } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind insight review design", () => {
  it("splits action items into a dedicated review card", () => {
    const actionCardPath = resolve(
      webRoot,
      "features/meetings/components/insights/action-item-card.tsx"
    );

    expect(existsSync(actionCardPath)).toBe(true);
    const actionCard = readFileSync(actionCardPath, "utf8");
    expect(actionCard).toContain("ActionReviewControls");
    expect(actionCard).toContain("负责人");
    expect(actionCard).toContain("截止");
    expect(actionCard).toContain("border-l-warning");
    expect(actionCard).toContain("需补充证据");
  });

  it("keeps the generic insight card focused on non-action insights", () => {
    const insightCard = source(
      "features/meetings/components/insights/insight-card.tsx"
    );

    expect(insightCard).not.toContain("ActionReviewControls");
    expect(insightCard).not.toContain("groupId");
    expect(insightCard).toContain("InsightReviewControls");
    expect(insightCard).toContain("需补充证据");
  });

  it("routes action groups through the action item card and localizes group copy", () => {
    const group = source(
      "features/meetings/components/insights/insight-group.tsx"
    );
    const viewModel = source("features/meetings/view-model.ts");
    const panel = source(
      "features/meetings/components/insights/insights-panel.tsx"
    );

    expect(group).toContain("ActionItemCard");
    expect(group).toContain('group.id === "action_items"');
    expect(viewModel).toContain('title: "行动项"');
    expect(viewModel).toContain('title: "决策"');
    expect(panel).toContain("审阅任务");
    expect(panel).toContain("AI 草稿");
  });
});

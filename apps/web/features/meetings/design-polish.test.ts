import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind final workbench polish", () => {
  it("localizes the evidence-backed Q&A surface", () => {
    const panel = source("features/meetings/components/qa/qa-panel.tsx");
    const input = source("features/meetings/components/qa/qa-input.tsx");
    const message = source("features/meetings/components/qa/qa-message.tsx");

    expect(panel).toContain("证据问答");
    expect(panel).toContain("基于当前会议");
    expect(panel).toContain("提一个问题，MeetMind 会优先从转写证据里回答。");
    expect(input).toContain("问题");
    expect(input).toContain("这次会议有哪些待办由谁负责？");
    expect(input).toContain("发送问题");
    expect(input).toContain("正在检索证据");
    expect(message).toContain("你的问题");
    expect(message).toContain("AI 回答");
    expect(message).toContain("引用证据");
    expect(message).toContain("bg-evidence-soft");
  });

  it("presents jobs as a localized processing timeline", () => {
    const panel = source("features/meetings/components/jobs/jobs-panel.tsx");
    const card = source("features/meetings/components/jobs/job-card.tsx");
    const tones = source("features/meetings/components/shared/tone-utils.ts");

    expect(panel).toContain("处理流水线");
    expect(panel).toContain("项任务");
    expect(panel).toContain("暂无处理任务");
    expect(card).toContain("data-job-status");
    expect(card).toContain("jobTypeLabel");
    expect(card).toContain("jobStatusLabel");
    expect(card).toContain("第");
    expect(card).toContain("次尝试");
    expect(card).toContain("开始处理");
    expect(card).toContain("重新排队");
    expect(card).toContain("border-l-brand-primary");
    expect(tones).toContain("export");
    expect(tones).toContain("导出");
  });

  it("keeps shared states and workflow messages in the Chinese workbench voice", () => {
    const meetingSearch = source(
      "features/meetings/components/meeting-list/meeting-search.tsx"
    );
    const panelState = source("features/meetings/components/shared/panel-state.tsx");
    const meetingDetail = source(
      "features/meetings/components/meeting-detail/meeting-detail.tsx"
    );
    const transcriptSegment = source(
      "features/meetings/components/transcript/transcript-segment.tsx"
    );
    const jobsHook = source("hooks/use-jobs.ts");
    const reviewHook = source("hooks/use-review.ts");

    expect(meetingSearch).toContain("selectedStatusLabel");
    expect(meetingSearch).toContain("全部状态");
    expect(panelState).toContain('label = "加载中..."');
    expect(panelState).toContain("text-text-muted");
    expect(meetingDetail).toContain("无法读取会议详情。");
    expect(transcriptSegment).toContain("发言人");
    expect(transcriptSegment).not.toContain("Speaker");
    expect(jobsHook).toContain("处理任务已更新");
    expect(jobsHook).toContain("重试任务已排队。");
    expect(reviewHook).toContain("审阅结果已更新。");
    expect(reviewHook).toContain("行动项已更新。");
  });
});

import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const webRoot = resolve(__dirname, "../..");

function source(path: string): string {
  return readFileSync(resolve(webRoot, path), "utf8");
}

describe("MeetMind workbench layout design", () => {
  it("uses a roomier app shell and meeting list rail", () => {
    const shell = source("components/layout/app-shell.tsx");

    expect(shell).toContain(
      "grid-rows-[64px_1fr]"
    );
    expect(shell).toContain(
      "md:grid-cols-[304px_minmax(0,1fr)]"
    );
    expect(shell).not.toContain("w-[280px] translate-x-0 transition-transform");
    expect(source("features/meetings/meeting-workbench.tsx")).toContain(
      "lg:grid-cols-[360px_minmax(0,1fr)]"
    );
  });

  it("anchors the phase 1 shell, header, and sidebar as one workbench", () => {
    const shell = source("components/layout/app-shell.tsx");
    const header = source("components/layout/app-header.tsx");
    const sidebar = source("components/layout/app-sidebar.tsx");
    const layout = source("app/layout.tsx");

    expect(shell).toContain("min-h-[calc(100vh-64px)]");
    expect(shell).toContain("bg-black/35");
    expect(shell).toContain("shadow-xl md:shadow-none");
    expect(header).toContain("sticky top-0 z-20 flex h-16");
    expect(header).toContain("bg-surface/95");
    expect(header).toContain("可信证据链");
    expect(header).toContain('size="icon-sm"');
    expect(header).toContain("TooltipContent");
    expect(sidebar).toContain('aria-label="主导航和上传入口"');
    expect(sidebar).toContain("bg-surface-subtle/70");
    expect(sidebar).toContain("border-l-2 border-brand-primary");
    expect(sidebar).toContain("上传入口");
    expect(sidebar).toContain("border border-evidence-border bg-evidence-soft p-3 text-xs text-evidence");
    expect(layout).toContain("focus-visible");
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

  it("anchors the phase 2 meeting screen as a focused review workspace", () => {
    const workbench = source("features/meetings/meeting-workbench.tsx");
    const detail = source(
      "features/meetings/components/meeting-detail/meeting-detail.tsx"
    );
    const header = source(
      "features/meetings/components/meeting-detail/meeting-header.tsx"
    );
    const listItem = source(
      "features/meetings/components/meeting-list/meeting-list-item.tsx"
    );

    expect(workbench).toContain('aria-label="会议工作台视图"');
    expect(workbench).toContain("min-h-[calc(100vh-144px)]");
    expect(workbench).toContain("flex min-h-0 flex-col");
    expect(detail).toContain('data-workspace-region="evidence-review"');
    expect(detail).toContain('aria-label="审阅辅助区"');
    expect(detail).toContain("bg-surface-subtle/70");
    expect(header).toContain("转写");
    expect(header).toContain("资源");
    expect(header).toContain("证据");
    expect(header).toContain("tabular-nums");
    expect(listItem).toContain("data-selected");
    expect(listItem).toContain("hover:bg-surface-subtle");
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
    expect(segment).toContain("grid-cols-[96px_minmax(0,1fr)]");
    expect(segment).toContain("border-l-evidence");
    expect(segment).toContain("bg-evidence-soft");
  });

  it("keeps transcript and companion panels readable inside the phase 2 screen", () => {
    const panel = source(
      "features/meetings/components/transcript/transcript-panel.tsx"
    );
    const segment = source(
      "features/meetings/components/transcript/transcript-segment.tsx"
    );
    const sectionNav = source(
      "features/meetings/components/transcript/section-nav.tsx"
    );
    const insights = source(
      "features/meetings/components/insights/insights-panel.tsx"
    );
    const qa = source("features/meetings/components/qa/qa-panel.tsx");
    const jobs = source("features/meetings/components/jobs/jobs-panel.tsx");

    expect(panel).toContain('aria-label="转写证据流"');
    expect(panel).toContain("bg-surface/95");
    expect(panel).toContain("space-y-2 p-4");
    expect(segment).toContain("data-timeline-segment");
    expect(segment).toContain("tabular-nums");
    expect(sectionNav).toContain("snap-x");
    expect(insights).toContain("sticky top-0 z-10");
    expect(qa).toContain("sticky top-0 z-10");
    expect(jobs).toContain("sticky top-0 z-10");
  });

  it("presents phase 3 secondary pages as searchable and scannable work surfaces", () => {
    const knowledge = source(
      "features/meetings/components/knowledge/knowledge-overview.tsx"
    );
    const actions = source(
      "features/meetings/components/action-items/action-items-overview.tsx"
    );
    const operations = source(
      "features/meetings/components/operations/operations-overview.tsx"
    );

    expect(knowledge).toContain('aria-label="知识库搜索和结果"');
    expect(knowledge).toContain('aria-label="知识库辅助信息"');
    expect(knowledge).toContain("bg-surface-subtle/70");
    expect(knowledge).toContain("grid-cols-[minmax(0,1fr)_auto]");
    expect(actions).toContain('aria-label="行动项管理"');
    expect(actions).toContain(
      "md:grid-cols-[minmax(0,1.4fr)_160px_160px_auto]"
    );
    expect(actions).toContain("data-action-row");
    expect(operations).toContain('aria-label="运维状态面板"');
    expect(operations).toContain('data-operations-state="loading"');
    expect(operations).not.toContain(
      'return <PanelState label="正在读取运维状态..." variant="loading" />;'
    );
    expect(operations).toContain(
      "lg:grid-cols-[minmax(0,1.1fr)_140px_minmax(160px,0.8fr)_auto]"
    );
    expect(operations).toContain("grid-cols-2 lg:grid-cols-4");
  });

  it("unifies shared status badges, notes, and panel states for phase 3", () => {
    const badge = source(
      "features/meetings/components/shared/status-badge.tsx"
    );
    const note = source("features/meetings/components/shared/status-note.tsx");
    const panelState = source(
      "features/meetings/components/shared/panel-state.tsx"
    );

    expect(badge).toContain("data-status-tone");
    expect(badge).toContain("h-6 rounded-md px-2.5");
    expect(note).toContain('data-slot="status-note"');
    expect(note).toContain("bg-surface-subtle/80");
    expect(panelState).toContain('data-slot="panel-state"');
    expect(panelState).toContain("border-dashed bg-surface-subtle/70");
  });

  it("guards phase 4 long-content and state accessibility regressions", () => {
    const transcriptSegment = source(
      "features/meetings/components/transcript/transcript-segment.tsx"
    );
    const actionItemCard = source(
      "features/meetings/components/insights/action-item-card.tsx"
    );
    const insightCard = source(
      "features/meetings/components/insights/insight-card.tsx"
    );
    const knowledge = source(
      "features/meetings/components/knowledge/knowledge-overview.tsx"
    );
    const actions = source(
      "features/meetings/components/action-items/action-items-overview.tsx"
    );
    const statusNote = source(
      "features/meetings/components/shared/status-note.tsx"
    );
    const panelState = source(
      "features/meetings/components/shared/panel-state.tsx"
    );

    expect(transcriptSegment).toContain("break-words text-sm leading-6");
    expect(actionItemCard).toContain("break-words text-sm font-semibold");
    expect(actionItemCard).toContain("break-words text-sm font-medium");
    expect(insightCard).toContain("break-words text-sm font-semibold");
    expect(insightCard).toContain("break-words text-sm leading-6");
    expect(knowledge).toContain("break-words text-sm font-semibold");
    expect(knowledge).toContain("break-words text-sm leading-6");
    expect(actions).toContain("break-words text-sm font-semibold");
    expect(statusNote).toContain('role={state === "error" ? "alert" : "status"}');
    expect(statusNote).toContain(
      'aria-live={state === "error" ? "assertive" : "polite"}'
    );
    expect(panelState).toContain(
      'role={tone === "danger" ? "alert" : "status"}'
    );
    expect(panelState).toContain(
      'aria-live={tone === "danger" ? "assertive" : "polite"}'
    );
    expect(panelState).toContain("aria-busy={variant === \"loading\"}");
  });
});

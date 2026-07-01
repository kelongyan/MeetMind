import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Split, Workflow } from "lucide-react";
import type {
  DuplicateActionGroup,
  KnowledgeDecision,
  KnowledgeSearchResult,
} from "../../types";
import type { LoadState } from "../shared/load-state";
import { PanelState } from "../shared/panel-state";

export function KnowledgeOverview({
  workspaceId,
  query,
  searchResults,
  decisions,
  duplicateGroups,
  loadState,
  error,
  onQueryChange,
  onSearch,
  onOpenMeeting,
}: {
  workspaceId: string;
  query: string;
  searchResults: KnowledgeSearchResult[];
  decisions: KnowledgeDecision[];
  duplicateGroups: DuplicateActionGroup[];
  loadState: LoadState;
  error: string | null;
  onQueryChange: (query: string) => void;
  onSearch: () => void;
  onOpenMeeting: (meetingId: string) => void;
}) {
  return (
    <section className="grid min-h-[calc(100vh-156px)] min-w-0 gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
      <div className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
        <div className="border-b border-border p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold tracking-normal text-text-primary">
                知识库
              </h1>
              <p className="mt-1 text-sm text-text-muted">
                当前工作区：{workspaceId}
              </p>
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <div className="relative min-w-0 flex-1">
              <Search
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted"
                aria-hidden="true"
              />
              <Input
                className="pl-9"
                placeholder="搜索历史会议、决策或行动项"
                value={query}
                onChange={(event) => onQueryChange(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") onSearch();
                }}
              />
            </div>
            <Button type="button" onClick={onSearch}>
              搜索
            </Button>
          </div>
        </div>

        {loadState === "error" ? (
          <PanelState label={error ?? "无法读取知识库。"} tone="danger" />
        ) : searchResults.length === 0 ? (
          <PanelState label="暂无搜索结果。" />
        ) : (
          <ScrollArea className="flex-1">
            <div className="divide-y divide-border">
              {searchResults.map((result) => (
                <article key={`${result.source_type}-${result.source_id}`} className="p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="text-xs font-medium text-evidence">
                        {result.meeting_title} · {sourceTypeLabel(result.source_type)}
                      </div>
                      <h2 className="mt-1 text-sm font-semibold text-text-primary">
                        {result.title}
                      </h2>
                      <p className="mt-1 text-sm leading-6 text-text-secondary">
                        {result.snippet}
                      </p>
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => onOpenMeeting(result.meeting_id)}
                    >
                      打开来源
                    </Button>
                  </div>
                </article>
              ))}
            </div>
          </ScrollArea>
        )}
      </div>

      <aside className="grid min-h-0 gap-4">
        <section className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <Workflow className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">历史决策</h2>
          </div>
          <div className="max-h-[38vh] overflow-auto">
            {decisions.length === 0 ? (
              <PanelState label="暂无历史决策。" />
            ) : (
              <div className="divide-y divide-border">
                {decisions.map((decision) => (
                  <article key={decision.id} className="p-4">
                    <div className="text-xs font-medium text-evidence">
                      {decision.meeting_title}
                    </div>
                    <h3 className="mt-1 text-sm font-semibold text-text-primary">
                      {decision.title}
                    </h3>
                    <p className="mt-1 text-sm leading-6 text-text-secondary">
                      {decision.body}
                    </p>
                    <Button
                      className="mt-3"
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => onOpenMeeting(decision.meeting_id)}
                    >
                      查看会议
                    </Button>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <Split className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">可能重复行动项</h2>
          </div>
          <div className="max-h-[38vh] overflow-auto">
            {duplicateGroups.length === 0 ? (
              <PanelState label="暂无重复提示。" />
            ) : (
              <div className="divide-y divide-border">
                {duplicateGroups.map((group, groupIndex) => (
                  <article key={`${group.reason}-${groupIndex}`} className="p-4">
                    <div className="text-xs font-medium text-text-muted">
                      {duplicateReasonLabel(group.reason)}
                    </div>
                    <div className="mt-2 space-y-2">
                      {group.items.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className="block w-full rounded-md border border-border bg-surface-subtle px-3 py-2 text-left text-sm hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring"
                          onClick={() => item.meeting_id && onOpenMeeting(item.meeting_id)}
                        >
                          <div className="font-medium text-text-primary">
                            {item.description}
                          </div>
                          <div className="mt-0.5 text-xs text-text-muted">
                            {item.owner_text || "未指定负责人"} · {item.status}
                          </div>
                        </button>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>
      </aside>
    </section>
  );
}

function sourceTypeLabel(sourceType: string): string {
  if (sourceType === "action_item") return "行动项";
  if (sourceType === "insight_item") return "洞察";
  return "转写";
}

function duplicateReasonLabel(reason: string): string {
  if (reason === "similar_owner_and_description") {
    return "负责人和描述相近";
  }
  return reason;
}

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Cable, Settings2 } from "lucide-react";
import type {
  ProviderStatusList,
  ProviderTelemetryList,
  TaskSyncStatus,
} from "../../types";
import { PanelState } from "../shared/panel-state";
import { StatusBadge } from "../shared/status-badge";
import type { LoadState } from "../shared/load-state";

export function OperationsOverview({
  providerStatus,
  telemetry,
  taskSyncStatus,
  loadState,
  error,
  onRefresh,
}: {
  providerStatus: ProviderStatusList | null;
  telemetry: ProviderTelemetryList | null;
  taskSyncStatus: TaskSyncStatus | null;
  loadState: LoadState;
  error: string | null;
  onRefresh: () => void;
}) {
  if (loadState === "loading") {
    return <PanelState label="正在读取运维状态..." variant="loading" />;
  }

  if (loadState === "error") {
    return <PanelState label={error ?? "无法读取运维状态。"} tone="danger" />;
  }

  return (
    <section className="grid min-h-[calc(100vh-156px)] min-w-0 gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.85fr)]">
      <div className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border p-4">
          <div>
            <div className="flex items-center gap-2">
              <Settings2 className="h-4 w-4 text-brand-primary" aria-hidden="true" />
              <h1 className="text-xl font-semibold tracking-normal text-text-primary">
                Provider 配置
              </h1>
            </div>
            <p className="mt-1 text-sm text-text-muted">
              只展示可用性和模型，不展示密钥或 webhook 地址。
            </p>
          </div>
          <Button variant="outline" size="sm" type="button" onClick={onRefresh}>
            刷新
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="divide-y divide-border">
            {(providerStatus?.providers ?? []).map((item) => (
              <article key={item.capability} className="p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge
                        label={item.configured ? "已配置" : "未配置"}
                        tone={item.configured ? "success" : "warning"}
                      />
                      <span className="text-xs font-medium uppercase text-evidence">
                        {item.capability}
                      </span>
                    </div>
                    <h2 className="mt-2 text-sm font-semibold text-text-primary">
                      {item.provider}
                    </h2>
                    <p className="mt-1 text-sm text-text-secondary">
                      {item.message}
                    </p>
                  </div>
                  <span className="rounded-md border border-border bg-surface-subtle px-2 py-1 text-xs text-text-muted">
                    {item.model ?? "无模型"}
                  </span>
                </div>
              </article>
            ))}
          </div>
        </ScrollArea>
      </div>

      <aside className="grid min-h-0 gap-4">
        <section className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <Activity className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">调用观测</h2>
          </div>
          <div className="max-h-[42vh] overflow-auto">
            {(telemetry?.summaries ?? []).length === 0 ? (
              <PanelState label="暂无 provider 调用记录。" />
            ) : (
              <div className="divide-y divide-border">
                {telemetry?.summaries.map((summary) => (
                  <article
                    key={`${summary.provider}-${summary.operation}-${summary.model}`}
                    className="p-4"
                  >
                    <div className="text-xs font-medium text-evidence">
                      {summary.provider} · {summary.operation}
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-text-muted">
                      <span>调用：{summary.call_count}</span>
                      <span>失败：{summary.failure_count}</span>
                      <span>均耗时：{summary.average_latency_ms}ms</span>
                      <span>估算成本：${summary.cost_estimate_usd}</span>
                    </div>
                    <p className="mt-2 text-xs text-text-muted">
                      {summary.model ?? "未记录模型"} ·{" "}
                      {summary.prompt_version ?? "无 prompt 版本"}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <Cable className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">任务同步</h2>
          </div>
          {taskSyncStatus ? (
            <div className="p-4">
              <StatusBadge
                label={taskSyncStatus.configured ? "已配置" : "未配置"}
                tone={taskSyncStatus.configured ? "success" : "warning"}
              />
              <h3 className="mt-3 text-sm font-semibold text-text-primary">
                {taskSyncStatus.provider}
              </h3>
              <p className="mt-1 text-sm leading-6 text-text-secondary">
                {taskSyncStatus.message}
              </p>
              <p className="mt-2 text-xs text-text-muted">
                推送能力：{taskSyncStatus.supports_push ? "可用" : "不可用"}
              </p>
            </div>
          ) : (
            <PanelState label="暂无任务同步状态。" />
          )}
        </section>
      </aside>
    </section>
  );
}

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
  const providerRows = providerStatus?.providers ?? [];
  const telemetryRows = telemetry?.summaries ?? [];

  return (
    <section
      className="grid min-h-[calc(100vh-156px)] min-w-0 gap-4 xl:grid-cols-[minmax(0,1fr)_380px]"
      aria-label="运维状态面板"
    >
      {loadState === "loading" ? (
        <div
          data-operations-state="loading"
          className="min-h-0 overflow-hidden rounded-lg border border-border bg-surface xl:col-span-2"
        >
          <PanelState label="正在读取运维状态..." variant="loading" />
        </div>
      ) : loadState === "error" ? (
        <div
          data-operations-state="error"
          className="min-h-0 overflow-hidden rounded-lg border border-border bg-surface xl:col-span-2"
        >
          <PanelState label={error ?? "无法读取运维状态。"} tone="danger" />
        </div>
      ) : (
        <>
      <div className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-surface">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-surface-subtle/70 p-4">
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
          {providerRows.length === 0 ? (
            <PanelState label="暂无 provider 配置状态。" />
          ) : (
            <>
              <div className="hidden border-b border-border bg-surface px-4 py-2 text-xs font-medium uppercase text-text-muted lg:grid lg:grid-cols-[minmax(0,1.1fr)_140px_minmax(160px,0.8fr)_auto] lg:items-center">
                <span>Provider</span>
                <span>状态</span>
                <span>模型</span>
                <span className="text-right">能力</span>
              </div>
              <div className="divide-y divide-border">
                {providerRows.map((item) => (
                  <article
                    key={item.capability}
                    className="grid gap-3 p-4 hover:bg-surface-subtle/60 lg:grid-cols-[minmax(0,1.1fr)_140px_minmax(160px,0.8fr)_auto] lg:items-center"
                  >
                    <div className="min-w-0">
                      <h2 className="break-words text-sm font-semibold text-text-primary">
                        {item.provider}
                      </h2>
                      <p className="mt-1 break-words text-sm leading-6 text-text-secondary">
                        {item.message}
                      </p>
                    </div>
                    <StatusBadge
                      label={item.configured ? "已配置" : "未配置"}
                      tone={item.configured ? "success" : "warning"}
                    />
                    <span className="w-fit break-words rounded-md border border-border bg-surface-subtle px-2 py-1 text-xs text-text-muted">
                      {item.model ?? "无模型"}
                    </span>
                    <span className="break-words text-xs font-medium uppercase text-evidence lg:justify-self-end">
                      {item.capability}
                    </span>
                  </article>
                ))}
              </div>
            </>
          )}
        </ScrollArea>
      </div>

      <aside className="grid min-h-0 gap-4">
        <section className="overflow-hidden rounded-lg border border-border bg-surface">
          <div className="flex items-center gap-2 border-b border-border bg-surface-subtle/70 px-4 py-3">
            <Activity className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">调用观测</h2>
          </div>
          <div className="max-h-[42vh] overflow-auto">
            {telemetryRows.length === 0 ? (
              <PanelState label="暂无 provider 调用记录。" />
            ) : (
              <div className="divide-y divide-border">
                {telemetryRows.map((summary) => (
                  <article
                    key={`${summary.provider}-${summary.operation}-${summary.model}`}
                    className="p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="min-w-0">
                        <div className="text-xs font-medium text-evidence">
                          {summary.provider} · {summary.operation}
                        </div>
                        <p className="mt-1 break-words text-xs text-text-muted">
                          {summary.model ?? "未记录模型"} ·{" "}
                          {summary.prompt_version ?? "无 prompt 版本"}
                        </p>
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-2 lg:grid-cols-4 gap-2 text-xs text-text-muted">
                      <span className="rounded-md border border-border bg-surface-subtle px-2 py-1">
                        调用 {summary.call_count}
                      </span>
                      <span className="rounded-md border border-border bg-surface-subtle px-2 py-1">
                        失败 {summary.failure_count}
                      </span>
                      <span className="rounded-md border border-border bg-surface-subtle px-2 py-1">
                        均耗时 {summary.average_latency_ms}ms
                      </span>
                      <span className="rounded-md border border-border bg-surface-subtle px-2 py-1">
                        成本 ${summary.cost_estimate_usd}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="overflow-hidden rounded-lg border border-border bg-surface">
          <div className="flex items-center gap-2 border-b border-border bg-surface-subtle/70 px-4 py-3">
            <Cable className="h-4 w-4 text-brand-primary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">任务同步</h2>
          </div>
          {taskSyncStatus ? (
            <div className="p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="break-words text-sm font-semibold text-text-primary">
                  {taskSyncStatus.provider}
                </h3>
                <StatusBadge
                  label={taskSyncStatus.configured ? "已配置" : "未配置"}
                  tone={taskSyncStatus.configured ? "success" : "warning"}
                />
              </div>
              <p className="mt-3 break-words text-sm leading-6 text-text-secondary">
                {taskSyncStatus.message}
              </p>
              <div className="mt-3 rounded-md border border-border bg-surface-subtle px-3 py-2 text-xs text-text-muted">
                推送能力：{taskSyncStatus.supports_push ? "可用" : "不可用"}
              </div>
            </div>
          ) : (
            <PanelState label="暂无任务同步状态。" />
          )}
        </section>
      </aside>
        </>
      )}
    </section>
  );
}

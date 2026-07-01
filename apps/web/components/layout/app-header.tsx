import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import { FileAudio, Menu, RefreshCcw, ShieldCheck } from "lucide-react";

export function AppHeader({
  onRefresh,
  onToggleSidebar,
}: {
  onRefresh: () => void;
  onToggleSidebar: () => void;
}) {
  return (
    <header className="flex items-center justify-between border-b border-border bg-surface px-4 md:px-6">
      <div className="flex items-center gap-3">
        {/* Mobile hamburger menu */}
        <Button
          variant="ghost"
          size="sm"
          type="button"
          className="md:hidden"
          onClick={onToggleSidebar}
          aria-label="打开导航菜单"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </Button>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-brand-border bg-brand-soft text-brand-primary">
            <FileAudio className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <p className="text-base font-semibold leading-5 text-text-primary">
              MeetMind
            </p>
            <p className="text-xs leading-4 text-text-muted">可信会议审阅工作台</p>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="hidden items-center gap-1.5 rounded-md border border-evidence-border bg-evidence-soft px-2.5 py-1 text-xs font-medium text-evidence md:flex">
          <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
          证据优先
        </div>
        <ThemeToggle />
        <Button variant="outline" size="sm" onClick={onRefresh} type="button">
          <RefreshCcw className="h-4 w-4" aria-hidden="true" />
          刷新
        </Button>
      </div>
    </header>
  );
}

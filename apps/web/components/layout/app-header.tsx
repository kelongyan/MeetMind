import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FileAudio, Menu, RefreshCcw, ShieldCheck } from "lucide-react";

export function AppHeader({
  onRefresh,
  onToggleSidebar,
}: {
  onRefresh: () => void;
  onToggleSidebar: () => void;
}) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-surface/90 md:px-5 xl:px-6">
      <div className="flex min-w-0 items-center gap-3">
        {/* Mobile hamburger menu */}
        <Button
          variant="ghost"
          size="icon-sm"
          type="button"
          className="md:hidden"
          onClick={onToggleSidebar}
          aria-label="打开导航菜单"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </Button>
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-brand-border bg-brand-soft text-brand-primary">
            <FileAudio className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-base font-semibold leading-5 text-text-primary">
              MeetMind
            </p>
            <p className="hidden truncate text-xs leading-4 text-text-muted sm:block">
              可信会议审阅工作台
            </p>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="hidden items-center gap-1.5 rounded-md border border-evidence-border bg-evidence-soft px-2.5 py-1 text-xs font-medium text-evidence md:inline-flex">
          <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
          可信证据链
        </div>
        <ThemeToggle />
        <Tooltip>
          <TooltipTrigger
            render={
              <Button
                variant="outline"
                size="icon-sm"
                onClick={onRefresh}
                type="button"
                aria-label="刷新数据"
              >
                <RefreshCcw className="h-4 w-4" aria-hidden="true" />
              </Button>
            }
          />
          <TooltipContent>刷新数据</TooltipContent>
        </Tooltip>
      </div>
    </header>
  );
}

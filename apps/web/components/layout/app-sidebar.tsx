"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BookOpen,
  CheckSquare,
  ChevronDown,
  ChevronRight,
  FileAudio,
  Loader2,
  Settings2,
  UploadCloud,
} from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import type { ProcessingJob } from "@/features/meetings/types";
import type { LoadState } from "@/features/meetings/components/shared/load-state";
import { StatusNote } from "@/features/meetings/components/shared/status-note";
import type { ActiveView } from "./app-shell";

const NAV_ITEMS: Array<{
  view: ActiveView;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}> = [
  { view: "meetings", icon: FileAudio, label: "会议" },
  { view: "knowledge", icon: BookOpen, label: "知识库" },
  { view: "action-items", icon: CheckSquare, label: "行动项" },
  { view: "operations", icon: Settings2, label: "运维" },
];

export function AppSidebar({
  activeView,
  onViewChange,
  title,
  language,
  uploadState,
  uploadMessage,
  lastUploadJob,
  onTitleChange,
  onLanguageChange,
  onFileChange,
  onSubmitUpload,
}: {
  activeView: ActiveView;
  onViewChange: (view: ActiveView) => void;
  title: string;
  language: string;
  file: File | null;
  uploadState: LoadState;
  uploadMessage: string | null;
  lastUploadJob: ProcessingJob | null;
  onTitleChange: (title: string) => void;
  onLanguageChange: (language: string) => void;
  onFileChange: (file: File | null) => void;
  onSubmitUpload: (event: FormEvent<HTMLFormElement>) => void;
}) {
  const [uploadExpanded, setUploadExpanded] = useState(false);

  useEffect(() => {
    if (uploadState === "loading" || lastUploadJob) {
      setUploadExpanded(true);
    }
  }, [uploadState, lastUploadJob]);

  return (
    <aside className="h-full overflow-y-auto border-b border-border bg-surface md:border-b-0 md:border-r">
      <div className="space-y-5 p-4">
        <div className="rounded-lg border border-brand-border bg-brand-soft p-3">
          <p className="text-sm font-semibold text-brand-primary">
            单会议可信闭环
          </p>
          <p className="mt-1 text-xs leading-5 text-text-secondary">
            上传、转写、提取行动项，并用引用回到原始发言。
          </p>
        </div>

        <nav aria-label="主导航" role="tablist" className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <SidebarNavItem
              key={item.view}
              icon={item.icon}
              active={activeView === item.view}
              onClick={() => onViewChange(item.view)}
            >
              {item.label}
            </SidebarNavItem>
          ))}
        </nav>

        <div>
          <button
            type="button"
            className="flex w-full items-center justify-between border-t border-border pb-4 pt-5 text-left"
            onClick={() => setUploadExpanded((prev) => !prev)}
          >
            <span>
              <span className="block text-sm font-semibold text-text-primary">
                新建会议
              </span>
              <span className="mt-0.5 block text-xs text-text-muted">
                支持音频、视频、转写文本和字幕
              </span>
            </span>
            <div className="flex items-center gap-2">
              {uploadState === "loading" ? (
                <Loader2
                  className="h-4 w-4 animate-spin text-brand-primary"
                  aria-label="上传中"
                />
              ) : null}
              {uploadExpanded ? (
                <ChevronDown className="h-4 w-4 text-text-muted" />
              ) : (
                <ChevronRight className="h-4 w-4 text-text-muted" />
              )}
            </div>
          </button>

          {uploadExpanded ? (
            <form className="space-y-4" onSubmit={onSubmitUpload}>
              <div className="space-y-2">
                <Label htmlFor="meeting-title" className="text-sm">
                  标题
                </Label>
                <Input
                  id="meeting-title"
                  placeholder="例如：产品周会"
                  value={title}
                  onChange={(event) => onTitleChange(event.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="meeting-language" className="text-sm">
                  语言
                </Label>
                <Select
                  value={language}
                  onValueChange={(value) => onLanguageChange(value ?? "zh-CN")}
                >
                  <SelectTrigger id="meeting-language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="zh-CN">中文</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="auto">自动识别</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="meeting-file" className="text-sm">
                  文件
                </Label>
                <Input
                  id="meeting-file"
                  type="file"
                  accept=".mp3,.wav,.mp4,.m4a,.webm,.txt,.srt,.vtt,audio/*,video/*,text/plain"
                  onChange={(event) => {
                    onFileChange(event.target.files?.[0] ?? null);
                  }}
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={uploadState === "loading"}
              >
                <UploadCloud className="h-4 w-4" aria-hidden="true" />
                创建并上传
              </Button>

              {uploadMessage ? (
                <StatusNote state={uploadState} message={uploadMessage} />
              ) : null}

              {lastUploadJob ? (
                <div className="rounded-md border border-brand-border bg-brand-soft p-3 text-xs text-brand-primary">
                  <div className="font-semibold">
                    处理任务：{lastUploadJob.status}
                  </div>
                  <div className="mt-1">
                    {lastUploadJob.job_type} · {lastUploadJob.id}
                  </div>
                </div>
              ) : null}
            </form>
          ) : null}
        </div>
      </div>
    </aside>
  );
}

function SidebarNavItem({
  icon: Icon,
  active,
  onClick,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  active?: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      className={[
        "flex h-10 w-full items-center gap-2 rounded-md px-3 text-sm font-medium transition-colors",
        active
          ? "bg-brand-soft text-brand-primary ring-1 ring-brand-border"
          : "text-text-secondary hover:bg-muted hover:text-text-primary",
      ].join(" ")}
      onClick={onClick}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {children}
    </button>
  );
}

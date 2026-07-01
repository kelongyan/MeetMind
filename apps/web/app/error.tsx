"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCcw } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[MeetMind ErrorBoundary]", error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-page p-6">
      <div className="max-w-md rounded-lg border border-border bg-surface p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-danger-soft">
          <AlertTriangle className="h-6 w-6 text-danger" aria-hidden="true" />
        </div>
        <h1 className="text-lg font-semibold text-text-primary">页面出现异常</h1>
        <p className="mt-2 text-sm leading-6 text-text-secondary">
          {error.message || "应用遇到了意外错误，请尝试刷新页面。"}
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button variant="outline" onClick={() => reset()}>
            <RefreshCcw className="h-4 w-4" aria-hidden="true" />
            重试
          </Button>
          <Button onClick={() => (window.location.href = "/")}>
            返回首页
          </Button>
        </div>
      </div>
    </div>
  );
}

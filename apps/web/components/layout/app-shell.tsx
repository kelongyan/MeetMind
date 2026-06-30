import type { ReactNode } from "react";
import { AppHeader } from "./app-header";

export function AppShell({
  children,
  sidebar,
  onRefresh,
}: {
  children: ReactNode;
  sidebar: ReactNode;
  onRefresh: () => void;
}) {
  return (
    <div className="grid min-h-screen grid-rows-[64px_1fr] bg-page">
      <AppHeader onRefresh={onRefresh} />
      <div className="grid min-h-0 md:grid-cols-[280px_minmax(0,1fr)]">
        {sidebar}
        <main className="min-w-0 overflow-hidden p-4 md:p-5 xl:p-6">{children}</main>
      </div>
    </div>
  );
}

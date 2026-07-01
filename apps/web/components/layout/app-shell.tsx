import type { ReactNode } from "react";
import { AppHeader } from "./app-header";

export type ActiveView = "meetings" | "action-items" | "knowledge" | "operations";

export function AppShell({
  children,
  sidebar,
  onRefresh,
  sidebarOpen,
  onToggleSidebar,
}: {
  children: ReactNode;
  sidebar: ReactNode;
  onRefresh: () => void;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}) {
  return (
    <div className="grid min-h-screen grid-rows-[64px_1fr] bg-page">
      <AppHeader
        onRefresh={onRefresh}
        onToggleSidebar={onToggleSidebar}
      />
      <div className="grid min-h-0 md:grid-cols-[280px_minmax(0,1fr)]">
        {/* Mobile: overlay sidebar when open; Desktop: always visible */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/30 md:hidden"
            onClick={onToggleSidebar}
            aria-hidden="true"
          />
        )}
        <aside
          className={`
            fixed inset-y-0 left-0 z-40 w-[280px] translate-x-0 transition-transform duration-200
            md:static md:z-auto md:translate-x-0 md:transition-none
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
          `}
        >
          <div className="h-full">{sidebar}</div>
        </aside>
        <main
          id="main-content"
          tabIndex={-1}
          className="min-w-0 overflow-hidden p-4 md:p-5 xl:p-6"
        >
          {children}
        </main>
      </div>
    </div>
  );
}

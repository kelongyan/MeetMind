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
    <div className="grid min-h-screen grid-rows-[64px_1fr] bg-page text-text-primary">
      <AppHeader
        onRefresh={onRefresh}
        onToggleSidebar={onToggleSidebar}
      />
      <div className="grid min-h-[calc(100vh-64px)] md:grid-cols-[304px_minmax(0,1fr)]">
        {/* Mobile: overlay sidebar when open; Desktop: always visible */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/35 backdrop-blur-[1px] md:hidden"
            onClick={onToggleSidebar}
            aria-hidden="true"
          />
        )}
        <aside
          className={`
            fixed inset-y-0 left-0 z-40 w-[304px] max-w-[calc(100vw-2rem)] bg-surface shadow-xl md:shadow-none transition-transform duration-200 ease-out
            md:static md:z-auto md:w-auto md:max-w-none md:translate-x-0 md:bg-transparent md:transition-none
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
          `}
        >
          <div className="h-full">{sidebar}</div>
        </aside>
        <main
          id="main-content"
          tabIndex={-1}
          className="min-w-0 overflow-hidden px-4 py-4 md:px-5 md:py-5 xl:px-6 xl:py-6"
        >
          {children}
        </main>
      </div>
    </div>
  );
}

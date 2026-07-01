import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  reviewButtonToneClassName,
  toneClassName,
} from "./components/shared/tone-utils";

const webRoot = resolve(__dirname, "../..");

describe("MeetMind visual design tokens", () => {
  it("defines the evidence workbench palette", () => {
    const globals = readFileSync(resolve(webRoot, "app/globals.css"), "utf8");

    expect(globals).toContain("--color-page: #F5F7FB");
    expect(globals).toContain("--color-surface-subtle: #F8FAFC");
    expect(globals).toContain("--color-border-default: #D9E2EC");
    expect(globals).toContain("--color-text-primary: #0F172A");
    expect(globals).toContain("--color-brand-primary: #2457F5");
    expect(globals).toContain("--color-evidence: #0F766E");
    expect(globals).toContain("--color-evidence-soft: #EAFBF7");
    expect(globals).toContain("--color-evidence-border: #99F6E4");
    expect(globals).toContain("--radius: 0.5rem");
  });

  it("defines a matching dark evidence workbench palette", () => {
    const globals = readFileSync(resolve(webRoot, "app/globals.css"), "utf8");

    expect(globals).toContain("--color-page: #0B1220");
    expect(globals).toContain("--color-surface-subtle: #172033");
    expect(globals).toContain("--color-border-default: #243244");
    expect(globals).toContain("--color-text-primary: #E5EEF9");
    expect(globals).toContain("--color-brand-primary: #6BA4FF");
    expect(globals).toContain("--color-evidence: #2DD4BF");
    expect(globals).toContain("--color-evidence-soft: #0F2F2E");
  });

  it("uses semantic tone classes instead of raw color families", () => {
    expect(toneClassName("success")).toBe(
      "border-success/20 bg-success-soft text-success"
    );
    expect(toneClassName("warning")).toBe(
      "border-warning/25 bg-warning-soft text-warning"
    );
    expect(toneClassName("danger")).toBe(
      "border-danger/20 bg-danger-soft text-danger"
    );
    expect(toneClassName("info")).toBe(
      "border-brand-primary/20 bg-brand-soft text-brand-primary"
    );
    expect(toneClassName("neutral")).toBe(
      "border-border bg-surface-subtle text-text-secondary"
    );
  });

  it("keeps review buttons quiet but stateful", () => {
    expect(reviewButtonToneClassName("neutral")).toBe(
      "border-border bg-surface text-text-secondary hover:bg-surface-subtle"
    );
    expect(reviewButtonToneClassName("success")).toBe(
      "border-success/20 bg-success-soft text-success hover:bg-success-soft/80"
    );
    expect(reviewButtonToneClassName("danger")).toBe(
      "border-danger/20 bg-danger-soft text-danger hover:bg-danger-soft/80"
    );
  });

  it("keeps base controls on the shared workbench baseline", () => {
    expect(readFileSync(resolve(webRoot, "components/ui/button.tsx"), "utf8"))
      .toContain("rounded-md");
    expect(readFileSync(resolve(webRoot, "components/ui/card.tsx"), "utf8"))
      .toContain("rounded-lg");
    expect(readFileSync(resolve(webRoot, "components/ui/input.tsx"), "utf8"))
      .toContain("bg-surface");
    expect(readFileSync(resolve(webRoot, "components/ui/select.tsx"), "utf8"))
      .toContain("w-full");
    expect(readFileSync(resolve(webRoot, "components/ui/tabs.tsx"), "utf8"))
      .toContain("bg-surface-subtle");
    expect(
      readFileSync(resolve(webRoot, "components/ui/scroll-area.tsx"), "utf8")
    ).toContain("bg-border-strong/70");
    expect(
      readFileSync(resolve(webRoot, "components/theme-toggle.tsx"), "utf8")
    ).toContain('size="icon-sm"');
    expect(readFileSync(resolve(webRoot, "components/ui/sonner.tsx"), "utf8"))
      .toContain("var(--color-surface)");
  });

  it("keeps workbench component styling semantic and non-decorative", () => {
    const componentPaths = [
      "components/layout/app-shell.tsx",
      "components/layout/app-header.tsx",
      "components/layout/app-sidebar.tsx",
      "features/meetings/meeting-workbench.tsx",
      "features/meetings/components/transcript/transcript-segment.tsx",
      "features/meetings/components/knowledge/knowledge-overview.tsx",
      "features/meetings/components/action-items/action-items-overview.tsx",
      "features/meetings/components/operations/operations-overview.tsx",
    ];

    for (const path of componentPaths) {
      const content = readFileSync(resolve(webRoot, path), "utf8");

      expect(content, path).not.toMatch(/bg-gradient|rgba\(|#[0-9A-Fa-f]{3,6}/);
    }
  });
});

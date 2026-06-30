import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  reviewButtonToneClassName,
  toneClassName,
} from "./components/shared/tone-utils";

const webRoot = resolve(__dirname, "../..");

describe("MeetMind visual design tokens", () => {
  it("defines the refreshed brand and evidence palette", () => {
    const globals = readFileSync(resolve(webRoot, "app/globals.css"), "utf8");

    expect(globals).toContain("--color-brand-primary: #1F5EFF");
    expect(globals).toContain("--color-evidence: #0891B2");
    expect(globals).toContain("--color-evidence-soft: #ECFEFF");
    expect(globals).toContain("--color-page: #F6F8FB");
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
      "border-border bg-muted text-text-secondary"
    );
  });

  it("keeps review buttons quiet but stateful", () => {
    expect(reviewButtonToneClassName("neutral")).toBe(
      "border-border bg-surface text-text-secondary hover:bg-muted"
    );
    expect(reviewButtonToneClassName("success")).toBe(
      "border-success/20 bg-success-soft text-success hover:bg-success-soft/80"
    );
    expect(reviewButtonToneClassName("danger")).toBe(
      "border-danger/20 bg-danger-soft text-danger hover:bg-danger-soft/80"
    );
  });
});

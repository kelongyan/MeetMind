import { describe, expect, it } from "vitest";

import {
  buildInsightGroups,
  filterMeetings,
  formatTimestamp,
  getMeetingStatusMeta,
} from "./view-model";

const meetings = [
  {
    id: "m-1",
    title: "Launch review",
    status: "ready_for_review",
    language: "en",
    duration_ms: 125000,
    created_at: "2026-06-29T08:00:00Z",
    updated_at: "2026-06-29T08:20:00Z",
  },
  {
    id: "m-2",
    title: "Backend sync",
    status: "failed_transcription",
    language: "zh-CN",
    duration_ms: null,
    created_at: "2026-06-29T09:00:00Z",
    updated_at: "2026-06-29T09:05:00Z",
  },
] as const;

describe("meeting workbench view model", () => {
  it("filters meetings by title and status", () => {
    expect(filterMeetings(meetings, "launch", "all")).toHaveLength(1);
    expect(filterMeetings(meetings, "", "failed")).toEqual([meetings[1]]);
    expect(filterMeetings(meetings, "sync", "ready_for_review")).toEqual([]);
  });

  it("maps backend status values to user-facing metadata", () => {
    expect(getMeetingStatusMeta("ready_for_review")).toMatchObject({
      label: "Ready for review",
      tone: "warning",
    });
    expect(getMeetingStatusMeta("failed_structuring")).toMatchObject({
      label: "Failed",
      tone: "danger",
    });
  });

  it("formats transcript timestamps consistently", () => {
    expect(formatTimestamp(0)).toBe("00:00");
    expect(formatTimestamp(65000)).toBe("01:05");
    expect(formatTimestamp(3671000)).toBe("1:01:11");
  });

  it("orders insight groups and resolves citation chips to transcript segments", () => {
    const groups = buildInsightGroups({
      actionItems: [
        {
          id: "action-1",
          description: "Prepare rollout checklist.",
          owner_text: "Nina",
          due_text: "Friday",
          status: "proposed",
          confidence: 0.86,
        },
      ],
      citations: [
        {
          id: "citation-1",
          target_type: "action_item",
          target_id: "action-1",
          segment_id: "segment-2",
          start_ms: 5000,
          end_ms: 9000,
          quote: "Nina will prepare the rollout checklist by Friday.",
          confidence: 0.9,
        },
        {
          id: "citation-2",
          target_type: "insight_item",
          target_id: "decision-1",
          segment_id: "segment-1",
          start_ms: 1000,
          end_ms: 4000,
          quote: "We decided to ship the first beta next week.",
          confidence: 0.92,
        },
      ],
      insights: [
        {
          id: "decision-1",
          type: "decision",
          title: "Ship beta",
          body: "The team decided to ship the first beta next week.",
          status: "proposed",
          confidence: 0.9,
        },
      ],
      transcriptSegments: [
        {
          id: "segment-1",
          start_ms: 1000,
          end_ms: 4000,
          text: "We decided to ship the first beta next week.",
        },
        {
          id: "segment-2",
          start_ms: 5000,
          end_ms: 9000,
          text: "Nina will prepare the rollout checklist by Friday.",
        },
      ],
    });

    expect(groups.map((group) => group.id)).toEqual([
      "action_items",
      "decisions",
      "risks",
      "summary",
      "open_questions",
    ]);
    expect(groups[0].items[0].citations[0]).toMatchObject({
      id: "citation-1",
      segmentId: "segment-2",
      label: "00:05",
      quote: "Nina will prepare the rollout checklist by Friday.",
    });
    expect(groups[1].items[0].citations[0]).toMatchObject({
      id: "citation-2",
      segmentId: "segment-1",
      label: "00:01",
    });
  });
});

import { describe, expect, it, vi } from "vitest";

import { createMeetMindApi } from "./api";

describe("MeetMind API client", () => {
  it("loads meetings from the configured backend base URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse([
        {
          id: "meeting-1",
          title: "Launch review",
          status: "ready_for_review",
          created_at: "2026-06-29T08:00:00Z",
          updated_at: "2026-06-29T08:30:00Z",
        },
      ]),
    );
    const api = createMeetMindApi("http://api.test", fetchMock);

    const meetings = await api.listMeetings();

    expect(fetchMock).toHaveBeenCalledWith("http://api.test/api/meetings", {
      headers: { Accept: "application/json" },
    });
    expect(meetings[0].title).toBe("Launch review");
  });

  it("creates a meeting and uploads a file with multipart form data", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          id: "meeting-2",
          title: "Upload flow",
          status: "uploaded",
          created_at: "2026-06-29T08:00:00Z",
          updated_at: "2026-06-29T08:00:00Z",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          duplicate: false,
          asset: { id: "asset-1", meeting_id: "meeting-2", asset_type: "audio" },
          job: { id: "job-1", status: "queued", job_type: "transcribe" },
        }),
      );
    const api = createMeetMindApi("http://api.test/", fetchMock);
    const file = new File(["audio"], "standup.wav", { type: "audio/wav" });

    const meeting = await api.createMeeting({ title: "Upload flow" });
    const upload = await api.uploadAsset(meeting.id, file);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://api.test/api/meetings",
      expect.objectContaining({
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://api.test/api/meetings/meeting-2/assets",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
    expect(upload.job?.id).toBe("job-1");
  });

  it("raises typed errors with backend details", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ detail: "Unsupported file type" }, { ok: false, status: 415 }),
    );
    const api = createMeetMindApi("http://api.test", fetchMock);

    await expect(api.listMeetings()).rejects.toMatchObject({
      status: 415,
      message: "Unsupported file type",
    });
  });

  it("asks a meeting question through the Q&A endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        conversation_id: "conversation-1",
        question: {
          id: "question-1",
          meeting_id: "meeting-1",
          conversation_id: "conversation-1",
          role: "user",
          content: "Who owns rollout?",
          citation_ids: [],
          model_name: null,
          created_at: "2026-06-29T08:00:00Z",
        },
        answer: {
          id: "answer-1",
          meeting_id: "meeting-1",
          conversation_id: "conversation-1",
          role: "assistant",
          content: "Nina owns rollout.",
          citation_ids: ["citation-1"],
          model_name: "fake-answer-model",
          created_at: "2026-06-29T08:00:01Z",
        },
        citations: [
          {
            id: "citation-1",
            meeting_id: "meeting-1",
            target_type: "answer",
            target_id: "answer-1",
            segment_id: "segment-1",
            start_ms: 1000,
            end_ms: 4000,
            quote: "Nina owns rollout.",
            confidence: 0.9,
            created_at: "2026-06-29T08:00:01Z",
          },
        ],
      }),
    );
    const api = createMeetMindApi("http://api.test", fetchMock);

    const response = await api.askQuestion("meeting-1", {
      question: "Who owns rollout?",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://api.test/api/meetings/meeting-1/qa",
      expect.objectContaining({
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: "Who owns rollout?" }),
      }),
    );
    expect(response.answer.content).toBe("Nina owns rollout.");
    expect(response.citations[0].segment_id).toBe("segment-1");
  });
});

function jsonResponse(
  body: unknown,
  init: { ok?: boolean; status?: number } = {},
): Response {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    json: () => Promise.resolve(body),
  } as Response;
}

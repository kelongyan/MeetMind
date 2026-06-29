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

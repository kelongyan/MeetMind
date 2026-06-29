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

  it("updates insights and action items through review endpoints", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          id: "insight-1",
          meeting_id: "meeting-1",
          section_id: null,
          type: "decision",
          title: "Updated decision",
          body: "Updated body",
          status: "dismissed",
          confidence: 0.8,
          model_name: null,
          model_version: null,
          prompt_version: null,
          created_at: "2026-06-29T08:00:00Z",
          updated_at: "2026-06-29T08:05:00Z",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          id: "action-1",
          meeting_id: "meeting-1",
          section_id: null,
          description: "Prepare rollout checklist.",
          owner_text: "Nina",
          owner_user_id: null,
          due_text: "Friday",
          due_date: null,
          status: "confirmed",
          confidence: 0.9,
          model_name: null,
          model_version: null,
          prompt_version: null,
          created_by_ai: true,
          confirmed_by_user_id: "local-user",
          confirmed_at: "2026-06-29T08:05:00Z",
          created_at: "2026-06-29T08:00:00Z",
          updated_at: "2026-06-29T08:05:00Z",
        }),
      );
    const api = createMeetMindApi("http://api.test", fetchMock);

    const insight = await api.updateInsight("meeting-1", "insight-1", {
      title: "Updated decision",
      status: "dismissed",
    });
    const action = await api.updateActionItem("meeting-1", "action-1", {
      status: "confirmed",
      confirmed_by_user_id: "local-user",
    });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://api.test/api/meetings/meeting-1/insights/insight-1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          title: "Updated decision",
          status: "dismissed",
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://api.test/api/meetings/meeting-1/action-items/action-1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          status: "confirmed",
          confirmed_by_user_id: "local-user",
        }),
      }),
    );
    expect(insight.status).toBe("dismissed");
    expect(action.confirmed_by_user_id).toBe("local-user");
  });

  it("loads and operates processing jobs", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse([
          {
            id: "job-1",
            meeting_id: "meeting-1",
            job_type: "structure",
            status: "queued",
            progress: 0,
            provider: "fake-llm",
            input_asset_id: "asset-1",
            retry_of_job_id: null,
            attempt_number: 1,
            failure_code: null,
            failure_message: null,
            retryable: true,
            failed_at: null,
            started_at: null,
            finished_at: null,
            created_at: "2026-06-29T08:00:00Z",
          },
        ]),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          job: { id: "job-1", job_type: "structure", status: "succeeded" },
          insights: [],
          action_items: [],
          citations: [],
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          id: "job-2",
          meeting_id: "meeting-1",
          job_type: "structure",
          status: "queued",
          progress: 0,
          provider: "fake-llm",
          input_asset_id: "asset-1",
          retry_of_job_id: "job-1",
          attempt_number: 2,
          failure_code: null,
          failure_message: null,
          retryable: true,
          failed_at: null,
          started_at: null,
          finished_at: null,
          created_at: "2026-06-29T08:05:00Z",
        }),
      );
    const api = createMeetMindApi("http://api.test", fetchMock);

    const jobs = await api.listJobs("meeting-1");
    const structureResult = await api.runJob(jobs[0]);
    const retryJob = await api.retryJob("job-1");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://api.test/api/meetings/meeting-1/jobs",
      { headers: { Accept: "application/json" } },
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://api.test/api/jobs/job-1/structure",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://api.test/api/jobs/job-1/retry",
      expect.objectContaining({ method: "POST" }),
    );
    expect(structureResult.job.status).toBe("succeeded");
    expect(retryJob.retry_of_job_id).toBe("job-1");
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

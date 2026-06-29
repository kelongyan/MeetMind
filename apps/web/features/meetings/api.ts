import type {
  ActionItem,
  AssetUploadResult,
  Citation,
  InsightItem,
  Meeting,
  MeetingAsset,
  MeetingDetailData,
  QAResponse,
  TranscriptSegment,
} from "./types";

export const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type FetchLike = typeof fetch;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface CreateMeetingPayload {
  title: string;
  description?: string | null;
  language?: string | null;
}

export interface AskQuestionPayload {
  question: string;
  conversation_id?: string | null;
}

export interface MeetMindApi {
  listMeetings(): Promise<Meeting[]>;
  getMeeting(meetingId: string): Promise<Meeting>;
  createMeeting(payload: CreateMeetingPayload): Promise<Meeting>;
  listAssets(meetingId: string): Promise<MeetingAsset[]>;
  uploadAsset(meetingId: string, file: File): Promise<AssetUploadResult>;
  listTranscript(meetingId: string): Promise<TranscriptSegment[]>;
  listInsights(meetingId: string): Promise<InsightItem[]>;
  listActionItems(meetingId: string): Promise<ActionItem[]>;
  listCitations(meetingId: string): Promise<Citation[]>;
  askQuestion(
    meetingId: string,
    payload: AskQuestionPayload,
  ): Promise<QAResponse>;
  loadMeetingDetail(meetingId: string): Promise<MeetingDetailData>;
}

export function createMeetMindApi(
  baseUrl = DEFAULT_API_BASE_URL,
  fetcher: FetchLike = fetch,
): MeetMindApi {
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, "");

  async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
    const headers = { Accept: "application/json", ...init?.headers };
    const response = await fetcher(`${normalizedBaseUrl}${path}`, {
      ...init,
      headers,
    });
    if (!response.ok) {
      throw new ApiError(await readErrorMessage(response), response.status);
    }
    return (await response.json()) as T;
  }

  return {
    listMeetings: () => requestJson<Meeting[]>("/api/meetings"),
    getMeeting: (meetingId) => requestJson<Meeting>(`/api/meetings/${meetingId}`),
    createMeeting: (payload) =>
      requestJson<Meeting>("/api/meetings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }),
    listAssets: (meetingId) =>
      requestJson<MeetingAsset[]>(`/api/meetings/${meetingId}/assets`),
    uploadAsset: (meetingId, file) => {
      const formData = new FormData();
      formData.append("file", file);
      return requestJson<AssetUploadResult>(`/api/meetings/${meetingId}/assets`, {
        method: "POST",
        body: formData,
      });
    },
    listTranscript: (meetingId) =>
      requestJson<TranscriptSegment[]>(`/api/meetings/${meetingId}/transcript`),
    listInsights: (meetingId) =>
      requestJson<InsightItem[]>(`/api/meetings/${meetingId}/insights`),
    listActionItems: (meetingId) =>
      requestJson<ActionItem[]>(`/api/meetings/${meetingId}/action-items`),
    listCitations: (meetingId) =>
      requestJson<Citation[]>(`/api/meetings/${meetingId}/citations`),
    askQuestion: (meetingId, payload) =>
      requestJson<QAResponse>(`/api/meetings/${meetingId}/qa`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }),
    async loadMeetingDetail(meetingId) {
      const [
        meeting,
        assets,
        transcriptSegments,
        insights,
        actionItems,
        citations,
      ] = await Promise.all([
        this.getMeeting(meetingId),
        this.listAssets(meetingId),
        this.listTranscript(meetingId),
        this.listInsights(meetingId),
        this.listActionItems(meetingId),
        this.listCitations(meetingId),
      ]);
      return {
        meeting,
        assets,
        transcriptSegments,
        insights,
        actionItems,
        citations,
      };
    },
  };
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
  } catch {
    return `Request failed with status ${response.status}`;
  }
  return `Request failed with status ${response.status}`;
}

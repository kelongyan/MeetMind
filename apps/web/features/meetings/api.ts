import type {
  ActionItem,
  AssetUploadResult,
  Citation,
  DuplicateActionGroup,
  InsightItem,
  JobRunResult,
  KnowledgeDecision,
  KnowledgeSearchResult,
  Meeting,
  MeetingAsset,
  MeetingDetailData,
  ProviderStatusList,
  ProviderTelemetryList,
  MeetingSection,
  ProcessingJob,
  QAMessage,
  QAResponse,
  TaskSyncStatus,
  TranscriptSegment,
} from "./types";

export const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type FetchLike = typeof fetch;
type GetAuthToken = () => string | null | Promise<string | null>;

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

export interface UpdateInsightPayload {
  title?: string;
  body?: string;
  status?: InsightItem["status"];
  confidence?: number | null;
}

export interface UpdateActionItemPayload {
  description?: string;
  owner_text?: string | null;
  owner_user_id?: string | null;
  due_text?: string | null;
  due_date?: string | null;
  status?: ActionItem["status"];
  confidence?: number | null;
  confirmed_by_user_id?: string | null;
}

export interface UploadAssetOptions {
  autoProcess?: boolean;
}

export interface ListActionItemsOptions {
  status?: ActionItem["status"];
  meetingId?: string;
}

export interface SearchKnowledgePayload {
  workspaceId: string;
  query: string;
}

export interface MeetMindApi {
  listMeetings(): Promise<Meeting[]>;
  getMeeting(meetingId: string): Promise<Meeting>;
  createMeeting(payload: CreateMeetingPayload): Promise<Meeting>;
  listJobs(meetingId: string): Promise<ProcessingJob[]>;
  listAssets(meetingId: string): Promise<MeetingAsset[]>;
  uploadAsset(
    meetingId: string,
    file: File,
    options?: UploadAssetOptions,
  ): Promise<AssetUploadResult>;
  publishMeeting(meetingId: string): Promise<Meeting>;
  runJob(job: ProcessingJob): Promise<JobRunResult>;
  retryJob(jobId: string): Promise<ProcessingJob>;
  listTranscript(meetingId: string): Promise<TranscriptSegment[]>;
  listSections(meetingId: string): Promise<MeetingSection[]>;
  listInsights(meetingId: string): Promise<InsightItem[]>;
  updateInsight(
    meetingId: string,
    insightId: string,
    payload: UpdateInsightPayload,
  ): Promise<InsightItem>;
  listActionItems(meetingId: string): Promise<ActionItem[]>;
  listGlobalActionItems(options?: ListActionItemsOptions): Promise<ActionItem[]>;
  searchKnowledge(payload: SearchKnowledgePayload): Promise<KnowledgeSearchResult[]>;
  listKnowledgeDecisions(workspaceId: string): Promise<KnowledgeDecision[]>;
  listDuplicateActionCandidates(
    workspaceId: string,
  ): Promise<DuplicateActionGroup[]>;
  getProviderStatus(): Promise<ProviderStatusList>;
  getProviderTelemetry(): Promise<ProviderTelemetryList>;
  getTaskSyncStatus(): Promise<TaskSyncStatus>;
  updateActionItem(
    meetingId: string,
    actionItemId: string,
    payload: UpdateActionItemPayload,
  ): Promise<ActionItem>;
  listCitations(meetingId: string): Promise<Citation[]>;
  askQuestion(
    meetingId: string,
    payload: AskQuestionPayload,
  ): Promise<QAResponse>;
  listQAMessages(meetingId: string, conversationId?: string): Promise<QAMessage[]>;
  loadMeetingDetail(meetingId: string): Promise<MeetingDetailData>;
}

export interface CreateApiOptions {
  fetcher?: FetchLike;
  getAuthToken?: GetAuthToken;
}

export function createMeetMindApi(
  baseUrl = DEFAULT_API_BASE_URL,
  options: CreateApiOptions = {},
): MeetMindApi {
  const fetcher = options.fetcher ?? fetch;
  const getAuthToken = options.getAuthToken;
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, "");

  async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
    const authHeaders: Record<string, string> = {};
    if (getAuthToken) {
      const token = await getAuthToken();
      if (token) {
        authHeaders["Authorization"] = `Bearer ${token}`;
      }
    }
    const headers = { Accept: "application/json", ...authHeaders, ...init?.headers };
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
    listJobs: (meetingId) =>
      requestJson<ProcessingJob[]>(`/api/meetings/${meetingId}/jobs`),
    listAssets: (meetingId) =>
      requestJson<MeetingAsset[]>(`/api/meetings/${meetingId}/assets`),
    uploadAsset: (meetingId, file, options) => {
      const formData = new FormData();
      formData.append("file", file);
      const query = options?.autoProcess ? "?auto_process=true" : "";
      return requestJson<AssetUploadResult>(
        `/api/meetings/${meetingId}/assets${query}`,
        {
          method: "POST",
          body: formData,
        },
      );
    },
    publishMeeting: (meetingId) =>
      requestJson<Meeting>(`/api/meetings/${meetingId}/publish`, {
        method: "POST",
      }),
    runJob: (job) => {
      if (job.job_type === "transcribe") {
        return requestJson<JobRunResult>(`/api/jobs/${job.id}/run`, {
          method: "POST",
        });
      }
      if (job.job_type === "structure") {
        return requestJson<JobRunResult>(`/api/jobs/${job.id}/structure`, {
          method: "POST",
        });
      }
      throw new ApiError(`${job.job_type} jobs cannot be run from the web UI`, 400);
    },
    retryJob: (jobId) =>
      requestJson<ProcessingJob>(`/api/jobs/${jobId}/retry`, {
        method: "POST",
      }),
    listTranscript: (meetingId) =>
      requestJson<TranscriptSegment[]>(`/api/meetings/${meetingId}/transcript`),
    listSections: (meetingId) =>
      requestJson<MeetingSection[]>(`/api/meetings/${meetingId}/sections`),
    listInsights: (meetingId) =>
      requestJson<InsightItem[]>(`/api/meetings/${meetingId}/insights`),
    updateInsight: (meetingId, insightId, payload) =>
      requestJson<InsightItem>(
        `/api/meetings/${meetingId}/insights/${insightId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      ),
    listActionItems: (meetingId) =>
      requestJson<ActionItem[]>(`/api/meetings/${meetingId}/action-items`),
    listGlobalActionItems: (options) => {
      const params = new URLSearchParams();
      if (options?.status) params.set("status", options.status);
      if (options?.meetingId) params.set("meeting_id", options.meetingId);
      const query = params.toString() ? `?${params.toString()}` : "";
      return requestJson<ActionItem[]>(`/api/action-items${query}`);
    },
    searchKnowledge: (payload) => {
      const params = new URLSearchParams({
        workspace_id: payload.workspaceId,
        query: payload.query,
      });
      return requestJson<KnowledgeSearchResult[]>(
        `/api/knowledge/search?${params.toString()}`,
      );
    },
    listKnowledgeDecisions: (workspaceId) => {
      const params = new URLSearchParams({ workspace_id: workspaceId });
      return requestJson<KnowledgeDecision[]>(
        `/api/knowledge/decisions?${params.toString()}`,
      );
    },
    listDuplicateActionCandidates: (workspaceId) => {
      const params = new URLSearchParams({ workspace_id: workspaceId });
      return requestJson<DuplicateActionGroup[]>(
        `/api/knowledge/duplicate-actions?${params.toString()}`,
      );
    },
    getProviderStatus: () =>
      requestJson<ProviderStatusList>("/api/operations/provider-status"),
    getProviderTelemetry: () =>
      requestJson<ProviderTelemetryList>("/api/operations/provider-telemetry"),
    getTaskSyncStatus: () =>
      requestJson<TaskSyncStatus>("/api/operations/task-sync"),
    updateActionItem: (meetingId, actionItemId, payload) =>
      requestJson<ActionItem>(
        `/api/meetings/${meetingId}/action-items/${actionItemId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      ),
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
    listQAMessages: (meetingId, conversationId) => {
      const query = conversationId
        ? `?conversation_id=${encodeURIComponent(conversationId)}`
        : "";
      return requestJson<QAMessage[]>(`/api/meetings/${meetingId}/qa${query}`);
    },
    async loadMeetingDetail(meetingId) {
      const [
        meeting,
        jobs,
        assets,
        transcriptSegments,
        sections,
        insights,
        actionItems,
        citations,
      ] = await Promise.all([
        this.getMeeting(meetingId),
        this.listJobs(meetingId),
        this.listAssets(meetingId),
        this.listTranscript(meetingId),
        this.listSections(meetingId),
        this.listInsights(meetingId),
        this.listActionItems(meetingId),
        this.listCitations(meetingId),
      ]);
      return {
        meeting,
        jobs,
        assets,
        transcriptSegments,
        sections,
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

export type MeetingStatus =
  | "uploaded"
  | "media_processing"
  | "transcribing"
  | "segmenting"
  | "structuring"
  | "citing"
  | "embedding"
  | "ready_for_review"
  | "published"
  | "failed_media_processing"
  | "failed_transcription"
  | "failed_structuring"
  | "failed_embedding";

export type JobStatus = "queued" | "running" | "succeeded" | "failed";

export type InsightType =
  | "discussion_point"
  | "decision"
  | "risk"
  | "open_question";

export type InsightStatus = "proposed" | "confirmed" | "dismissed";

export type ActionItemStatus =
  | "proposed"
  | "confirmed"
  | "in_progress"
  | "done"
  | "canceled";

export type CitationTargetType = "insight_item" | "action_item" | "answer";

export interface Meeting {
  id: string;
  title: string;
  description?: string | null;
  language?: string | null;
  workspace_id?: string | null;
  status: MeetingStatus;
  started_at?: string | null;
  ended_at?: string | null;
  duration_ms?: number | null;
  created_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProcessingJob {
  id: string;
  meeting_id?: string;
  job_type: "transcribe" | "structure" | "embed" | "export";
  status: JobStatus;
  progress?: number;
  provider?: string | null;
  failure_code?: string | null;
  failure_message?: string | null;
  retryable?: boolean;
  failed_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  created_at?: string;
}

export interface MeetingAsset {
  id: string;
  meeting_id: string;
  asset_type: "audio" | "video" | "transcript" | "subtitle" | "export";
  original_filename?: string | null;
  mime_type?: string | null;
  size_bytes?: number | null;
  duration_ms?: number | null;
  created_at?: string;
  deleted_at?: string | null;
}

export interface AssetUploadResult {
  asset: MeetingAsset;
  job: ProcessingJob | null;
  duplicate: boolean;
}

export interface TranscriptSegment {
  id: string;
  meeting_id?: string;
  speaker_id?: string | null;
  start_ms: number;
  end_ms: number;
  text: string;
  confidence?: number | null;
  source_asset_id?: string | null;
  chunk_index?: number | null;
  created_at?: string;
}

export interface InsightItem {
  id: string;
  meeting_id?: string;
  type: InsightType;
  title: string;
  body: string;
  status: InsightStatus;
  confidence?: number | null;
  model_name?: string | null;
  model_version?: string | null;
  prompt_version?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ActionItem {
  id: string;
  meeting_id?: string;
  description: string;
  owner_text?: string | null;
  owner_user_id?: string | null;
  due_text?: string | null;
  due_date?: string | null;
  status: ActionItemStatus;
  confidence?: number | null;
  model_name?: string | null;
  model_version?: string | null;
  prompt_version?: string | null;
  created_by_ai?: boolean;
  confirmed_by_user_id?: string | null;
  confirmed_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Citation {
  id: string;
  meeting_id?: string;
  target_type: CitationTargetType;
  target_id: string;
  segment_id: string;
  start_ms: number;
  end_ms: number;
  quote: string;
  confidence?: number | null;
  created_at?: string;
}

export interface MeetingDetailData {
  meeting: Meeting;
  assets: MeetingAsset[];
  transcriptSegments: TranscriptSegment[];
  insights: InsightItem[];
  actionItems: ActionItem[];
  citations: Citation[];
}

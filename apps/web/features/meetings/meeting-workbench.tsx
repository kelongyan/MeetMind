"use client";

import {
  AlertCircle,
  Bot,
  Check,
  FileAudio,
  Link2,
  Loader2,
  MessageSquareText,
  Pencil,
  Play,
  Plus,
  RefreshCcw,
  Search,
  Send,
  UploadCloud,
  X,
} from "lucide-react";
import {
  type FormEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ApiError,
  createMeetMindApi,
  type UpdateActionItemPayload,
  type UpdateInsightPayload,
} from "./api";
import type {
  Citation,
  Meeting,
  MeetingDetailData,
  ProcessingJob,
  QAResponse,
} from "./types";
import {
  buildInsightGroups,
  confidenceLabel,
  filterMeetings,
  formatDateTime,
  formatDuration,
  formatTimestamp,
  getMeetingStatusMeta,
  type MeetingStatusFilter,
  type StatusTone,
} from "./view-model";

type InsightGroup = ReturnType<typeof buildInsightGroups>[number];
type InsightCardItem = InsightGroup["items"][number];
type LoadState = "idle" | "loading" | "success" | "error";

const statusFilters: Array<{ value: MeetingStatusFilter; label: string }> = [
  { value: "all", label: "All status" },
  { value: "uploaded", label: "Uploaded" },
  { value: "transcribing", label: "Transcribing" },
  { value: "structuring", label: "Structuring" },
  { value: "ready_for_review", label: "Ready" },
  { value: "published", label: "Published" },
  { value: "failed", label: "Failed" },
];
const REVIEWER_USER_ID = "local-user";

export function MeetingWorkbench() {
  const api = useMemo(() => createMeetMindApi(), []);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [listState, setListState] = useState<LoadState>("idle");
  const [listError, setListError] = useState<string | null>(null);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);
  const [detail, setDetail] = useState<MeetingDetailData | null>(null);
  const [detailState, setDetailState] = useState<LoadState>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<MeetingStatusFilter>("all");
  const [title, setTitle] = useState("");
  const [language, setLanguage] = useState("zh-CN");
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<LoadState>("idle");
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [lastUploadJob, setLastUploadJob] = useState<ProcessingJob | null>(null);
  const [qaQuestion, setQaQuestion] = useState("");
  const [qaResponses, setQaResponses] = useState<QAResponse[]>([]);
  const [qaState, setQaState] = useState<LoadState>("idle");
  const [qaError, setQaError] = useState<string | null>(null);
  const [reviewState, setReviewState] = useState<LoadState>("idle");
  const [reviewMessage, setReviewMessage] = useState<string | null>(null);
  const [highlightedSegmentId, setHighlightedSegmentId] = useState<string | null>(
    null,
  );

  const refreshMeetings = useCallback(async () => {
    setListState("loading");
    setListError(null);
    try {
      const nextMeetings = await api.listMeetings();
      setMeetings(nextMeetings);
      setListState("success");
      setSelectedMeetingId((current) => current ?? nextMeetings[0]?.id ?? null);
    } catch (error) {
      setListState("error");
      setListError(toErrorMessage(error, "无法读取会议列表，请稍后重试。"));
    }
  }, [api]);

  const loadDetail = useCallback(
    async (meetingId: string) => {
      setDetailState("loading");
      setDetailError(null);
      try {
        const nextDetail = await api.loadMeetingDetail(meetingId);
        setDetail(nextDetail);
        setDetailState("success");
      } catch (error) {
        setDetailState("error");
        setDetailError(toErrorMessage(error, "无法读取会议详情，请稍后重试。"));
      }
    },
    [api],
  );

  useEffect(() => {
    void refreshMeetings();
  }, [refreshMeetings]);

  useEffect(() => {
    if (selectedMeetingId) {
      void loadDetail(selectedMeetingId);
    } else {
      setDetail(null);
      setDetailState("idle");
    }
    setQaQuestion("");
    setQaResponses([]);
    setQaState("idle");
    setQaError(null);
    setReviewState("idle");
    setReviewMessage(null);
    setHighlightedSegmentId(null);
  }, [loadDetail, selectedMeetingId]);

  const visibleMeetings = useMemo(
    () => filterMeetings(meetings, query, statusFilter),
    [meetings, query, statusFilter],
  );

  const selectedMeeting =
    detail?.meeting ??
    meetings.find((meeting) => meeting.id === selectedMeetingId) ??
    null;

  const insightGroups = useMemo(
    () =>
      detail
        ? buildInsightGroups({
            actionItems: detail.actionItems,
            citations: detail.citations,
            insights: detail.insights,
            transcriptSegments: detail.transcriptSegments,
          })
        : [],
    [detail],
  );

  async function handleCreateAndUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setUploadState("error");
      setUploadMessage("会议标题不能为空。");
      return;
    }

    setUploadState("loading");
    setUploadMessage(null);
    setLastUploadJob(null);
    try {
      const meeting = await api.createMeeting({
        title: trimmedTitle,
        language: language || null,
      });
      let job: ProcessingJob | null = null;
      if (file) {
        const upload = await api.uploadAsset(meeting.id, file);
        job = upload.job;
        setUploadMessage(
          upload.duplicate
            ? "文件已存在，已打开对应会议。"
            : "文件已上传，处理任务已排队。",
        );
      } else {
        setUploadMessage("会议已创建。");
      }
      setLastUploadJob(job);
      setTitle("");
      setFile(null);
      setSelectedMeetingId(meeting.id);
      setUploadState("success");
      await refreshMeetings();
    } catch (error) {
      setUploadState("error");
      setUploadMessage(toErrorMessage(error, "上传失败，请检查文件后重试。"));
    }
  }

  async function handleAskQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = qaQuestion.trim();
    if (!selectedMeetingId || !trimmedQuestion) {
      return;
    }

    setQaState("loading");
    setQaError(null);
    try {
      const response = await api.askQuestion(selectedMeetingId, {
        question: trimmedQuestion,
        conversation_id: qaResponses[0]?.conversation_id ?? null,
      });
      setQaResponses((current) => [...current, response]);
      setQaQuestion("");
      setQaState("success");
    } catch (error) {
      setQaState("error");
      setQaError(toErrorMessage(error, "无法回答该问题，请稍后重试。"));
    }
  }

  async function handleUpdateInsight(
    insightId: string,
    payload: UpdateInsightPayload,
  ) {
    if (!selectedMeetingId) {
      return;
    }
    setReviewState("loading");
    setReviewMessage(null);
    try {
      await api.updateInsight(selectedMeetingId, insightId, payload);
      await loadDetail(selectedMeetingId);
      setReviewState("success");
      setReviewMessage("Insight updated.");
    } catch (error) {
      setReviewState("error");
      setReviewMessage(toErrorMessage(error, "无法更新 insight。"));
    }
  }

  async function handleUpdateActionItem(
    actionItemId: string,
    payload: UpdateActionItemPayload,
  ) {
    if (!selectedMeetingId) {
      return;
    }
    setReviewState("loading");
    setReviewMessage(null);
    try {
      await api.updateActionItem(selectedMeetingId, actionItemId, payload);
      await loadDetail(selectedMeetingId);
      setReviewState("success");
      setReviewMessage("Action item updated.");
    } catch (error) {
      setReviewState("error");
      setReviewMessage(toErrorMessage(error, "无法更新 action item。"));
    }
  }

  function handleCitationClick(citation: Citation | { segmentId: string }) {
    const segmentId = "segment_id" in citation ? citation.segment_id : citation.segmentId;
    setHighlightedSegmentId(segmentId);
    window.requestAnimationFrame(() => {
      const element = document.getElementById(segmentDomId(segmentId));
      element?.scrollIntoView({ behavior: "smooth", block: "center" });
      element?.focus({ preventScroll: true });
    });
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <div className="grid min-h-screen grid-rows-[56px_1fr]">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 md:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-blue-200 bg-blue-50 text-blue-700">
              <FileAudio className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-semibold leading-5">MeetMind</p>
              <p className="text-xs leading-4 text-slate-500">
                Meeting workbench
              </p>
            </div>
          </div>
          <button
            className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            onClick={() => void refreshMeetings()}
            type="button"
          >
            <RefreshCcw className="h-4 w-4" aria-hidden="true" />
            Refresh
          </button>
        </header>

        <div className="grid min-h-0 md:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="border-b border-slate-200 bg-white md:border-b-0 md:border-r">
            <div className="space-y-5 p-4">
              <nav aria-label="Primary">
                <a
                  className="flex h-10 items-center rounded-md bg-blue-50 px-3 text-sm font-medium text-blue-700"
                  href="#meetings"
                >
                  Meetings
                </a>
              </nav>

              <form className="space-y-4" onSubmit={handleCreateAndUpload}>
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-900">
                    New meeting
                  </h2>
                  {uploadState === "loading" ? (
                    <Loader2
                      className="h-4 w-4 animate-spin text-blue-600"
                      aria-label="Uploading"
                    />
                  ) : null}
                </div>

                <label className="grid gap-1 text-sm font-medium text-slate-700">
                  Title
                  <input
                    className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    onChange={(event) => setTitle(event.target.value)}
                    placeholder="Weekly product sync"
                    value={title}
                  />
                </label>

                <label className="grid gap-1 text-sm font-medium text-slate-700">
                  Language
                  <select
                    className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    onChange={(event) => setLanguage(event.target.value)}
                    value={language}
                  >
                    <option value="zh-CN">中文</option>
                    <option value="en">English</option>
                    <option value="">Auto</option>
                  </select>
                </label>

                <label className="grid gap-2 text-sm font-medium text-slate-700">
                  File
                  <input
                    accept=".mp3,.wav,.mp4,.m4a,.webm,.txt,.srt,.vtt,audio/*,video/*,text/plain"
                    className="block w-full text-sm text-slate-600 file:mr-3 file:h-9 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
                    onChange={(event) => {
                      setFile(event.target.files?.[0] ?? null);
                    }}
                    type="file"
                  />
                </label>

                <button
                  className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  disabled={uploadState === "loading"}
                  type="submit"
                >
                  <UploadCloud className="h-4 w-4" aria-hidden="true" />
                  Create and upload
                </button>

                {uploadMessage ? (
                  <StatusNote state={uploadState} message={uploadMessage} />
                ) : null}

                {lastUploadJob ? (
                  <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-xs text-blue-900">
                    <div className="font-semibold">Job {lastUploadJob.status}</div>
                    <div className="mt-1 text-blue-800">
                      {lastUploadJob.job_type} · {lastUploadJob.id}
                    </div>
                  </div>
                ) : null}
              </form>
            </div>
          </aside>

          <section className="min-w-0 p-4 md:p-6" id="meetings">
            <div className="grid min-h-[calc(100vh-104px)] gap-4 xl:grid-cols-[420px_minmax(0,1fr)]">
              <section className="min-w-0 rounded-lg border border-slate-200 bg-white">
                <div className="border-b border-slate-200 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h1 className="text-xl font-semibold tracking-normal text-slate-950">
                        Meetings
                      </h1>
                      <p className="mt-1 text-sm text-slate-500">
                        {meetings.length} total
                      </p>
                    </div>
                    <button
                      className="inline-flex h-9 items-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      onClick={() => {
                        document.querySelector<HTMLInputElement>(
                          "input[placeholder='Weekly product sync']",
                        )?.focus();
                      }}
                      type="button"
                    >
                      <Plus className="h-4 w-4" aria-hidden="true" />
                      New
                    </button>
                  </div>

                  <div className="mt-4 grid gap-2 sm:grid-cols-[1fr_150px]">
                    <label className="relative block">
                      <span className="sr-only">Search meetings</span>
                      <Search
                        className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                        aria-hidden="true"
                      />
                      <input
                        className="h-10 w-full rounded-md border border-slate-300 bg-white pl-9 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="Search"
                        value={query}
                      />
                    </label>
                    <label>
                      <span className="sr-only">Filter by status</span>
                      <select
                        className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                        onChange={(event) =>
                          setStatusFilter(event.target.value as MeetingStatusFilter)
                        }
                        value={statusFilter}
                      >
                        {statusFilters.map((filter) => (
                          <option key={filter.value} value={filter.value}>
                            {filter.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </div>

                <MeetingList
                  listError={listError}
                  listState={listState}
                  meetings={visibleMeetings}
                  onSelectMeeting={setSelectedMeetingId}
                  selectedMeetingId={selectedMeetingId}
                />
              </section>

              <MeetingDetail
                detail={detail}
                detailError={detailError}
                detailState={detailState}
                highlightedSegmentId={highlightedSegmentId}
                insightGroups={insightGroups}
                onCitationClick={handleCitationClick}
                onQaQuestionChange={setQaQuestion}
                onSubmitQuestion={handleAskQuestion}
                onUpdateActionItem={handleUpdateActionItem}
                onUpdateInsight={handleUpdateInsight}
                qaError={qaError}
                qaQuestion={qaQuestion}
                qaResponses={qaResponses}
                qaState={qaState}
                reviewMessage={reviewMessage}
                reviewState={reviewState}
                selectedMeeting={selectedMeeting}
              />
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function MeetingList({
  listError,
  listState,
  meetings,
  onSelectMeeting,
  selectedMeetingId,
}: {
  listError: string | null;
  listState: LoadState;
  meetings: Meeting[];
  onSelectMeeting: (meetingId: string) => void;
  selectedMeetingId: string | null;
}) {
  if (listState === "loading" && meetings.length === 0) {
    return <PanelState label="Loading meetings" />;
  }
  if (listState === "error") {
    return (
      <PanelState
        label={listError ?? "Unable to load meetings."}
        tone="danger"
      />
    );
  }
  if (meetings.length === 0) {
    return <PanelState label="No meetings found." />;
  }

  return (
    <div className="divide-y divide-slate-100">
      {meetings.map((meeting) => {
        const meta = getMeetingStatusMeta(meeting.status);
        const isSelected = meeting.id === selectedMeetingId;
        return (
          <button
            className={[
              "grid w-full gap-2 px-4 py-3 text-left hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500",
              isSelected ? "bg-blue-50" : "bg-white",
            ].join(" ")}
            key={meeting.id}
            onClick={() => onSelectMeeting(meeting.id)}
            type="button"
          >
            <div className="flex items-start justify-between gap-3">
              <span className="min-w-0 truncate text-sm font-semibold text-slate-950">
                {meeting.title}
              </span>
              <StatusBadge label={meta.label} tone={meta.tone} />
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
              <span>{formatDateTime(meeting.created_at)}</span>
              <span className="text-right">{formatDuration(meeting.duration_ms)}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

function MeetingDetail({
  detail,
  detailError,
  detailState,
  highlightedSegmentId,
  insightGroups,
  onCitationClick,
  onQaQuestionChange,
  onSubmitQuestion,
  onUpdateActionItem,
  onUpdateInsight,
  qaError,
  qaQuestion,
  qaResponses,
  qaState,
  reviewMessage,
  reviewState,
  selectedMeeting,
}: {
  detail: MeetingDetailData | null;
  detailError: string | null;
  detailState: LoadState;
  highlightedSegmentId: string | null;
  insightGroups: ReturnType<typeof buildInsightGroups>;
  onCitationClick: (citation: Citation | { segmentId: string }) => void;
  onQaQuestionChange: (question: string) => void;
  onSubmitQuestion: (event: FormEvent<HTMLFormElement>) => void;
  onUpdateActionItem: (
    actionItemId: string,
    payload: UpdateActionItemPayload,
  ) => void;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  qaError: string | null;
  qaQuestion: string;
  qaResponses: QAResponse[];
  qaState: LoadState;
  reviewMessage: string | null;
  reviewState: LoadState;
  selectedMeeting: Meeting | null;
}) {
  if (!selectedMeeting) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white">
        <PanelState label="Create or select a meeting." />
      </section>
    );
  }

  const status = getMeetingStatusMeta(selectedMeeting.status);

  return (
    <section className="min-w-0 overflow-hidden rounded-lg border border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="truncate text-xl font-semibold tracking-normal text-slate-950">
                {selectedMeeting.title}
              </h2>
              <StatusBadge label={status.label} tone={status.tone} />
            </div>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
              <span>{selectedMeeting.language ?? "Auto language"}</span>
              <span>{formatDuration(selectedMeeting.duration_ms)}</span>
              <span>Updated {formatDateTime(selectedMeeting.updated_at)}</span>
            </div>
          </div>
          <div className="text-right text-xs text-slate-500">
            <div>{detail?.assets.length ?? 0} assets</div>
            <div>{detail?.citations.length ?? 0} citations</div>
          </div>
        </div>
      </div>

      {detailState === "loading" && !detail ? (
        <PanelState label="Loading meeting detail" />
      ) : null}
      {detailState === "error" ? (
        <PanelState
          label={detailError ?? "Unable to load meeting detail."}
          tone="danger"
        />
      ) : null}

      {detail ? (
        <div className="grid min-h-[640px] min-w-0 gap-0 lg:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.9fr)]">
          <section className="min-h-0 min-w-0 border-b border-slate-200 lg:border-b-0 lg:border-r">
            <div className="flex h-12 items-center justify-between border-b border-slate-200 px-4">
              <h3 className="text-sm font-semibold text-slate-900">Transcript</h3>
              <span className="text-xs text-slate-500">
                {detail.transcriptSegments.length} segments
              </span>
            </div>
            <div className="max-h-[640px] overflow-y-auto p-3">
              {detail.transcriptSegments.length === 0 ? (
                <PanelState label="No transcript yet." />
              ) : (
                <div className="space-y-2">
                  {detail.transcriptSegments.map((segment) => (
                    <article
                      className={[
                        "rounded-md border px-3 py-3 outline-none transition-colors",
                        highlightedSegmentId === segment.id
                          ? "border-blue-300 bg-blue-50"
                          : "border-slate-200 bg-white",
                      ].join(" ")}
                      id={segmentDomId(segment.id)}
                      key={segment.id}
                      tabIndex={-1}
                    >
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <time className="font-mono text-xs font-medium text-blue-700">
                          {formatTimestamp(segment.start_ms)}
                        </time>
                        <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                          Speaker
                        </span>
                        {segment.confidence !== undefined &&
                        segment.confidence !== null &&
                        segment.confidence < 0.7 ? (
                          <span className="text-xs text-amber-700">
                            Needs review
                          </span>
                        ) : null}
                      </div>
                      <p className="text-sm leading-6 text-slate-800">
                        {segment.text}
                      </p>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </section>

          <section className="min-h-0 min-w-0">
            <QAPanel
              onCitationClick={onCitationClick}
              onQuestionChange={onQaQuestionChange}
              onSubmitQuestion={onSubmitQuestion}
              qaError={qaError}
              qaQuestion={qaQuestion}
              qaResponses={qaResponses}
              qaState={qaState}
            />
            <InsightsPanel
              insightGroups={insightGroups}
              onCitationClick={onCitationClick}
              onUpdateActionItem={onUpdateActionItem}
              onUpdateInsight={onUpdateInsight}
              reviewMessage={reviewMessage}
              reviewState={reviewState}
            />
          </section>
        </div>
      ) : null}
    </section>
  );
}

function QAPanel({
  onCitationClick,
  onQuestionChange,
  onSubmitQuestion,
  qaError,
  qaQuestion,
  qaResponses,
  qaState,
}: {
  onCitationClick: (citation: Citation) => void;
  onQuestionChange: (question: string) => void;
  onSubmitQuestion: (event: FormEvent<HTMLFormElement>) => void;
  qaError: string | null;
  qaQuestion: string;
  qaResponses: QAResponse[];
  qaState: LoadState;
}) {
  return (
    <section className="border-b border-slate-200">
      <div className="flex h-12 items-center justify-between border-b border-slate-200 px-4">
        <div className="flex items-center gap-2">
          <MessageSquareText className="h-4 w-4 text-blue-700" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-slate-900">Ask</h3>
        </div>
        <span className="text-xs text-slate-500">Current meeting</span>
      </div>
      <div className="space-y-3 p-3">
        <form className="space-y-2" onSubmit={onSubmitQuestion}>
          <label className="grid gap-1 text-sm font-medium text-slate-700">
            Question
            <textarea
              className="min-h-20 resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6 text-slate-950 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              onChange={(event) => onQuestionChange(event.target.value)}
              placeholder="Who owns the rollout checklist?"
              value={qaQuestion}
            />
          </label>
          <button
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md bg-blue-600 px-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={qaState === "loading" || qaQuestion.trim().length === 0}
            type="submit"
          >
            {qaState === "loading" ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="h-4 w-4" aria-hidden="true" />
            )}
            Ask
          </button>
        </form>

        {qaError ? <StatusNote message={qaError} state="error" /> : null}

        <div className="max-h-72 space-y-3 overflow-y-auto">
          {qaResponses.length === 0 ? (
            <p className="rounded-md border border-dashed border-slate-200 px-3 py-3 text-sm text-slate-500">
              Ask a question to get an answer backed by transcript citations.
            </p>
          ) : (
            qaResponses.map((response) => (
              <article
                className="rounded-md border border-slate-200 bg-white p-3"
                key={response.answer.id}
              >
                <div className="mb-3 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  {response.question.content}
                </div>
                <div className="flex gap-2">
                  <Bot className="mt-1 h-4 w-4 shrink-0 text-blue-700" aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm leading-6 text-slate-800">
                      {response.answer.content}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {response.citations.length === 0 ? (
                        <span className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-medium text-amber-800">
                          No cited evidence
                        </span>
                      ) : (
                        response.citations.map((citation) => (
                          <button
                            className="inline-flex h-8 items-center gap-1 rounded-md border border-blue-200 bg-blue-50 px-2 text-xs font-medium text-blue-700 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            key={citation.id}
                            onClick={() => onCitationClick(citation)}
                            title={citation.quote}
                            type="button"
                          >
                            <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                            {formatTimestamp(citation.start_ms)}
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}

function InsightsPanel({
  insightGroups,
  onCitationClick,
  onUpdateActionItem,
  onUpdateInsight,
  reviewMessage,
  reviewState,
}: {
  insightGroups: ReturnType<typeof buildInsightGroups>;
  onCitationClick: (citation: { segmentId: string }) => void;
  onUpdateActionItem: (
    actionItemId: string,
    payload: UpdateActionItemPayload,
  ) => void;
  onUpdateInsight: (insightId: string, payload: UpdateInsightPayload) => void;
  reviewMessage: string | null;
  reviewState: LoadState;
}) {
  const reviewDisabled = reviewState === "loading";

  return (
    <section>
      <div className="flex h-12 items-center justify-between border-b border-slate-200 px-4">
        <h3 className="text-sm font-semibold text-slate-900">Insights</h3>
        {reviewState === "loading" ? (
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" aria-hidden="true" />
        ) : (
          <span className="text-xs text-slate-500">AI proposed</span>
        )}
      </div>
      <div className="max-h-[360px] overflow-y-auto p-3">
        {reviewMessage ? (
          <div className="mb-3">
            <StatusNote message={reviewMessage} state={reviewState} />
          </div>
        ) : null}
        <div className="space-y-4">
          {insightGroups.map((group) => (
            <section key={group.id}>
              <div className="mb-2 flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-900">
                  {group.title}
                </h4>
                <span className="text-xs text-slate-500">
                  {group.items.length}
                </span>
              </div>
              {group.items.length === 0 ? (
                <p className="rounded-md border border-dashed border-slate-200 px-3 py-3 text-sm text-slate-500">
                  {group.emptyLabel}
                </p>
              ) : (
                <div className="space-y-2">
                  {group.items.map((item) => (
                    <article
                      className="rounded-md border border-slate-200 bg-white p-3"
                      key={item.id}
                    >
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <StatusBadge
                          label={item.status}
                          tone={item.status === "confirmed" ? "success" : "info"}
                        />
                        <span className="text-xs text-slate-500">
                          {confidenceLabel(item.confidence)}
                        </span>
                      </div>
                      <h5 className="text-sm font-semibold leading-5 text-slate-950">
                        {item.title}
                      </h5>
                      {item.ownerText || item.dueText ? (
                        <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
                          {item.ownerText ? <span>{item.ownerText}</span> : null}
                          {item.dueText ? <span>{item.dueText}</span> : null}
                        </div>
                      ) : null}
                      {item.body !== item.title ? (
                        <p className="mt-2 text-sm leading-6 text-slate-700">
                          {item.body}
                        </p>
                      ) : null}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.citations.length === 0 ? (
                          <span className="rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-medium text-amber-800">
                            Needs source
                          </span>
                        ) : (
                          item.citations.map((citation) => (
                            <button
                              className="inline-flex h-8 items-center gap-1 rounded-md border border-blue-200 bg-blue-50 px-2 text-xs font-medium text-blue-700 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                              key={citation.id}
                              onClick={() => onCitationClick(citation)}
                              title={citation.quote}
                              type="button"
                            >
                              <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                              {citation.label}
                            </button>
                          ))
                        )}
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                        {group.id === "action_items" ? (
                          <ActionReviewControls
                            disabled={reviewDisabled}
                            item={item}
                            onUpdate={onUpdateActionItem}
                          />
                        ) : (
                          <InsightReviewControls
                            disabled={reviewDisabled}
                            item={item}
                            onUpdate={onUpdateInsight}
                          />
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>
      </div>
    </section>
  );
}

function ActionReviewControls({
  disabled,
  item,
  onUpdate,
}: {
  disabled: boolean;
  item: InsightCardItem;
  onUpdate: (actionItemId: string, payload: UpdateActionItemPayload) => void;
}) {
  const status = item.status;

  function editActionItem() {
    const description = window.prompt("Action item", item.title);
    if (description === null) {
      return;
    }
    const owner = window.prompt("Owner", item.ownerText ?? "");
    if (owner === null) {
      return;
    }
    const due = window.prompt("Due", item.dueText ?? "");
    if (due === null) {
      return;
    }
    onUpdate(item.id, {
      description: description.trim() || item.title,
      owner_text: owner.trim() || null,
      due_text: due.trim() || null,
    });
  }

  return (
    <>
      <ReviewButton disabled={disabled} onClick={editActionItem}>
        <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
        Edit
      </ReviewButton>
      {status === "proposed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() =>
            onUpdate(item.id, {
              status: "confirmed",
              confirmed_by_user_id: REVIEWER_USER_ID,
            })
          }
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          Confirm
        </ReviewButton>
      ) : null}
      {status === "confirmed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "in_progress" })}
        >
          <Play className="h-3.5 w-3.5" aria-hidden="true" />
          Start
        </ReviewButton>
      ) : null}
      {status === "confirmed" || status === "in_progress" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "done" })}
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          Done
        </ReviewButton>
      ) : null}
      {status !== "done" && status !== "canceled" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "canceled" })}
          tone="danger"
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
          Cancel
        </ReviewButton>
      ) : null}
    </>
  );
}

function InsightReviewControls({
  disabled,
  item,
  onUpdate,
}: {
  disabled: boolean;
  item: InsightCardItem;
  onUpdate: (insightId: string, payload: UpdateInsightPayload) => void;
}) {
  function editInsight() {
    const title = window.prompt("Insight title", item.title);
    if (title === null) {
      return;
    }
    const body = window.prompt("Insight body", item.body);
    if (body === null) {
      return;
    }
    onUpdate(item.id, {
      title: title.trim() || item.title,
      body: body.trim() || item.body,
    });
  }

  return (
    <>
      <ReviewButton disabled={disabled} onClick={editInsight}>
        <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
        Edit
      </ReviewButton>
      {item.status !== "confirmed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "confirmed" })}
          tone="success"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" />
          Confirm
        </ReviewButton>
      ) : null}
      {item.status !== "dismissed" ? (
        <ReviewButton
          disabled={disabled}
          onClick={() => onUpdate(item.id, { status: "dismissed" })}
          tone="danger"
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
          Dismiss
        </ReviewButton>
      ) : null}
    </>
  );
}

function ReviewButton({
  children,
  disabled,
  onClick,
  tone = "neutral",
}: {
  children: ReactNode;
  disabled: boolean;
  onClick: () => void;
  tone?: "neutral" | "success" | "danger";
}) {
  return (
    <button
      className={[
        "inline-flex h-8 items-center gap-1 rounded-md border px-2 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
        reviewButtonToneClassName(tone),
      ].join(" ")}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
}

function StatusBadge({ label, tone }: { label: string; tone: StatusTone }) {
  return (
    <span
      className={[
        "inline-flex h-6 items-center rounded-md border px-2 text-xs font-medium",
        toneClassName(tone),
      ].join(" ")}
    >
      {label}
    </span>
  );
}

function StatusNote({
  message,
  state,
}: {
  message: string;
  state: LoadState;
}) {
  const tone = state === "error" ? "danger" : state === "success" ? "success" : "info";
  return (
    <div
      className={[
        "flex gap-2 rounded-md border p-3 text-xs",
        toneClassName(tone),
      ].join(" ")}
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

function PanelState({
  label,
  tone = "neutral",
}: {
  label: string;
  tone?: StatusTone;
}) {
  return (
    <div className="flex min-h-40 items-center justify-center p-6">
      <div
        className={[
          "rounded-md border px-3 py-2 text-sm",
          toneClassName(tone),
        ].join(" ")}
      >
        {label}
      </div>
    </div>
  );
}

function toneClassName(tone: StatusTone): string {
  if (tone === "success") {
    return "border-green-200 bg-green-50 text-green-700";
  }
  if (tone === "warning") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }
  if (tone === "danger") {
    return "border-red-200 bg-red-50 text-red-700";
  }
  if (tone === "info") {
    return "border-blue-200 bg-blue-50 text-blue-700";
  }
  return "border-slate-200 bg-slate-100 text-slate-700";
}

function reviewButtonToneClassName(
  tone: "neutral" | "success" | "danger",
): string {
  if (tone === "success") {
    return "border-green-200 bg-green-50 text-green-700 hover:bg-green-100";
  }
  if (tone === "danger") {
    return "border-red-200 bg-red-50 text-red-700 hover:bg-red-100";
  }
  return "border-slate-200 bg-white text-slate-700 hover:bg-slate-100";
}

function toErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

function segmentDomId(segmentId: string): string {
  return `transcript-segment-${segmentId}`;
}

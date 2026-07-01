"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BookOpen, ListChecks, Plus, Settings2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

import { createMeetMindApi } from "./api";
import type { MeetingStatusFilter } from "./view-model";
import type {
  ActionItem,
  Citation,
  DuplicateActionGroup,
  KnowledgeDecision,
  KnowledgeSearchResult,
  MeetingSection,
  ProviderStatusList,
  ProviderTelemetryList,
  TaskSyncStatus,
} from "./types";
import { buildInsightGroups, filterMeetings } from "./view-model";
import { segmentDomId } from "./components/shared/tone-utils";

import type { ActiveView } from "@/components/layout/app-shell";
import { AppShell } from "@/components/layout/app-shell";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MeetingList } from "./components/meeting-list/meeting-list";
import { MeetingSearch } from "./components/meeting-list/meeting-search";
import { MeetingDetail } from "./components/meeting-detail/meeting-detail";
import {
  ActionItemsOverview,
  type ActionStatusFilter,
} from "./components/action-items/action-items-overview";
import { KnowledgeOverview } from "./components/knowledge/knowledge-overview";
import { OperationsOverview } from "./components/operations/operations-overview";
import type { LoadState } from "./components/shared/load-state";

import { useMeetings } from "@/hooks/use-meetings";
import { useMeetingDetail } from "@/hooks/use-meeting-detail";
import { useUpload } from "@/hooks/use-upload";
import { useQA } from "@/hooks/use-qa";
import { useJobs } from "@/hooks/use-jobs";
import { useReview } from "@/hooks/use-review";
import { useDebounce } from "@/hooks/use-debounce";
import { SEARCH_DEBOUNCE_MS } from "@/lib/constants";

export function MeetingWorkbench() {
  const api = useMemo(() => createMeetMindApi(), []);
  const [activeView, setActiveView] = useState<ActiveView>("meetings");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Meeting list state
  const { meetings, listState, listError, refreshMeetings } = useMeetings(api);

  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(
    null,
  );

  // Meeting detail state
  const { detail, detailState, detailError, loadDetail } = useMeetingDetail(
    api,
    selectedMeetingId,
  );

  // Upload state
  const {
    title,
    language,
    file,
    uploadState,
    uploadMessage,
    lastUploadJob,
    setTitle,
    setLanguage,
    setFile,
    handleCreateAndUpload,
  } = useUpload(api, setSelectedMeetingId, refreshMeetings);

  // Q&A state
  const {
    qaQuestion,
    qaResponses,
    qaState,
    qaError,
    setQaQuestion,
    handleAskQuestion,
  } = useQA(api, selectedMeetingId, detail?.citations);

  // Jobs state
  const { jobState, jobMessage, handleRunJob, handleRetryJob } = useJobs(
    api,
    selectedMeetingId,
    refreshMeetings,
    loadDetail,
  );

  // Review state
  const { reviewState, reviewMessage, handleUpdateInsight, handleUpdateActionItem } =
    useReview(api, selectedMeetingId, loadDetail);

  // Search and filter (with debounce)
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, SEARCH_DEBOUNCE_MS);
  const [statusFilter, setStatusFilter] = useState<MeetingStatusFilter>("all");
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [actionItemsState, setActionItemsState] = useState<LoadState>("idle");
  const [actionItemsError, setActionItemsError] = useState<string | null>(null);
  const [actionStatusFilter, setActionStatusFilter] =
    useState<ActionStatusFilter>("all");
  const [knowledgeQuery, setKnowledgeQuery] = useState("");
  const debouncedKnowledgeQuery = useDebounce(
    knowledgeQuery,
    SEARCH_DEBOUNCE_MS,
  );
  const [knowledgeResults, setKnowledgeResults] = useState<
    KnowledgeSearchResult[]
  >([]);
  const [knowledgeDecisions, setKnowledgeDecisions] = useState<
    KnowledgeDecision[]
  >([]);
  const [duplicateActionGroups, setDuplicateActionGroups] = useState<
    DuplicateActionGroup[]
  >([]);
  const [knowledgeState, setKnowledgeState] = useState<LoadState>("idle");
  const [knowledgeError, setKnowledgeError] = useState<string | null>(null);
  const [providerStatus, setProviderStatus] =
    useState<ProviderStatusList | null>(null);
  const [providerTelemetry, setProviderTelemetry] =
    useState<ProviderTelemetryList | null>(null);
  const [taskSyncStatus, setTaskSyncStatus] = useState<TaskSyncStatus | null>(
    null,
  );
  const [operationsState, setOperationsState] = useState<LoadState>("idle");
  const [operationsError, setOperationsError] = useState<string | null>(null);

  // Citation highlight
  const [highlightedSegmentId, setHighlightedSegmentId] = useState<string | null>(
    null,
  );
  const [pulsedSegmentId, setPulsedSegmentId] = useState<string | null>(null);
  const highlightResetRef = useRef<number | null>(null);

  const visibleMeetings = useMemo(
    () => filterMeetings(meetings, debouncedQuery, statusFilter),
    [meetings, debouncedQuery, statusFilter],
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

  const workspaceId =
    selectedMeeting?.workspace_id ??
    meetings.find((meeting) => meeting.workspace_id)?.workspace_id ??
    "workspace-local";

  function handleCitationClick(citation: Citation | { segmentId: string }) {
    const segmentId =
      "segment_id" in citation ? citation.segment_id : citation.segmentId;
    setHighlightedSegmentId(segmentId);
    setPulsedSegmentId(segmentId);
    if (highlightResetRef.current !== null) {
      window.clearTimeout(highlightResetRef.current);
    }
    highlightResetRef.current = window.setTimeout(() => {
      setPulsedSegmentId(null);
      highlightResetRef.current = null;
    }, 2800);
    // Respect prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    window.requestAnimationFrame(() => {
      const element = document.getElementById(segmentDomId(segmentId));
      element?.scrollIntoView({
        behavior: prefersReducedMotion ? "auto" : "smooth",
        block: "center",
      });
      element?.focus({ preventScroll: true });
    });
  }

  function handleSectionClick(section: MeetingSection) {
    const target = detail?.transcriptSegments.find((segment) => {
      if (section.start_ms === null || section.start_ms === undefined) {
        return false;
      }
      return segment.start_ms >= section.start_ms;
    });
    if (target) {
      handleCitationClick({ segmentId: target.id });
    }
  }

  useEffect(() => {
    return () => {
      if (highlightResetRef.current !== null) {
        window.clearTimeout(highlightResetRef.current);
      }
    };
  }, []);

  function handleViewChange(view: ActiveView) {
    setActiveView(view);
    setSidebarOpen(false); // Close mobile sidebar on navigation
  }

  function handleRefresh() {
    void refreshMeetings();
    if (activeView === "action-items") {
      void loadActionItems(actionStatusFilter);
    }
    if (activeView === "knowledge") {
      void loadKnowledge();
    }
    if (activeView === "operations") {
      void loadOperations();
    }
  }

  async function loadActionItems(filter = actionStatusFilter) {
    setActionItemsState("loading");
    setActionItemsError(null);
    try {
      const items = await api.listGlobalActionItems(
        filter === "all" ? undefined : { status: filter },
      );
      setActionItems(items);
      setActionItemsState("success");
    } catch (error) {
      setActionItemsState("error");
      setActionItemsError(
        error instanceof Error && error.message
          ? error.message
          : "无法读取行动项。",
      );
    }
  }

  function handleActionStatusFilterChange(filter: ActionStatusFilter) {
    setActionStatusFilter(filter);
    void loadActionItems(filter);
  }

  function handleOpenActionMeeting(meetingId: string) {
    setSelectedMeetingId(meetingId);
    setActiveView("meetings");
  }

  const loadKnowledge = useCallback(
    async (q?: string) => {
      const searchQuery = q ?? debouncedKnowledgeQuery;
      setKnowledgeState("loading");
      setKnowledgeError(null);
      try {
        const [results, decisions, duplicates] = await Promise.all([
          searchQuery.trim()
            ? api.searchKnowledge({
                workspaceId,
                query: searchQuery.trim(),
              })
            : Promise.resolve([]),
          api.listKnowledgeDecisions(workspaceId),
          api.listDuplicateActionCandidates(workspaceId),
        ]);
        setKnowledgeResults(results);
        setKnowledgeDecisions(decisions);
        setDuplicateActionGroups(duplicates);
        setKnowledgeState("success");
      } catch (error) {
        setKnowledgeState("error");
        setKnowledgeError(
          error instanceof Error && error.message
            ? error.message
            : "无法读取知识库。",
        );
      }
    },
    [api, debouncedKnowledgeQuery, workspaceId],
  );

  function handleOpenKnowledgeMeeting(meetingId: string) {
    setSelectedMeetingId(meetingId);
    setActiveView("meetings");
  }

  async function loadOperations() {
    setOperationsState("loading");
    setOperationsError(null);
    try {
      const [status, telemetry, taskSync] = await Promise.all([
        api.getProviderStatus(),
        api.getProviderTelemetry(),
        api.getTaskSyncStatus(),
      ]);
      setProviderStatus(status);
      setProviderTelemetry(telemetry);
      setTaskSyncStatus(taskSync);
      setOperationsState("success");
    } catch (error) {
      setOperationsState("error");
      setOperationsError(
        error instanceof Error && error.message
          ? error.message
          : "无法读取运维状态。",
      );
    }
  }

  async function handlePublishMeeting() {
    if (!selectedMeetingId) return;
    try {
      await api.publishMeeting(selectedMeetingId);
      await refreshMeetings();
      await loadDetail(selectedMeetingId);
      toast.success("会议已发布。");
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : "无法发布会议，请检查审阅状态。";
      toast.error(message);
    }
  }

  // Auto-load when switching views
  useEffect(() => {
    if (activeView === "action-items") {
      void loadActionItems(actionStatusFilter);
    }
    if (activeView === "knowledge") {
      void loadKnowledge();
    }
    if (activeView === "operations") {
      void loadOperations();
    }
  }, [activeView]);

  const sidebar = (
    <AppSidebar
      activeView={activeView}
      onViewChange={handleViewChange}
      title={title}
      language={language}
      file={file}
      uploadState={uploadState}
      uploadMessage={uploadMessage}
      lastUploadJob={lastUploadJob}
      onTitleChange={setTitle}
      onLanguageChange={setLanguage}
      onFileChange={setFile}
      onSubmitUpload={handleCreateAndUpload}
    />
  );

  return (
    <AppShell
      sidebar={sidebar}
      onRefresh={handleRefresh}
      sidebarOpen={sidebarOpen}
      onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
    >
      <div className="space-y-4">
        <div
          className="flex flex-wrap items-center gap-2"
          role="tablist"
          aria-label="视图切换"
        >
          <Button
            role="tab"
            aria-selected={activeView === "meetings"}
            variant={activeView === "meetings" ? "default" : "outline"}
            size="sm"
            type="button"
            onClick={() => handleViewChange("meetings")}
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            会议
          </Button>
          <Button
            role="tab"
            aria-selected={activeView === "action-items"}
            variant={activeView === "action-items" ? "default" : "outline"}
            size="sm"
            type="button"
            onClick={() => handleViewChange("action-items")}
          >
            <ListChecks className="h-4 w-4" aria-hidden="true" />
            行动项
          </Button>
          <Button
            role="tab"
            aria-selected={activeView === "knowledge"}
            variant={activeView === "knowledge" ? "default" : "outline"}
            size="sm"
            type="button"
            onClick={() => handleViewChange("knowledge")}
          >
            <BookOpen className="h-4 w-4" aria-hidden="true" />
            知识库
          </Button>
          <Button
            role="tab"
            aria-selected={activeView === "operations"}
            variant={activeView === "operations" ? "default" : "outline"}
            size="sm"
            type="button"
            onClick={() => handleViewChange("operations")}
          >
            <Settings2 className="h-4 w-4" aria-hidden="true" />
            运维
          </Button>
        </div>

        {/* aria-live region for status announcements */}
        <div aria-live="polite" className="sr-only">
          {listState === "loading"
            ? "会议列表加载中"
            : detailState === "loading"
              ? "会议详情加载中"
              : ""}
        </div>

        {activeView === "operations" ? (
          <OperationsOverview
            providerStatus={providerStatus}
            telemetry={providerTelemetry}
            taskSyncStatus={taskSyncStatus}
            loadState={operationsState}
            error={operationsError}
            onRefresh={() => void loadOperations()}
          />
        ) : activeView === "knowledge" ? (
          <KnowledgeOverview
            workspaceId={workspaceId}
            query={knowledgeQuery}
            searchResults={knowledgeResults}
            decisions={knowledgeDecisions}
            duplicateGroups={duplicateActionGroups}
            loadState={knowledgeState}
            error={knowledgeError}
            onQueryChange={setKnowledgeQuery}
            onSearch={() => void loadKnowledge(knowledgeQuery)}
            onOpenMeeting={handleOpenKnowledgeMeeting}
          />
        ) : activeView === "action-items" ? (
          <ActionItemsOverview
            actionItems={actionItems}
            meetings={meetings}
            statusFilter={actionStatusFilter}
            loadState={actionItemsState}
            error={actionItemsError}
            onStatusFilterChange={handleActionStatusFilterChange}
            onOpenMeeting={handleOpenActionMeeting}
            onRefresh={() => void loadActionItems(actionStatusFilter)}
          />
        ) : (
          <div className="grid min-h-[calc(100vh-156px)] gap-4 lg:grid-cols-[360px_minmax(0,1fr)] xl:gap-5">
            <section className="min-w-0 overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
              <div className="border-b border-border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h1 className="text-xl font-semibold tracking-normal text-text-primary">
                      会议
                    </h1>
                    <p className="mt-1 text-sm text-text-muted">
                      {meetings.length} 场会议
                    </p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => {
                      document
                        .querySelector<HTMLInputElement>("#meeting-title")
                        ?.focus();
                    }}
                  >
                    <Plus className="h-4 w-4" aria-hidden="true" />
                    新建
                  </Button>
                </div>

                <div className="mt-4">
                  <MeetingSearch
                    query={query}
                    statusFilter={statusFilter}
                    onQueryChange={setQuery}
                    onStatusFilterChange={setStatusFilter}
                  />
                </div>
              </div>

              <MeetingList
                meetings={visibleMeetings}
                selectedMeetingId={selectedMeetingId}
                listState={listState}
                listError={listError}
                onSelectMeeting={setSelectedMeetingId}
              />
            </section>

            <MeetingDetail
              selectedMeeting={selectedMeeting}
              detail={detail}
              detailState={detailState}
              detailError={detailError}
              highlightedSegmentId={highlightedSegmentId}
              pulsedSegmentId={pulsedSegmentId}
              insightGroups={insightGroups}
              jobState={jobState}
              jobMessage={jobMessage}
              qaQuestion={qaQuestion}
              qaResponses={qaResponses}
              qaState={qaState}
              qaError={qaError}
              reviewState={reviewState}
              reviewMessage={reviewMessage}
              onCitationClick={handleCitationClick}
              onSectionClick={handleSectionClick}
              onRunJob={handleRunJob}
              onRetryJob={handleRetryJob}
              onQaQuestionChange={setQaQuestion}
              onSubmitQuestion={handleAskQuestion}
              onUpdateActionItem={handleUpdateActionItem}
              onUpdateInsight={handleUpdateInsight}
              onPublishMeeting={handlePublishMeeting}
            />
          </div>
        )}
      </div>
    </AppShell>
  );
}

"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

import { createMeetMindApi } from "./api";
import type { MeetingStatusFilter } from "./view-model";
import type { Citation } from "./types";
import { buildInsightGroups, filterMeetings } from "./view-model";
import { segmentDomId } from "./components/shared/tone-utils";

import { AppShell } from "@/components/layout/app-shell";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MeetingList } from "./components/meeting-list/meeting-list";
import { MeetingSearch } from "./components/meeting-list/meeting-search";
import { MeetingDetail } from "./components/meeting-detail/meeting-detail";

import { useMeetings } from "@/hooks/use-meetings";
import { useMeetingDetail } from "@/hooks/use-meeting-detail";
import { useUpload } from "@/hooks/use-upload";
import { useQA } from "@/hooks/use-qa";
import { useJobs } from "@/hooks/use-jobs";
import { useReview } from "@/hooks/use-review";

export function MeetingWorkbench() {
  const api = useMemo(() => createMeetMindApi(), []);

  // Meeting list state
  const {
    meetings,
    listState,
    listError,
    refreshMeetings,
  } = useMeetings(api);

  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);

  // Meeting detail state
  const {
    detail,
    detailState,
    detailError,
    loadDetail,
  } = useMeetingDetail(api, selectedMeetingId);

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
  } = useQA(api, selectedMeetingId);

  // Jobs state
  const {
    jobState,
    jobMessage,
    handleRunJob,
    handleRetryJob,
  } = useJobs(api, selectedMeetingId, refreshMeetings, loadDetail);

  // Review state
  const {
    reviewState,
    reviewMessage,
    handleUpdateInsight,
    handleUpdateActionItem,
  } = useReview(api, selectedMeetingId, loadDetail);

  // Search and filter
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<MeetingStatusFilter>("all");

  // Citation highlight
  const [highlightedSegmentId, setHighlightedSegmentId] = useState<string | null>(null);
  const [pulsedSegmentId, setPulsedSegmentId] = useState<string | null>(null);
  const highlightResetRef = useRef<number | null>(null);

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
    window.requestAnimationFrame(() => {
      const element = document.getElementById(segmentDomId(segmentId));
      element?.scrollIntoView({ behavior: "smooth", block: "center" });
      element?.focus({ preventScroll: true });
    });
  }

  useEffect(() => {
    return () => {
      if (highlightResetRef.current !== null) {
        window.clearTimeout(highlightResetRef.current);
      }
    };
  }, []);

  function handleRefresh() {
    void refreshMeetings();
  }

  const sidebar = (
    <AppSidebar
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
    <AppShell sidebar={sidebar} onRefresh={handleRefresh}>
      <div className="grid min-h-[calc(100vh-112px)] gap-4 lg:grid-cols-[360px_minmax(0,1fr)] xl:gap-5">
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
          onRunJob={handleRunJob}
          onRetryJob={handleRetryJob}
          onQaQuestionChange={setQaQuestion}
          onSubmitQuestion={handleAskQuestion}
          onUpdateActionItem={handleUpdateActionItem}
          onUpdateInsight={handleUpdateInsight}
        />
      </div>
    </AppShell>
  );
}

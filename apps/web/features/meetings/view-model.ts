import type {
  ActionItem,
  Citation,
  InsightItem,
  MeetingStatus,
  TranscriptSegment,
} from "./types";

export type MeetingStatusFilter = "all" | "failed" | MeetingStatus;

export type StatusTone = "neutral" | "info" | "success" | "warning" | "danger";

export interface StatusMeta {
  label: string;
  tone: StatusTone;
}

export interface CitationChipView {
  id: string;
  segmentId: string;
  label: string;
  quote: string;
  confidence?: number | null;
}

export interface InsightItemView {
  id: string;
  title: string;
  body: string;
  status: string;
  confidence?: number | null;
  ownerText?: string | null;
  dueText?: string | null;
  citations: CitationChipView[];
}

export interface InsightGroupView {
  id:
    | "action_items"
    | "decisions"
    | "risks"
    | "summary"
    | "open_questions";
  title: string;
  emptyLabel: string;
  items: InsightItemView[];
}

const insightGroupOrder: Array<Omit<InsightGroupView, "items">> = [
  {
    id: "action_items",
    title: "行动项",
    emptyLabel: "暂无行动项。",
  },
  { id: "decisions", title: "决策", emptyLabel: "暂无决策。" },
  { id: "risks", title: "风险", emptyLabel: "暂无风险。" },
  { id: "summary", title: "摘要", emptyLabel: "暂无摘要。" },
  {
    id: "open_questions",
    title: "开放问题",
    emptyLabel: "暂无开放问题。",
  },
];

const statusMeta: Record<MeetingStatus, StatusMeta> = {
  uploaded: { label: "已上传", tone: "neutral" },
  media_processing: { label: "媒体处理中", tone: "info" },
  transcribing: { label: "转写中", tone: "info" },
  segmenting: { label: "分段中", tone: "info" },
  structuring: { label: "结构化中", tone: "info" },
  citing: { label: "证据匹配中", tone: "info" },
  embedding: { label: "索引中", tone: "info" },
  ready_for_review: { label: "待审阅", tone: "warning" },
  published: { label: "已发布", tone: "success" },
  failed_media_processing: { label: "处理失败", tone: "danger" },
  failed_transcription: { label: "处理失败", tone: "danger" },
  failed_structuring: { label: "处理失败", tone: "danger" },
  failed_embedding: { label: "处理失败", tone: "danger" },
};

export function filterMeetings<T extends { title: string; status: string }>(
  meetings: readonly T[],
  query: string,
  statusFilter: MeetingStatusFilter,
): T[] {
  const normalizedQuery = query.trim().toLowerCase();
  return meetings.filter((meeting) => {
    const matchesQuery =
      normalizedQuery.length === 0 ||
      meeting.title.toLowerCase().includes(normalizedQuery);
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "failed"
        ? meeting.status.startsWith("failed_")
        : meeting.status === statusFilter);
    return matchesQuery && matchesStatus;
  });
}

export function getMeetingStatusMeta(status: string): StatusMeta {
  if (isMeetingStatus(status)) {
    return statusMeta[status];
  }
  return { label: status.replaceAll("_", " "), tone: "neutral" };
}

export function formatTimestamp(milliseconds: number): string {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const seconds = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const hours = Math.floor(totalMinutes / 60);
  if (hours > 0) {
    return `${hours}:${pad2(minutes)}:${pad2(seconds)}`;
  }
  return `${pad2(minutes)}:${pad2(seconds)}`;
}

export function formatDuration(milliseconds?: number | null): string {
  if (milliseconds === undefined || milliseconds === null) {
    return "未设置";
  }
  return formatTimestamp(milliseconds);
}

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return "未设置";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function buildInsightGroups(input: {
  actionItems: readonly ActionItem[];
  insights: readonly InsightItem[];
  citations: readonly Citation[];
  transcriptSegments: readonly TranscriptSegment[];
}): InsightGroupView[] {
  const segmentIds = new Set(input.transcriptSegments.map((segment) => segment.id));
  const citationsByTarget = groupCitationsByTarget(input.citations);
  const itemsByGroup = new Map<InsightGroupView["id"], InsightItemView[]>();

  for (const actionItem of input.actionItems) {
    pushGroupItem(itemsByGroup, "action_items", {
      id: actionItem.id,
      title: actionItem.description,
      body: actionItem.description,
      status: actionItem.status,
      confidence: actionItem.confidence,
      ownerText: actionItem.owner_text,
      dueText: actionItem.due_text ?? actionItem.due_date,
      citations: toCitationChips(
        citationsByTarget.get(targetKey("action_item", actionItem.id)) ?? [],
        segmentIds,
      ),
    });
  }

  for (const insight of input.insights) {
    pushGroupItem(itemsByGroup, groupIdForInsight(insight), {
      id: insight.id,
      title: insight.title,
      body: insight.body,
      status: insight.status,
      confidence: insight.confidence,
      citations: toCitationChips(
        citationsByTarget.get(targetKey("insight_item", insight.id)) ?? [],
        segmentIds,
      ),
    });
  }

  return insightGroupOrder.map((group) => ({
    ...group,
    items: itemsByGroup.get(group.id) ?? [],
  }));
}

export function confidenceLabel(confidence?: number | null): string {
  if (confidence === undefined || confidence === null) {
    return "需核对";
  }
  if (confidence >= 0.85) {
    return "高置信度";
  }
  if (confidence >= 0.65) {
    return "需核对";
  }
  return "低置信度";
}

function groupCitationsByTarget(
  citations: readonly Citation[],
): Map<string, Citation[]> {
  const grouped = new Map<string, Citation[]>();
  for (const citation of citations) {
    const key = targetKey(citation.target_type, citation.target_id);
    grouped.set(key, [...(grouped.get(key) ?? []), citation]);
  }
  return grouped;
}

function toCitationChips(
  citations: readonly Citation[],
  segmentIds: Set<string>,
): CitationChipView[] {
  return citations.map((citation) => ({
    id: citation.id,
    segmentId: citation.segment_id,
    label: formatTimestamp(citation.start_ms),
    quote: segmentIds.has(citation.segment_id)
      ? citation.quote
      : "引用的转写片段已缺失。",
    confidence: citation.confidence,
  }));
}

function groupIdForInsight(insight: InsightItem): InsightGroupView["id"] {
  if (insight.type === "decision") {
    return "decisions";
  }
  if (insight.type === "risk") {
    return "risks";
  }
  if (insight.type === "open_question") {
    return "open_questions";
  }
  return "summary";
}

function pushGroupItem(
  itemsByGroup: Map<InsightGroupView["id"], InsightItemView[]>,
  groupId: InsightGroupView["id"],
  item: InsightItemView,
): void {
  itemsByGroup.set(groupId, [...(itemsByGroup.get(groupId) ?? []), item]);
}

function targetKey(targetType: string, targetId: string): string {
  return `${targetType}:${targetId}`;
}

function isMeetingStatus(status: string): status is MeetingStatus {
  return Object.hasOwn(statusMeta, status);
}

function pad2(value: number): string {
  return value.toString().padStart(2, "0");
}

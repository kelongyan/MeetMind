import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import type { MeetingStatusFilter } from "../../view-model";

const statusFilters: Array<{ value: MeetingStatusFilter; label: string }> = [
  { value: "all", label: "全部状态" },
  { value: "uploaded", label: "已上传" },
  { value: "transcribing", label: "转写中" },
  { value: "structuring", label: "结构化中" },
  { value: "ready_for_review", label: "待审阅" },
  { value: "published", label: "已发布" },
  { value: "failed", label: "失败" },
];

export function MeetingSearch({
  query,
  statusFilter,
  onQueryChange,
  onStatusFilterChange,
}: {
  query: string;
  statusFilter: MeetingStatusFilter;
  onQueryChange: (query: string) => void;
  onStatusFilterChange: (statusFilter: MeetingStatusFilter) => void;
}) {
  const selectedStatusLabel =
    statusFilters.find((filter) => filter.value === statusFilter)?.label ?? "全部状态";

  return (
    <div className="grid gap-2 sm:grid-cols-[1fr_136px]">
      <div className="relative">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <Input
          className="pl-9"
          placeholder="搜索会议"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
      </div>
      <Select
        value={statusFilter}
        onValueChange={(value) => onStatusFilterChange(value as MeetingStatusFilter)}
      >
        <SelectTrigger>
          <SelectValue>{selectedStatusLabel}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          {statusFilters.map((filter) => (
            <SelectItem key={filter.value} value={filter.value}>
              {filter.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

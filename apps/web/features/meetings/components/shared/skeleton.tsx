import { cn } from "@/lib/utils";

/**
 * Animated loading placeholder that mimics content layout.
 * Uses `prefers-reduced-motion` via CSS to disable animation for
 * users with vestibular disorders.
 */
export function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-muted motion-reduce:animate-none",
        className,
      )}
      aria-hidden="true"
      {...props}
    />
  );
}

/** Skeleton for a meeting list item. */
export function MeetingCardSkeleton() {
  return (
    <div className="flex flex-col gap-2 p-4">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-1/2" />
      <Skeleton className="h-3 w-1/3" />
    </div>
  );
}

/** Skeleton for a list of meetings. */
export function MeetingListSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="divide-y divide-border" role="status" aria-label="加载中">
      {Array.from({ length: count }, (_, i) => (
        <MeetingCardSkeleton key={i} />
      ))}
    </div>
  );
}

/** Skeleton for the meeting detail panel. */
export function DetailSkeleton() {
  return (
    <div className="space-y-4 p-4" role="status" aria-label="加载中">
      <Skeleton className="h-6 w-2/3" />
      <Skeleton className="h-4 w-1/2" />
      <div className="space-y-2 pt-4">
        {Array.from({ length: 5 }, (_, i) => (
          <div key={i} className="flex gap-4">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 flex-1" />
          </div>
        ))}
      </div>
    </div>
  );
}

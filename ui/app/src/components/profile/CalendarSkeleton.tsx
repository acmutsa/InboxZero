import { Skeleton } from '@/components/ui/skeleton';

export default function CalendarSkeleton() {
  return (
    <div role="status" aria-label="Loading calendar" aria-busy="true">
      <span className="sr-only">Loading calendar…</span>
      <div aria-hidden="true">
        <div className="calendar-skeleton-header">
          <div>
            <Skeleton className="calendar-skeleton-title" />
            <Skeleton className="calendar-skeleton-description" />
          </div>
          <Skeleton className="calendar-skeleton-actions" />
        </div>
        <div className="calendar-layout">
          <div className="calendar-skeleton-sidebar">
            <Skeleton className="calendar-skeleton-month" />
            <Skeleton className="calendar-skeleton-list" />
            <Skeleton className="calendar-skeleton-list" />
          </div>
          <Skeleton className="calendar-skeleton-grid" />
        </div>
      </div>
    </div>
  );
}
